import csv
import io
import json
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .crop_models import CsvFile, CropImage, CropMetadata
from .crop_serializers import CsvFileSerializer, CropImageSerializer, CropMetadataSerializer

class CsvFileViewSet(viewsets.ModelViewSet):
    queryset = CsvFile.objects.all().order_by('-uploaded_at')
    serializer_class = CsvFileSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def process_csv(self, request, pk=None):
        csv_file = self.get_object()
        
        try:
            # Read CSV file
            csv_file_path = csv_file.file.path
            with open(csv_file_path, 'r') as file:
                csv_reader = csv.DictReader(file)
                rows = list(csv_reader)
            
            # Process each row and create/update CropImage records
            created_count = 0
            updated_count = 0
            with transaction.atomic():
                for row in rows:
                    # Extract required fields
                    sample_id = row.get('sample_id')
                    if not sample_id:
                        continue  # Skip rows without sample_id
                    
                    # Try to find existing image or create new one
                    crop_image, created = CropImage.objects.update_or_create(
                        sample_id=sample_id,
                        csv_file=csv_file,
                        defaults={
                            'user': request.user,
                            'description': row.get('description', '')
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                    
                    # Process additional metadata
                    for key, value in row.items():
                        if key not in ['sample_id', 'description'] and value:
                            CropMetadata.objects.update_or_create(
                                crop_image=crop_image,
                                label=key,
                                defaults={'value': value}
                            )
            
            return Response({
                'message': f'CSV processing complete',
                'created': created_count,
                'updated': updated_count,
                'total_processed': len(rows)
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CropImageViewSet(viewsets.ModelViewSet):
    queryset = CropImage.objects.all().order_by('-uploaded_at')
    serializer_class = CropImageSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by sample_id
        sample_id = self.request.query_params.get('sample_id')
        if sample_id:
            queryset = queryset.filter(sample_id__icontains=sample_id)
        
        # Filter by csv_file
        csv_file = self.request.query_params.get('csv_file')
        if csv_file:
            queryset = queryset.filter(csv_file=csv_file)
            
        # Filter by metadata label/value
        metadata_label = self.request.query_params.get('metadata_label')
        metadata_value = self.request.query_params.get('metadata_value')
        if metadata_label and metadata_value:
            queryset = queryset.filter(metadata__label=metadata_label, metadata__value__icontains=metadata_value)
        elif metadata_label:
            queryset = queryset.filter(metadata__label=metadata_label)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def upload_images(self, request):
        try:
            images = request.FILES.getlist('images')
            csv_file_id = request.data.get('csv_file')
            sample_id_prefix = request.data.get('sample_id_prefix', 'IMG')
            
            if not images:
                return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not csv_file_id:
                return Response({'error': 'CSV file ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                csv_file = CsvFile.objects.get(id=csv_file_id)
            except CsvFile.DoesNotExist:
                return Response({'error': 'CSV file not found'}, status=status.HTTP_404_NOT_FOUND)
            
            created_images = []
            for index, image_file in enumerate(images):
                # Create a CropImage record with sequential sample_id
                crop_image = CropImage.objects.create(
                    image=image_file,
                    sample_id=f'{sample_id_prefix}_{index + 1}',
                    description=f'Uploaded image {index + 1}',
                    csv_file=csv_file,
                    user=request.user
                )
                created_images.append(CropImageSerializer(crop_image, context={'request': request}).data)
            
            return Response({
                'message': f'Successfully uploaded {len(images)} images',
                'images': created_images
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_metadata(self, request, pk=None):
        crop_image = self.get_object()
        metadata_items = request.data.get('metadata', [])
        
        if not isinstance(metadata_items, list):
            return Response({'error': 'Metadata must be a list of label/value pairs'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        created_metadata = []
        try:
            with transaction.atomic():
                for item in metadata_items:
                    label = item.get('label')
                    value = item.get('value')
                    
                    if not label or not value:
                        continue
                    
                    metadata, created = CropMetadata.objects.update_or_create(
                        crop_image=crop_image,
                        label=label,
                        defaults={'value': value}
                    )
                    
                    created_metadata.append(CropMetadataSerializer(metadata).data)
            
            return Response({
                'message': f'Added {len(created_metadata)} metadata items',
                'metadata': created_metadata
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def metadata_labels(self, request):
        distinct_labels = CropMetadata.objects.values_list('label', flat=True).distinct()
        return Response(list(distinct_labels))
    
    @action(detail=False, methods=['get'])
    def metadata_values(self, request):
        label = request.query_params.get('label')
        if not label:
            return Response({'error': 'Label parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        distinct_values = CropMetadata.objects.filter(label=label).values_list('value', flat=True).distinct()
        return Response(list(distinct_values))

class CropMetadataViewSet(viewsets.ModelViewSet):
    queryset = CropMetadata.objects.all()
    serializer_class = CropMetadataSerializer
    permission_classes = [permissions.IsAuthenticated]
