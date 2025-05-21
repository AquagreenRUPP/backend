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
from rest_framework.views import APIView
import numpy as np

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

class ExcelFileDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            excel_file = get_object_or_404(ExcelFile, id=pk, uploaded_by=request.user)
            
            # Calculate the actual file size for accurate reporting
            file_size = 0
            if excel_file.file and hasattr(excel_file.file, 'path') and os.path.exists(excel_file.file.path):
                file_size = os.path.getsize(excel_file.file.path)
            
            # Create the serializer with the file size in context
            serializer = ExcelFileSerializer(
                excel_file, 
                context={
                    'request': request,
                    'file_size': file_size
                }
            )
            
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ProcessFileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            excel_file = get_object_or_404(ExcelFile, id=pk, uploaded_by=request.user)
            
            # Process the file here (e.g., run calculations, data transformation, etc.)
            # For now, just mark as processed
            excel_file.processed = True
            excel_file.save()
            
            # Update the file size information for accurate reporting
            file_size = 0
            if excel_file.file and os.path.exists(excel_file.file.path):
                file_size = os.path.getsize(excel_file.file.path)
            
            return Response({
                'message': 'File processed successfully',
                'file_id': excel_file.id,
                'file_size_in_bytes': file_size
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
            
            # Process each row to link with crop images by sample_id
            created = 0
            updated = 0

            # Ensure sample_id column exists
            if 'sample_id' in df.columns:
                # Find crop images with matching sample_ids
                for _, row in df.iterrows():
                    sample_id = row['sample_id']
                    if not sample_id:
                        continue
                    
                    # Look for matching crop images
                    matching_images = CropImage.objects.filter(
                        sample_id=sample_id,
                        uploaded_by=request.user
                    )
                    
                    # Link found images to this CSV file
                    for image in matching_images:
                        if image.csv_file != csv_file:
                            image.csv_file = csv_file
                            image.save()
                            updated += 1
                    
                    # Create metadata for the matching images
                    for image in matching_images:
                        # Add each column as metadata
                        for column in df.columns:
                            if column != 'sample_id' and not pd.isna(row[column]):
                                # Check if this metadata already exists
                                existing_meta = ImageMetadata.objects.filter(
                                    image=image,
                                    label=column
                                ).first()
                                
                                if existing_meta:
                                    # Update existing metadata
                                    existing_meta.value = str(row[column])
                                    existing_meta.save()
                                else:
                                    # Create new metadata
                                    ImageMetadata.objects.create(
                                        image=image,
                                        label=column,
                                        value=str(row[column])
                                    )
                                    created += 1
            
            # Mark as processed
            csv_file.processed = True
            csv_file.save()
            
            return Response({
                'message': 'CSV file processed successfully',
                'created': created,
                'updated': updated
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ProcessedDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        file_id = request.query_params.get('file_id')
        if not file_id:
            return Response({"error": "Missing file_id parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get the file, ensuring it belongs to the current user
            excel_file = get_object_or_404(ExcelFile, id=file_id, uploaded_by=request.user)
            
            if not excel_file.processed:
                return Response([])
            
            # Check if we have cached processed data in the session to avoid reprocessing
            cache_key = f'processed_data_{file_id}'
            processed_data = request.session.get(cache_key)
            
            if processed_data:
                # Use cached data if available
                return Response(processed_data)
            
            file_path = excel_file.file.path
            try:
                # Check if file exists and is not empty
                import os
                if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                    return Response({"error": "File is empty or invalid"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Read the Excel file with more efficient pandas settings
                # Use chunksize for larger files to prevent memory issues
                file_size = os.path.getsize(file_path)
                if file_size > 10 * 1024 * 1024:  # If file is larger than 10MB
                    # Process in chunks for large files
                    chunks = pd.read_excel(file_path, chunksize=1000)
                    all_data = []
                    for chunk in chunks:
                        all_data.append(chunk)
                    df = pd.concat(all_data)
                else:
                    # For smaller files, read normally
                    df = pd.read_excel(file_path, engine='openpyxl')
                
                # Check if dataframe is empty or has only 1 row/column
                if df.empty:
                    return Response({"error": "File contains no data"}, status=status.HTTP_400_BAD_REQUEST)
                elif len(df) <= 1:
                    return Response({"error": "File contains only one row of data, which is insufficient for analysis"}, status=status.HTTP_400_BAD_REQUEST)
                elif len(df.columns) <= 1:
                    return Response({"error": "File contains only one column of data, which is insufficient for analysis"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Only process first 1000 rows for performance if data is very large
                if len(df) > 1000:
                    df = df.head(1000)
                    
                # Handle NaN values correctly - replace with None for JSON serialization
                processed_data = df.replace({np.nan: None}).to_dict('records')
                
                # Additional safety check for any remaining problematic values
                for record in processed_data:
                    for key, value in record.items():
                        # Check for NaN, infinity values and replace with None
                        if isinstance(value, float) and (pd.isna(value) or np.isinf(value)):
                            record[key] = None
                        # Convert any problematic types to strings
                        elif not isinstance(value, (str, int, float, bool, type(None))):
                            record[key] = str(value)
                
                # Cache the processed data in the session to avoid reprocessing
                request.session[cache_key] = processed_data
                
                return Response(processed_data)
            except pd.errors.EmptyDataError:
                return Response({"error": "The file is empty or contains no data"}, status=status.HTTP_400_BAD_REQUEST)
            except pd.errors.ParserError:
                return Response({"error": "Error parsing the Excel file. It may be corrupted or in an unsupported format."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": f"Error processing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
                
        except ExcelFile.DoesNotExist:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
