from django.contrib import admin
from .models import ExcelFile, ProcessedData

@admin.register(ExcelFile)
class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'processed')
    list_filter = ('processed', 'uploaded_at')
    search_fields = ('title',)

@admin.register(ProcessedData)
class ProcessedDataAdmin(admin.ModelAdmin):
    list_display = ('excel_file', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('excel_file__title',)
