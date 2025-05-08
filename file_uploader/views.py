from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ExcelFile, CropImage, ImageMetadata, CsvFile
from .serializers import ExcelFileSerializer, CropImageSerializer, ImageMetadataSerializer, CsvFileSerializer
from .excel_utils import process_excel_file
import pandas as pd
import json
import os
from django.conf import settings
from django.contrib.auth.models import User

class ExcelFileViewSet(viewsets.ModelViewSet):
    queryset = ExcelFile.objects.all().order_by('-uploaded_at')
    serializer_class = ExcelFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    def get_queryset(self):
        # Filter to only show files uploaded by the current user
        return ExcelFile.objects.filter(uploaded_by=self.request.user).order_by('-uploaded_at')
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        excel_file = self.get_object()
        
        try:
            # Process the file
            processed_data = process_excel_file(excel_file)
            
            return Response({
                'message': 'File processed successfully',
                'preview': processed_data[:5] if len(processed_data) > 5 else processed_data
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        excel_file = self.get_object()
        
        try:
            file_path = excel_file.file.path
            # Read the Excel file
            df = pd.read_excel(file_path)
            
            # Convert to JSON for preview (first 5 rows)
            preview_data = df.head(5).to_dict('records')
            
            return Response({
                'preview': preview_data
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class CropImageViewSet(viewsets.ModelViewSet):
    queryset = CropImage.objects.all().order_by('-uploaded_at')
    serializer_class = CropImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        instance = serializer.save(uploaded_by=self.request.user)
        
        # Process metadata if provided
        metadata = self.request.data.get('metadata', [])
        if isinstance(metadata, list):
            for meta_item in metadata:
                if 'label' in meta_item and 'value' in meta_item:
                    ImageMetadata.objects.create(
                        image=instance,
                        label=meta_item['label'],
                        value=meta_item['value']
                    )
    
    def get_queryset(self):
        # Filter to only show images uploaded by the current user
        return CropImage.objects.filter(uploaded_by=self.request.user).order_by('-uploaded_at')
    
    @action(detail=False, methods=['post'])
    def upload_images(self, request):
        """Upload multiple crop images in one request"""
        csv_file_id = request.data.get('csv_file')
        sample_id_prefix = request.data.get('sample_id_prefix', '')
        
        # Get the CSV file if provided
        csv_file = None
        if csv_file_id:
            try:
                csv_file = CsvFile.objects.get(id=csv_file_id, uploaded_by=request.user)
            except CsvFile.DoesNotExist:
                return Response({
                    'error': 'CSV file not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if images are provided
        if 'images' not in request.FILES:
            return Response({
                'error': 'No images provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_images = []
        for image_file in request.FILES.getlist('images'):
            # Create a sample ID using prefix if provided
            sample_id = f"{sample_id_prefix}_{len(uploaded_images) + 1}" if sample_id_prefix else None
            
            serializer = CropImageSerializer(data={
                'sample_id': sample_id,
                'csv_file': csv_file.id if csv_file else None
            })
            
            if serializer.is_valid():
                image_instance = serializer.save(uploaded_by=request.user, image=image_file)
                uploaded_images.append(CropImageSerializer(image_instance).data)
        
        return Response({
            'message': f'Successfully uploaded {len(uploaded_images)} images',
            'images': uploaded_images
        })
    
    @action(detail=True, methods=['post'])
    def add_metadata(self, request, pk=None):
        crop_image = self.get_object()
        metadata = request.data.get('metadata', [])
        
        created_items = []
        for meta_item in metadata:
            if 'label' in meta_item and 'value' in meta_item:
                meta = ImageMetadata.objects.create(
                    image=crop_image,
                    label=meta_item['label'],
                    value=meta_item['value']
                )
                created_items.append(ImageMetadataSerializer(meta).data)
        
        return Response({
            'message': f'Added {len(created_items)} metadata items',
            'metadata': created_items
        })
        
    @action(detail=False, methods=['get'])
    def metadata_labels(self, request):
        """Get all unique metadata labels for crop images"""
        # Get unique labels from ImageMetadata for the current user's images
        labels = ImageMetadata.objects.filter(
            image__uploaded_by=request.user
        ).values_list('label', flat=True).distinct()
        
        return Response({
            'labels': list(labels)
        })

class CsvFileViewSet(viewsets.ModelViewSet):
    queryset = CsvFile.objects.all().order_by('-uploaded_at')
    serializer_class = CsvFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    def get_queryset(self):
        # Filter to only show files uploaded by the current user
        return CsvFile.objects.filter(uploaded_by=self.request.user).order_by('-uploaded_at')
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        csv_file = self.get_object()
        
        try:
            file_path = csv_file.file.path
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Convert to JSON for preview (first 5 rows)
            preview_data = df.head(5).to_dict('records')
            
            return Response({
                'preview': preview_data
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        csv_file = self.get_object()
        
        try:
            file_path = csv_file.file.path
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Mark as processed
            csv_file.processed = True
            csv_file.save()
            
            return Response({
                'message': 'CSV file processed successfully'
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
