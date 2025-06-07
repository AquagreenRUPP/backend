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
        # Save first to get the file path
        instance = serializer.save(uploaded_by=self.request.user)
        # Process the file immediately after upload
        self._extract_columns(instance)
    
    def get_queryset(self):
        # Filter to only show files uploaded by the current user
        return CsvFile.objects.filter(uploaded_by=self.request.user).order_by('-uploaded_at')
    
    def _extract_columns(self, csv_file):
        """Extract column names from CSV and store them in the model"""
        import hashlib
        
        try:
            file_path = csv_file.file.path
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Generate hash of file content for change detection
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Store column information
            csv_file.columns = list(df.columns)
            csv_file.data_hash = file_hash
            csv_file.save()
            
            return df
        except Exception as e:
            # Log the error but don't fail
            print(f"Error extracting columns: {str(e)}")
            return None
            
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        csv_file = self.get_object()
        
        try:
            file_path = csv_file.file.path
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Convert to JSON for preview (first 5 rows)
            preview_data = df.head(5).to_dict('records')
            
            # Include column information
            column_types = {}
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    column_types[col] = 'numeric'
                elif pd.api.types.is_datetime64_dtype(df[col]):
                    column_types[col] = 'datetime'
                else:
                    column_types[col] = 'text'
            
            return Response({
                'preview': preview_data,
                'columns': csv_file.columns,
                'column_types': column_types,
                'total_rows': len(df)
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        csv_file = self.get_object()
        import hashlib
        
        try:
            file_path = csv_file.file.path
            
            # Check if file exists
            if not os.path.exists(file_path):
                return Response({
                    'error': 'File not found on server'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate hash of file content for change detection
            with open(file_path, 'rb') as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Check if this is a re-upload of the same file (no changes)
            is_update = csv_file.data_hash and csv_file.data_hash != current_hash
            
            # Read the CSV file
            try:
                df = pd.read_csv(file_path)
            except pd.errors.EmptyDataError:
                return Response({
                    'error': 'The CSV file is empty'
                }, status=status.HTTP_400_BAD_REQUEST)
            except pd.errors.ParserError:
                return Response({
                    'error': 'Could not parse the CSV file. Please check the format.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process each row to link with crop images by sample_id
            created = 0
            updated = 0
            rows_processed = 0

            # Ensure sample_id column exists
            if 'sample_id' not in df.columns:
                return Response({
                    'error': "CSV must contain a 'sample_id' column"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update the columns in the model
            csv_file.columns = list(df.columns)
            csv_file.data_hash = current_hash
            
            # Process each row in the CSV
            for _, row in df.iterrows():
                sample_id = row.get('sample_id')
                if not sample_id or pd.isna(sample_id):
                    continue  # Skip rows without a valid sample_id
                    
                rows_processed += 1
                    
                # Look for matching crop images
                matching_images = CropImage.objects.filter(
                    sample_id=str(sample_id),  # Convert to string in case sample_id is numeric
                    uploaded_by=request.user
                )
                
                # Link found images to this CSV file
                for image in matching_images:
                    if image.csv_file != csv_file:
                        image.csv_file = csv_file
                        image.save()
                        updated += 1
                
                # Create/update metadata for the matching images
                for image in matching_images:
                    # Add each column as metadata
                    for column in df.columns:
                        if column != 'sample_id' and not pd.isna(row[column]):
                            # Format the value based on its type
                            value = row[column]
                            if isinstance(value, (int, float)) and pd.notna(value):
                                # Format numbers without trailing zeros
                                value = str(value).rstrip('0').rstrip('.') if '.' in str(value) else str(value)
                            else:
                                value = str(value)
                                
                            # Check if this metadata already exists
                            _, created_new = ImageMetadata.objects.update_or_create(
                                image=image,
                                label=column,
                                defaults={'value': value}
                            )
                            
                            if created_new:
                                created += 1
                            else:
                                updated += 1
            
            # Mark as processed
            csv_file.processed = True
            csv_file.save()
            
            return Response({
                'message': 'CSV file processed successfully',
                'created': created,
                'updated': updated,
                'rows_processed': rows_processed,
                'columns': csv_file.columns,
                'is_update': is_update
            })
        except Exception as e:
            import traceback
            print(f"Error processing CSV: {str(e)}")
            print(traceback.format_exc())
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class CsvDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        file_id = request.query_params.get('file_id')
        columns = request.query_params.getlist('columns[]', [])
        
        if not file_id:
            return Response({"error": "Missing file_id parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get the file, ensuring it belongs to the current user
            csv_file = get_object_or_404(CsvFile, id=file_id, uploaded_by=request.user)
            
            if not csv_file.processed:
                return Response({"error": "CSV file has not been processed yet"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if file exists 
            if not os.path.exists(csv_file.file.path):
                return Response({"error": "File not found on server"}, status=status.HTTP_404_NOT_FOUND)
            
            # Read the CSV file
            try:
                df = pd.read_csv(csv_file.file.path)
            except Exception as e:
                return Response({"error": f"Error reading CSV file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # If specific columns are requested, filter the dataframe
            if columns:
                # Always include sample_id column if it exists
                if 'sample_id' in df.columns and 'sample_id' not in columns:
                    columns.append('sample_id')
                    
                # Filter columns that exist in the dataframe
                valid_columns = [col for col in columns if col in df.columns]
                if not valid_columns:
                    return Response({"error": "None of the requested columns exist in the CSV file"}, status=status.HTTP_400_BAD_REQUEST)
                
                df = df[valid_columns]
            
            # Handle missing values for JSON serialization
            df = df.replace({np.nan: None})
            
            # Prepare data for visualization
            data = {
                'columns': list(df.columns),
                'rows': df.to_dict('records'),
                'total_rows': len(df),
                'column_types': {}
            }
            
            # Determine column types for visualization hints
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    data['column_types'][col] = 'numeric'
                elif pd.api.types.is_datetime64_dtype(df[col]):
                    data['column_types'][col] = 'datetime'
                else:
                    data['column_types'][col] = 'text'
            
            return Response(data)
            
        except CsvFile.DoesNotExist:
            return Response({"error": "CSV file not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
