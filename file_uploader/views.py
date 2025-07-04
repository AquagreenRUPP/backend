from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ExcelFile, CropImage, ImageMetadata, CsvFile, GeneticData, GeneticRecord
from .serializers import ExcelFileSerializer, CropImageSerializer, ImageMetadataSerializer, CsvFileSerializer
from .excel_utils import process_excel_file
from .encryption_utils import encryption_manager
import pandas as pd
import json
import os
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.views import APIView
import numpy as np
from django.core.files.base import ContentFile
import tempfile

class ExcelFileViewSet(viewsets.ModelViewSet):
    queryset = ExcelFile.objects.all().order_by('-uploaded_at')
    serializer_class = ExcelFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    def get_queryset(self):

        return ExcelFile.objects.filter(uploaded_by=self.request.user).order_by('-uploaded_at')
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        excel_file = self.get_object()
        
        try:
    
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
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            

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
            

            file_size = 0
            if excel_file.file and hasattr(excel_file.file, 'path') and os.path.exists(excel_file.file.path):
                file_size = os.path.getsize(excel_file.file.path)
            

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
            

            if not excel_file.file or not os.path.exists(excel_file.file.path):
                return Response({
                    'error': 'File not found or is invalid'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            file_path = excel_file.file.path
            file_ext = os.path.splitext(file_path)[1].lower()
            

            try:

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        sample = f.read(1024)

                        if ',' in sample and '\n' in sample:
                            df = pd.read_csv(file_path)
                            print(f"Successfully read as CSV: {file_path}")
                            return_early = True
                        else:
                            return_early = False
                except UnicodeDecodeError:

                    return_early = False
                
                if not return_early:

                    excel_engines = ['openpyxl', 'xlrd', None]  
                    last_error = None
                    
                    for engine in excel_engines:
                        try:
                            engine_arg = {} if engine is None else {'engine': engine}
                            df = pd.read_excel(file_path, **engine_arg)
                            break
                        except Exception as e:
                            last_error = e
                            continue
                    else:

                        try:
                            df = pd.read_csv(file_path)
                        except Exception:

                            raise last_error
                    

                if df.empty:
                    return Response({
                        'error': 'File contains no data'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    

                excel_file.processed = True
                excel_file.save()
                

                file_size = os.path.getsize(file_path)
                
                return Response({
                    'message': 'File processed successfully',
                    'file_id': excel_file.id,
                    'file_size_in_bytes': file_size
                })
            except pd.errors.EmptyDataError:
                return Response({
                    'error': 'The file is empty or contains no data'
                }, status=status.HTTP_400_BAD_REQUEST)
            except pd.errors.ParserError:
                return Response({
                    'error': 'Error parsing the file. It may be corrupted or in an unsupported format.'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'error': f'Error processing file: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
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

        return CropImage.objects.filter(uploaded_by=self.request.user).order_by('-uploaded_at')
    
    @action(detail=False, methods=['post'])
    def upload_images(self, request):
        csv_file_id = request.data.get('csv_file')
        sample_id_prefix = request.data.get('sample_id_prefix', '')
        

        csv_file = None
        if csv_file_id:
            try:
                csv_file = CsvFile.objects.get(id=csv_file_id, uploaded_by=request.user)
            except CsvFile.DoesNotExist:
                return Response({
                    'error': 'CSV file not found'
                }, status=status.HTTP_404_NOT_FOUND)
        

        if 'images' not in request.FILES:
            return Response({
                'error': 'No images provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_images = []
        for image_file in request.FILES.getlist('images'):

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

        instance = serializer.save(uploaded_by=self.request.user)
        
        self._extract_columns(instance)
    
    def get_queryset(self):

        return CsvFile.objects.filter(uploaded_by=self.request.user).order_by('-uploaded_at')
    
    def _extract_columns(self, csv_file):
        import hashlib
        
        try:
            file_path = csv_file.file.path

            df = pd.read_csv(file_path)
            

            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            

            csv_file.columns = list(df.columns)
            csv_file.data_hash = file_hash
            csv_file.save()
            
            return df
        except Exception as e:

            print(f"Error extracting columns: {str(e)}")
            return None
            
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        csv_file = self.get_object()
        
        try:
            file_path = csv_file.file.path

            df = pd.read_csv(file_path)
            

            preview_data = df.head(5).to_dict('records')
            

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
            
            if not os.path.exists(file_path):
                return Response({
                    'error': 'File not found on server'
                }, status=status.HTTP_400_BAD_REQUEST)
            

            with open(file_path, 'rb') as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()
            

            is_update = csv_file.data_hash and csv_file.data_hash != current_hash
            

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
            

            created = 0
            updated = 0
            rows_processed = 0


            if 'sample_id' not in df.columns:
                return Response({
                    'error': "CSV must contain a 'sample_id' column"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            csv_file.columns = list(df.columns)
            csv_file.data_hash = current_hash
            
            for _, row in df.iterrows():
                sample_id = row.get('sample_id')
                if not sample_id or pd.isna(sample_id):
                    continue  
                    
                rows_processed += 1
                    
                matching_images = CropImage.objects.filter(
                    sample_id=str(sample_id),  
                    uploaded_by=request.user
                )
                
                for image in matching_images:
                    if image.csv_file != csv_file:
                        image.csv_file = csv_file
                        image.save()
                        updated += 1
                
                for image in matching_images:
                    for column in df.columns:
                        if column != 'sample_id' and not pd.isna(row[column]):
                            value = row[column]
                            if isinstance(value, (int, float)) and pd.notna(value):
                                value = str(value).rstrip('0').rstrip('.') if '.' in str(value) else str(value)
                            else:
                                value = str(value)
                                
                            _, created_new = ImageMetadata.objects.update_or_create(
                                image=image,
                                label=column,
                                defaults={'value': value}
                            )
                            
                            if created_new:
                                created += 1
                            else:
                                updated += 1
            
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
            csv_file = get_object_or_404(CsvFile, id=file_id, uploaded_by=request.user)
            
            if not csv_file.processed:
                return Response({"error": "CSV file has not been processed yet"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not os.path.exists(csv_file.file.path):
                return Response({"error": "File not found on server"}, status=status.HTTP_404_NOT_FOUND)
            

            try:
                df = pd.read_csv(csv_file.file.path)
            except Exception as e:
                return Response({"error": f"Error reading CSV file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            if columns:
                if 'sample_id' in df.columns and 'sample_id' not in columns:
                    columns.append('sample_id')
                    
                valid_columns = [col for col in columns if col in df.columns]
                if not valid_columns:
                    return Response({"error": "None of the requested columns exist in the CSV file"}, status=status.HTTP_400_BAD_REQUEST)
                
                df = df[valid_columns]
            
            df = df.replace({np.nan: None})
            
            data = {
                'columns': list(df.columns),
                'rows': df.to_dict('records'),
                'total_rows': len(df),
                'column_types': {}
            }
            
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
            excel_file = get_object_or_404(ExcelFile, id=file_id, uploaded_by=request.user)
            
            if not excel_file.processed:
                return Response([])
            
            cache_key = f'processed_data_{file_id}'
            processed_data = request.session.get(cache_key)
            
            if processed_data:
                return Response(processed_data)
            
            file_path = excel_file.file.path
            try:
                if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                    return Response({"error": "File is empty or invalid"}, status=status.HTTP_400_BAD_REQUEST)
                
                file_ext = os.path.splitext(file_path)[1].lower()
                file_size = os.path.getsize(file_path)
                
                if file_ext == '.csv':
                    if file_size > 10 * 1024 * 1024:  
                        chunks = pd.read_csv(file_path, chunksize=1000)
                        all_data = []
                        for chunk in chunks:
                            all_data.append(chunk)
                        df = pd.concat(all_data)
                    else:
                        df = pd.read_csv(file_path)
                else:
                    if file_size > 10 * 1024 * 1024:  
                        chunks = pd.read_excel(file_path, chunksize=1000)
                        all_data = []
                        for chunk in chunks:
                            all_data.append(chunk)
                        df = pd.concat(all_data)
                    else:
                        df = pd.read_excel(file_path, engine='openpyxl')
                
                if df.empty:
                    return Response({"error": "File contains no data"}, status=status.HTTP_400_BAD_REQUEST)
                elif len(df) <= 1:
                    return Response({"error": "File contains only one row of data, which is insufficient for analysis"}, status=status.HTTP_400_BAD_REQUEST)
                elif len(df.columns) <= 1:
                    return Response({"error": "File contains only one column of data, which is insufficient for analysis"}, status=status.HTTP_400_BAD_REQUEST)
                
                if len(df) > 1000:
                    df = df.head(1000)
                    
                processed_data = df.replace({np.nan: None}).to_dict('records')
                
                for record in processed_data:
                    for key, value in record.items():
                        if isinstance(value, float) and (pd.isna(value) or np.isinf(value)):
                            record[key] = None
                        elif not isinstance(value, (str, int, float, bool, type(None))):
                            record[key] = str(value)
                
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

class GeneticDataUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            file = request.FILES.get('file')
            if not file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            file_type = 'csv' if file.name.endswith('.csv') else 'xlsx' if file.name.endswith('.xlsx') else None
            if not file_type:
                return Response({'error': 'Invalid file type. Please upload CSV or Excel file'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            file.seek(0)
            original_content = file.read()
            encrypted_content = encryption_manager.encrypt_file(original_content)
            
            encrypted_file = ContentFile(encrypted_content, name=file.name)
            
            file_metadata = {
                'original_name': file.name,
                'original_size': len(original_content),
                'content_type': file.content_type,
                'encryption_timestamp': str(pd.Timestamp.now())
            }
            
            genetic_data = GeneticData.objects.create(
                file=encrypted_file,
                uploaded_by=request.user,
                file_type=file_type,
                is_encrypted=True,
                encrypted_metadata=encryption_manager.encrypt_json(file_metadata)
            )
            
            try:
                if file_type == 'csv':
                    df = pd.read_csv(pd.io.common.BytesIO(original_content))
                else:
                    df = pd.read_excel(pd.io.common.BytesIO(original_content))
                
                if df.empty:
                    genetic_data.delete()
                    return Response({'error': 'The uploaded file is empty'}, status=status.HTTP_400_BAD_REQUEST)
                
                required_columns = ['No.', 'F5 Code']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    genetic_data.delete()
                    return Response({
                        'error': f'Missing required columns: {", ".join(missing_columns)}. Found columns: {", ".join(list(df.columns))}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                records = []
                for index, row in df.iterrows():
                    try:
                        record_data = {
                            'genetic_data': genetic_data,
                            'record_number': int(row['No.']),
                            'f5_code': str(row['F5 Code'])
                        }
                        
                        optional_fields = {
                            'location': '6th Location',
                            'f5_fruit_number': 'F5 Fruit #',
                            'f6_full_name': 'F6 Full Name',
                            'sixth_code': '6th Code',
                            'fruit_number': 'Fruit No.',
                            'pollination_date': 'Polli.Date(2024)',
                            'harvest_date': 'Har.Date(2024)',
                            'pedicel_length': 'Pedicel Length (cm)',
                            'pedicel_width': 'Pedicel Width (mm)',
                            'insertion_peduncle_size': 'Size of Insertion Peduncle (mm)',
                            'fruit_weight': 'Fruit Weight (Kg)',
                            'fruit_length': 'Fruit Length (cm)',
                            'fruit_width': 'Fruit Width (cm)',
                            'rind_thickness': 'Rind Thickness (mm)',
                            'rind_hardness': 'Rind Hardness (Kpa)',
                            'apex_size': 'Size of Apex (mm)',
                            'rind_stripe': 'Rind Stripe',
                            'flesh_hardness': 'Flesh Hardness',
                            'flesh_color': 'Flesh Color',
                            'brix_content': 'Flesh sugar content Brix (%)',
                            'seeds_quantity': 'Seeds Quantity',
                            'remained_seeds': 'Remained Seeds'
                        }
                        
                        for field, column in optional_fields.items():
                            if column in df.columns and pd.notna(row[column]):
                                try:
                                    if field in ['pollination_date', 'harvest_date']:
                                        record_data[field] = pd.to_datetime(row[column]).date()
                                    elif field in ['pedicel_length', 'pedicel_width', 'insertion_peduncle_size', 
                                                'fruit_weight', 'fruit_length', 'fruit_width', 'rind_thickness',
                                                'rind_hardness', 'apex_size', 'brix_content']:
                                        record_data[field] = float(row[column])
                                    elif field in ['seeds_quantity', 'remained_seeds']:
                                        record_data[field] = int(row[column])
                                    else:
                                        record_data[field] = str(row[column])
                                except (ValueError, TypeError):
                                    continue
                        
                        genetic_record = GeneticRecord(**record_data)
                        
                        genetic_signature = {
                            'f5_code': genetic_record.f5_code,
                            'f6_full_name': genetic_record.f6_full_name,
                            'location': genetic_record.location,
                            'breeding_cycle': 'F5-F6'
                        }
                        
                        breeding_data = {
                            'pollination_date': str(genetic_record.pollination_date) if genetic_record.pollination_date else None,
                            'harvest_date': str(genetic_record.harvest_date) if genetic_record.harvest_date else None,
                            'genetic_traits': {
                                'fruit_weight': genetic_record.fruit_weight,
                                'fruit_dimensions': {
                                    'length': genetic_record.fruit_length,
                                    'width': genetic_record.fruit_width
                                },
                                'quality_metrics': {
                                    'brix_content': genetic_record.brix_content,
                                    'flesh_color': genetic_record.flesh_color,
                                    'flesh_hardness': genetic_record.flesh_hardness
                                }
                            }
                        }
                        
                        genetic_record.set_encrypted_genetic_signature(genetic_signature)
                        genetic_record.set_encrypted_breeding_data(breeding_data)
                        
                        records.append(genetic_record)
                    except Exception as e:
                        print(f"Error processing row {index}: {e}")
                        continue
                
                if not records:
                    genetic_data.delete()
                    return Response({'error': 'No valid records found in the file'}, status=status.HTTP_400_BAD_REQUEST)
                
                GeneticRecord.objects.bulk_create(records)
                
                genetic_data.total_records = len(records)
                genetic_data.processed = True
                genetic_data.save()
                
                return Response({
                    'message': 'Genetic data uploaded and processed successfully',
                    'total_records': len(records),
                    'id': genetic_data.id
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                genetic_data.delete()
                return Response({
                    'error': f'Error processing file: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(f"Unexpected error: {e}")
            return Response({
                'error': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GeneticDataPreviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            file = request.FILES.get('file')
            if not file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            file_type = 'csv' if file.name.endswith('.csv') else 'xlsx' if file.name.endswith('.xlsx') else None
            if not file_type:
                return Response({'error': 'Invalid file type. Please upload CSV or Excel file'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            try:
                if file_type == 'csv':
                    file.seek(0)
                    df = pd.read_csv(file)
                else:
                    file.seek(0)
                    df = pd.read_excel(file)
                
                if df.empty:
                    return Response({'error': 'The uploaded file is empty'}, status=status.HTTP_400_BAD_REQUEST)
                
                required_columns = ['No.', 'F5 Code']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    return Response({
                        'error': f'Missing required columns: {", ".join(missing_columns)}. Found columns: {", ".join(list(df.columns))}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                preview_data = []
                for _, row in df.iterrows():
                    row_dict = {}
                    for col in df.columns:
                        value = row[col]
                        if pd.isna(value):
                            row_dict[col] = ''
                        else:
                            row_dict[col] = str(value)
                    preview_data.append(row_dict)
                
                return Response({
                    'preview_data': preview_data,
                    'columns': list(df.columns),
                    'total_records': len(preview_data),
                    'message': f'Successfully parsed {len(preview_data)} records'
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'error': f'Error processing file: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GeneticImageMatchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            genetic_data_id = request.data.get('genetic_data_id')
            images = request.FILES.getlist('images')
            
            if not genetic_data_id or not images:
                return Response({
                    'error': 'Both genetic data ID and images are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            genetic_data = GeneticData.objects.get(id=genetic_data_id, uploaded_by=request.user)
            
            if len(images) != genetic_data.total_records:
                return Response({
                    'error': f'Number of images ({len(images)}) does not match number of records ({genetic_data.total_records})'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            genetic_records = genetic_data.records.order_by('record_number')
            
            for i, image in enumerate(images):
                genetic_record = genetic_records[i]
                
                crop_image = CropImage.objects.create(
                    sample_id=f"{genetic_record.f5_code}",
                    image=image,
                    uploaded_by=request.user,
                    description=f"Genetic Record {genetic_record.record_number} - {genetic_record.f5_code}"
                )
                
                genetic_record.image = crop_image
                genetic_record.save()
            
            return Response({
                'message': f'Successfully uploaded and matched {len(images)} images with genetic records'
            }, status=status.HTTP_201_CREATED)
            
        except GeneticData.DoesNotExist:
            return Response({
                'error': 'Genetic data not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error uploading images: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GeneticDataListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            genetic_data_list = GeneticData.objects.filter(
                uploaded_by=request.user
            ).order_by('-uploaded_at')
            
            data = []
            for genetic_data in genetic_data_list:
                metadata = None
                if genetic_data.is_encrypted and genetic_data.encrypted_metadata:
                    try:
                        metadata = encryption_manager.decrypt_json(genetic_data.encrypted_metadata)
                    except:
                        metadata = None
                
                data.append({
                    'id': genetic_data.id,
                    'uploaded_at': genetic_data.uploaded_at,
                    'file_type': genetic_data.file_type,
                    'total_records': genetic_data.total_records,
                    'processed': genetic_data.processed,
                    'is_encrypted': genetic_data.is_encrypted,
                    'file_name': metadata.get('original_name') if metadata else (os.path.basename(genetic_data.file.name) if genetic_data.file else None),
                    'original_size': metadata.get('original_size') if metadata else None,
                    'encryption_timestamp': metadata.get('encryption_timestamp') if metadata else None
                })
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'Error fetching genetic data: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GeneticRecordsDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, genetic_data_id):
        try:
            genetic_data = GeneticData.objects.get(
                id=genetic_data_id,
                uploaded_by=request.user
            )
            
            records = GeneticRecord.objects.filter(
                genetic_data=genetic_data
            ).order_by('record_number').select_related('image')
            
            data = []
            for record in records:
                record_data = {
                    'id': record.id,
                    'record_number': record.record_number,
                    'f5_code': record.f5_code,
                    'location': record.location,
                    'f5_fruit_number': record.f5_fruit_number,
                    'f6_full_name': record.f6_full_name,
                    'sixth_code': record.sixth_code,
                    'fruit_number': record.fruit_number,
                    'pollination_date': record.pollination_date,
                    'harvest_date': record.harvest_date,
                    'pedicel_length': record.pedicel_length,
                    'pedicel_width': record.pedicel_width,
                    'insertion_peduncle_size': record.insertion_peduncle_size,
                    'fruit_weight': record.fruit_weight,
                    'fruit_length': record.fruit_length,
                    'fruit_width': record.fruit_width,
                    'rind_thickness': record.rind_thickness,
                    'rind_hardness': record.rind_hardness,
                    'apex_size': record.apex_size,
                    'rind_stripe': record.rind_stripe,
                    'flesh_hardness': record.flesh_hardness,
                    'flesh_color': record.flesh_color,
                    'brix_content': record.brix_content,
                    'seeds_quantity': record.seeds_quantity,
                    'remained_seeds': record.remained_seeds,
                    'image': {
                        'id': record.image.id,
                        'sample_id': record.image.sample_id,
                        'image': record.image.image.url,
                        'description': record.image.description,
                        'uploaded_at': record.image.uploaded_at
                    } if record.image else None
                }
                data.append(record_data)
            
            return Response(data, status=status.HTTP_200_OK)
        except GeneticData.DoesNotExist:
            return Response({
                'error': 'Genetic data not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error fetching genetic records: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GeneticDataDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, genetic_data_id):
        try:
            genetic_data = GeneticData.objects.get(
                id=genetic_data_id,
                uploaded_by=request.user
            )
            
            records = GeneticRecord.objects.filter(genetic_data=genetic_data)
            
            for record in records:
                if record.image:
                    if record.image.image:
                        try:
                            record.image.image.delete()
                        except:
                            pass  
                    record.image.delete()
            
            if genetic_data.file:
                try:
                    genetic_data.file.delete()
                except:
                    pass  
            
            genetic_data.delete()
            
            return Response({
                'message': 'Genetic data deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except GeneticData.DoesNotExist:
            return Response({
                'error': 'Genetic data not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error deleting genetic data: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SecureFileDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, genetic_data_id):
        try:
            genetic_data = GeneticData.objects.get(
                id=genetic_data_id,
                uploaded_by=request.user
            )
            
            if not genetic_data.file:
                return Response({
                    'error': 'File not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if genetic_data.is_encrypted:
                decrypted_content = genetic_data.get_file_content()
                
                metadata = None
                if genetic_data.encrypted_metadata:
                    try:
                        metadata = encryption_manager.decrypt_json(genetic_data.encrypted_metadata)
                    except:
                        metadata = {}
                
                from django.http import HttpResponse
                response = HttpResponse(
                    decrypted_content,
                    content_type=metadata.get('content_type', 'application/octet-stream')
                )
                response['Content-Disposition'] = f'attachment; filename="{metadata.get("original_name", "genetic_data.csv")}"'
                return response
            else:
                from django.http import FileResponse
                return FileResponse(
                    genetic_data.file.open('rb'),
                    as_attachment=True,
                    filename=os.path.basename(genetic_data.file.name)
                )
                
        except GeneticData.DoesNotExist:
            return Response({
                'error': 'Genetic data not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error downloading file: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EncryptionStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            total_genetic_data = GeneticData.objects.filter(uploaded_by=request.user).count()
            encrypted_genetic_data = GeneticData.objects.filter(
                uploaded_by=request.user, 
                is_encrypted=True
            ).count()
            
            total_records = GeneticRecord.objects.filter(
                genetic_data__uploaded_by=request.user
            ).count()
            
            encrypted_records = GeneticRecord.objects.filter(
                genetic_data__uploaded_by=request.user,
                encrypted_genetic_signature__isnull=False
            ).count()
            
            return Response({
                'encryption_stats': {
                    'total_genetic_files': total_genetic_data,
                    'encrypted_genetic_files': encrypted_genetic_data,
                    'total_genetic_records': total_records,
                    'encrypted_genetic_records': encrypted_records,
                    'encryption_percentage': round((encrypted_genetic_data / total_genetic_data * 100) if total_genetic_data > 0 else 0, 2)
                },
                'encryption_enabled': True,
                'encryption_algorithm': 'AES-256 (Fernet)'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error getting encryption status: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
