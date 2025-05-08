from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExcelFileViewSet, CropImageViewSet, CsvFileViewSet

router = DefaultRouter()
router.register(r'excel-files', ExcelFileViewSet)
router.register(r'crop-images', CropImageViewSet)
router.register(r'csv-files', CsvFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
