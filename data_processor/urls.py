
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from file_uploader.auth import RegisterView, CustomTokenObtainPairView, UserProfileView
from rest_framework_simplejwt.views import TokenRefreshView
from file_uploader.views import ExcelFileViewSet, CropImageViewSet, CsvFileViewSet, ProcessedDataView, ExcelFileDetailView, ProcessFileView, CsvDataView
from file_uploader.dashboard_views import DashboardDataView
from rest_framework.routers import DefaultRouter


api_router = DefaultRouter()
api_router.register(r'excel-files', ExcelFileViewSet)
api_router.register(r'crop-images', CropImageViewSet)
api_router.register(r'csv-files', CsvFileViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/file-uploader/', include('file_uploader.urls')),

    path('api/', include(api_router.urls)),
    path('api/excel-files/<int:pk>/detail/', ExcelFileDetailView.as_view(), name='excel_file_detail'),
    path('api/excel-files/<int:pk>/process/', ProcessFileView.as_view(), name='process_file'),
    path('api/processed-data/by_file/', ProcessedDataView.as_view(), name='processed_data_by_file'),
    path('api/csv-data/', CsvDataView.as_view(), name='csv_data'),
    path('api/dashboard/', DashboardDataView.as_view(), name='dashboard_data'),
    

    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/profile/', UserProfileView.as_view(), name='user_profile'),
    path('api/auth/password-reset/', include("file_uploader.password_reset_urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
