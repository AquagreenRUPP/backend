from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ExcelFile, ProcessedData
from .serializers import ExcelFileSerializer, ProcessedDataSerializer
from .excel_utils import process_excel_file
from .kafka_utils import KafkaProducer
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
        return ExcelFile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Associate the uploaded file with the current user"""
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Handle file upload and process it."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the uploaded file
            excel_file = serializer.save()
            
            # Process the Excel file
            try:
                # Process the file and get the processed data
                processed_data = process_excel_file(excel_file)
                
                # Publish data to Kafka
                kafka_producer = KafkaProducer()
                for data in processed_data:
                    kafka_producer.publish_data(data.data_json)
                
                # Mark the file as processed
                excel_file.processed = True
                excel_file.save()
                
                return Response({
                    'file': serializer.data,
                    'message': 'File uploaded and processed successfully'
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'file': serializer.data,
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
            kafka_producer = KafkaProducer()
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
        if not file_id:
            return Response(
                {"error": "file_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the file and verify it belongs to the user
        excel_file = get_object_or_404(ExcelFile, id=file_id, user=request.user)
        
        # Get processed data for the file
        data = ProcessedData.objects.filter(excel_file=excel_file)
        serializer = self.get_serializer(data, many=True)
        
        return Response(serializer.data)
