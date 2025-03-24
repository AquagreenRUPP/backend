from rest_framework import serializers
from .models import ExcelFile, ProcessedData

class ExcelFileSerializer(serializers.ModelSerializer):
    """Serializer for the ExcelFile model."""
    
    class Meta:
        model = ExcelFile
        fields = ['id', 'title', 'file', 'uploaded_at', 'processed']
        read_only_fields = ['uploaded_at', 'processed']

class ProcessedDataSerializer(serializers.ModelSerializer):
    """Serializer for the ProcessedData model."""
    
    class Meta:
        model = ProcessedData
        fields = ['id', 'excel_file', 'data_json', 'created_at']
        read_only_fields = ['created_at']
