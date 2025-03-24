from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExcelFileViewSet, ProcessedDataViewSet

router = DefaultRouter()
router.register(r'excel-files', ExcelFileViewSet)
router.register(r'processed-data', ProcessedDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
