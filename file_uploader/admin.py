from django.contrib import admin
from .models import ExcelFile, CropImage, ImageMetadata, CsvFile

@admin.register(ExcelFile)
class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'processed')
    list_filter = ('processed', 'uploaded_at')
    search_fields = ('title',)

@admin.register(CropImage)
class CropImageAdmin(admin.ModelAdmin):
    list_display = ('sample_id', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('sample_id', 'description')

@admin.register(ImageMetadata)
class ImageMetadataAdmin(admin.ModelAdmin):
    list_display = ('image', 'label', 'value')
    list_filter = ('label',)
    search_fields = ('label', 'value')

@admin.register(CsvFile)
class CsvFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at', 'processed')
    list_filter = ('processed', 'uploaded_at')
    search_fields = ('name',)
