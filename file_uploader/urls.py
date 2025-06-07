from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExcelFileViewSet, CropImageViewSet, CsvFileViewSet, ProcessFileView, ExcelFileDetailView, GeneticDataUploadView, GeneticDataPreviewView, GeneticImageMatchView, GeneticDataListView, GeneticRecordsDetailView, GeneticDataDeleteView, SecureFileDownloadView, EncryptionStatusView

router = DefaultRouter()
router.register(r'excel-files', ExcelFileViewSet)
router.register(r'crop-images', CropImageViewSet)
router.register(r'csv-files', CsvFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('excel-files/<int:pk>/process/', ProcessFileView.as_view(), name='process-file'),
    path('excel-files/<int:pk>/detail/', ExcelFileDetailView.as_view(), name='excel-file-detail'),
    path('genetic-data/', GeneticDataListView.as_view(), name='genetic-data-list'),
    path('genetic-data/preview/', GeneticDataPreviewView.as_view(), name='genetic-data-preview'),
    path('genetic-data/upload/', GeneticDataUploadView.as_view(), name='genetic-data-upload'),
    path('genetic-data/<int:genetic_data_id>/records/', GeneticRecordsDetailView.as_view(), name='genetic-records-detail'),
    path('genetic-data/<int:genetic_data_id>/', GeneticDataDeleteView.as_view(), name='genetic-data-delete'),
    path('genetic-data/<int:genetic_data_id>/download/', SecureFileDownloadView.as_view(), name='secure-file-download'),
    path('genetic-data/images/', GeneticImageMatchView.as_view(), name='genetic-image-match'),
    path('encryption/status/', EncryptionStatusView.as_view(), name='encryption-status'),
]
