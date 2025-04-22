from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ExcelFile, ProcessedData
from .serializers import ExcelFileSerializer, ProcessedDataSerializer
from .excel_utils import process_excel_file
from .kafka_utils import kafka_producer
import logging

logger = logging.getLogger(__name__)

class ExcelFileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Excel files
    """
    queryset = ExcelFile.objects.all()
    serializer_class = ExcelFileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter files to only show those belonging to the current user"""
        user = self.request.user
        logger.info(f"Fetching files for user: {user.username} (ID: {user.id})")
        
        # Get all files for this user
        queryset = ExcelFile.objects.filter(user=user)
        logger.info(f"Found {queryset.count()} files for user {user.username}")
        
        return queryset
        
    def list(self, request, *args, **kwargs):
        """Override list method to add debugging"""
        queryset = self.filter_queryset(self.get_queryset())
        
        logger.info(f"Listing files for user {request.user.username}, found {queryset.count()} files")
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """Associate the uploaded file with the current user"""
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Handle file upload and process it."""
        logger.info(f"File upload request from user: {request.user.username}")
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Save the uploaded file and associate with the current user
            excel_file = serializer.save(user=request.user)
            logger.info(f"File saved: {excel_file.title} (ID: {excel_file.id}) for user {request.user.username}")
            
            # Process the Excel file
            try:
                # Process the file and get the processed data
                processed_data = process_excel_file(excel_file)
                logger.info(f"File processed: {excel_file.title}, extracted {len(processed_data)} data points")
                
                # Publish data to Kafka
                for data in processed_data:
                    kafka_producer.publish_data(data.data_json)
                
                # Mark the file as processed
                excel_file.processed = True
                excel_file.save()
                
                # Re-serialize to include the user field
                updated_serializer = self.get_serializer(excel_file)
                
                return Response({
                    'success': True,
                    'file': updated_serializer.data,
                    'message': 'File uploaded and processed successfully'
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                return Response({
                    'success': False,
                    'file': serializer.data,
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.warning(f"Invalid file upload data: {serializer.errors}")
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        Process the Excel file and extract data
        """
        excel_file = self.get_object()
        
        if excel_file.processed:
            return Response(
                {"message": "File has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Process the file and get the processed data
            processed_data = process_excel_file(excel_file)
            
            # Publish data to Kafka
            for data in processed_data:
                kafka_producer.publish_data(data.data_json)
            
            # Mark the file as processed
            excel_file.processed = True
            excel_file.save()
            
            return Response(
                {"message": "File processed successfully."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProcessedDataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving processed data
    """
    queryset = ProcessedData.objects.all()
    serializer_class = ProcessedDataSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter data to only show those belonging to the current user's files"""
        return ProcessedData.objects.filter(excel_file__user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_file(self, request):
        """
        Get processed data for a specific file
        """
        file_id = request.query_params.get('file_id')
        
        # Handle missing or invalid file_id
        if not file_id or file_id == 'undefined' or file_id == 'null':
            logger.warning(f"Invalid file_id provided: {file_id}")
            return Response(
                {"success": False, "error": "Valid file_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the file and verify it belongs to the user
            excel_file = get_object_or_404(ExcelFile, id=file_id, user=request.user)
            
            # Get processed data for the file
            data = ProcessedData.objects.filter(excel_file=excel_file)
            serializer = self.get_serializer(data, many=True)
            
            return Response({
                "success": True,
                "data": serializer.data
            })
        except Exception as e:
            logger.error(f"Error retrieving processed data: {str(e)}")
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
