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
    - Genetic Mapping data
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Provide data for dashboard components including Plant Growth and Genetic Mapping"""
        try:
            # Get user-specific data
            user = request.user
            
            # Get plant growth data (sample data for demonstration)
            plant_growth_data = {
                'growth_metrics': [
                    {
                        'date': '2025-05-01',
                        'plant_type': 'Tomato',
                        'growth_rate': 2.3,
                        'height': 15.7,
                        'health_index': 0.85
                    },
                    {
                        'date': '2025-05-08',
                        'plant_type': 'Tomato',
                        'growth_rate': 2.5,
                        'height': 18.2,
                        'health_index': 0.89
                    },
                    {
                        'date': '2025-05-15',
                        'plant_type': 'Tomato',
                        'growth_rate': 2.7,
                        'height': 21.0,
                        'health_index': 0.91
                    },
                    {
                        'date': '2025-05-01',
                        'plant_type': 'Lettuce',
                        'growth_rate': 1.8,
                        'height': 10.2,
                        'health_index': 0.78
                    },
                    {
                        'date': '2025-05-08',
                        'plant_type': 'Lettuce',
                        'growth_rate': 2.0,
                        'height': 12.0,
                        'health_index': 0.82
                    },
                    {
                        'date': '2025-05-15',
                        'plant_type': 'Lettuce',
                        'growth_rate': 2.1,
                        'height': 14.5,
                        'health_index': 0.87
                    }
                ],
                'summary': {
                    'average_growth_rate': 2.23,
                    'health_trend': 'positive',
                    'optimal_conditions': {
                        'temperature': '24-26°C',
                        'humidity': '65-70%',
                        'light': '16 hours/day'
                    }
                }
            }
            
            # Get genetic mapping data (sample data)
            genetic_mapping_data = {
                'gene_maps': [
                    {
                        'id': 1,
                        'name': 'Drought Resistance Gene Map',
                        'description': 'Genetic markers associated with drought resistance',
                        'image_url': '/media/genetic_maps/drought_resistance_map.jpg',
                        'markers_count': 15,
                        'created_at': '2025-05-10'
                    },
                    {
                        'id': 2,
                        'name': 'Yield Enhancement Gene Map',
                        'description': 'Genetic markers associated with enhanced crop yield',
                        'image_url': '/media/genetic_maps/yield_enhancement_map.jpg',
                        'markers_count': 23,
                        'created_at': '2025-05-12'
                    },
                    {
                        'id': 3,
                        'name': 'Disease Resistance Map',
                        'description': 'Genetic markers for common disease resistance',
                        'image_url': '/media/genetic_maps/disease_resistance_map.jpg',
                        'markers_count': 18,
                        'created_at': '2025-05-15'
                    }
                ],
                'recent_analyses': [
                    {
                        'name': 'Comparative Analysis: Drought Resistant vs. Standard',
                        'date': '2025-05-20',
                        'significant_markers': 7,
                        'confidence_level': 0.92
                    },
                    {
                        'name': 'Expression Profile: Stress Response Genes',
                        'date': '2025-05-18',
                        'significant_markers': 12,
                        'confidence_level': 0.89
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
                'genetic_mapping': genetic_mapping_data,
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
