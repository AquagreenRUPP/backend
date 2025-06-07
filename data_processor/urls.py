"""data_processor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from file_uploader.auth import RegisterView, CustomTokenObtainPairView, UserProfileView
from rest_framework_simplejwt.views import TokenRefreshView
from file_uploader.views import ExcelFileViewSet, CropImageViewSet, CsvFileViewSet, ProcessedDataView, ExcelFileDetailView, ProcessFileView, CsvDataView
from file_uploader.dashboard_views import DashboardDataView
from rest_framework.routers import DefaultRouter

# Create a router for direct API access
api_router = DefaultRouter()
api_router.register(r'excel-files', ExcelFileViewSet)
api_router.register(r'crop-images', CropImageViewSet)
api_router.register(r'csv-files', CsvFileViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/file-uploader/', include('file_uploader.urls')),
    # Direct API endpoints without the file-uploader prefix
    path('api/', include(api_router.urls)),
    
    # Custom API endpoints
    path('api/excel-files/<int:pk>/detail/', ExcelFileDetailView.as_view(), name='excel_file_detail'),
    path('api/excel-files/<int:pk>/process/', ProcessFileView.as_view(), name='process_file'),
    
    # Processed data endpoints
    path('api/processed-data/by_file/', ProcessedDataView.as_view(), name='processed_data_by_file'),
    path('api/csv-data/', CsvDataView.as_view(), name='csv_data'),
    
    # Dashboard data endpoint
    path('api/dashboard/', DashboardDataView.as_view(), name='dashboard_data'),
    
    # Authentication endpoints
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Password reset endpoints
    path('api/auth/password-reset/', include("file_uploader.password_reset_urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
