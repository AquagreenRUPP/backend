from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import crop_views

router = DefaultRouter()
router.register(r'excel-files', views.ExcelFileViewSet)

# Register crop image system endpoints
router.register(r'csv-files', crop_views.CsvFileViewSet)
router.register(r'crop-images', crop_views.CropImageViewSet)
router.register(r'crop-metadata', crop_views.CropMetadataViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
