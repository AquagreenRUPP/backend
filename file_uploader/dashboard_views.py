from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ExcelFile, CropImage, CsvFile
import numpy as np
import pandas as pd

class DashboardDataView(APIView):
    """
    API view to provide data for the dashboard, including:
    - Plant Growth Analysis data
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Provide data for dashboard components including Plant Growth"""
        try:
            # Get user-specific data
            user = request.user
            
            # Get plant growth data (sample data for demonstration)
            plant_growth_data = {
                'growth_metrics': [
                    {
                        'date': '2025-05-01',
                        'height': 15.2,
                        'leaf_count': 8,
                        'health_score': 0.85
                    },
                    {
                        'date': '2025-05-08',
                        'height': 18.5,
                        'leaf_count': 12,
                        'health_score': 0.88
                    },
                    {
                        'date': '2025-05-15',
                        'height': 22.1,
                        'leaf_count': 15,
                        'health_score': 0.92
                    }
                ],
                'environmental_data': [
                    {
                        'date': '2025-05-01',
                        'temperature': 24.5,
                        'humidity': 65,
                        'light_intensity': 8500
                    },
                    {
                        'date': '2025-05-08',
                        'temperature': 25.2,
                        'humidity': 68,
                        'light_intensity': 8700
                    },
                    {
                        'date': '2025-05-15',
                        'temperature': 26.0,
                        'humidity': 70,
                        'light_intensity': 8900
                    }
                ]
            }
            
            # Get statistics about user data
            excel_files_count = ExcelFile.objects.filter(uploaded_by=user).count()
            crop_images_count = CropImage.objects.filter(uploaded_by=user).count()
            csv_files_count = CsvFile.objects.filter(uploaded_by=user).count()
            
            # Get latest file upload date
            latest_upload = None
            if ExcelFile.objects.filter(uploaded_by=user).exists():
                latest_upload = ExcelFile.objects.filter(uploaded_by=user).order_by('-uploaded_at').first().uploaded_at
            
            # Combine all data for the dashboard
            dashboard_data = {
                'plant_growth': plant_growth_data,
                'user_stats': {
                    'excel_files_count': excel_files_count,
                    'crop_images_count': crop_images_count,
                    'csv_files_count': csv_files_count,
                    'last_upload': latest_upload
                }
            }
            
            return Response(dashboard_data)
        
        except Exception as e:
            return Response({
                'error': str(e),
                'message': 'Error retrieving dashboard data.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
