from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExcelFileViewSet, CropImageViewSet, CsvFileViewSet, ProcessFileView, ExcelFileDetailView

router = DefaultRouter()
router.register(r'excel-files', ExcelFileViewSet)
router.register(r'crop-images', CropImageViewSet)
router.register(r'csv-files', CsvFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('excel-files/<int:pk>/process/', ProcessFileView.as_view(), name='process-file'),
    path('excel-files/<int:pk>/detail/', ExcelFileDetailView.as_view(), name='excel-file-detail'),
]
