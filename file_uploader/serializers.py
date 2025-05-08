from rest_framework import serializers
from .models import ExcelFile, ProcessedData
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']

class ExcelFileSerializer(serializers.ModelSerializer):
    """Serializer for the ExcelFile model."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ExcelFile
        fields = ['id', 'title', 'file', 'uploaded_at', 'processed', 'user']
        read_only_fields = ['uploaded_at', 'processed', 'user']

class ProcessedDataSerializer(serializers.ModelSerializer):
    """Serializer for the ProcessedData model."""
    
    class Meta:
        model = ProcessedData
        fields = ['id', 'excel_file', 'data_json', 'created_at']
        read_only_fields = ['created_at']
