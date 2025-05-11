from rest_framework import serializers
from .models import ExcelFile, CropImage, ImageMetadata, CsvFile
from django.contrib.auth.models import User
import os

class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']

class ImageMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageMetadata
        fields = ['id', 'label', 'value']
        read_only_fields = ['id']

class CropImageSerializer(serializers.ModelSerializer):
    metadata = ImageMetadataSerializer(many=True, read_only=True)
    uploaded_by = UserSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CropImage
        fields = ['id', 'sample_id', 'image', 'image_url', 'description', 'uploaded_by', 'uploaded_at', 'metadata']
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by', 'image_url']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url') and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class ExcelFileSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size_in_bytes = serializers.SerializerMethodField()
    
    class Meta:
        model = ExcelFile
        fields = ['id', 'title', 'file', 'file_url', 'file_size_in_bytes', 'uploaded_by', 'uploaded_at', 'processed']
        read_only_fields = ['id', 'uploaded_at', 'processed', 'uploaded_by', 'file_url', 'file_size_in_bytes']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url') and request:
            return request.build_absolute_uri(obj.file.url)
        return None
        
    def get_file_size_in_bytes(self, obj):
        # First check if file size is in context (from detail view)
        if 'file_size' in self.context:
            return self.context['file_size']
        
        # Otherwise, get the actual file size from the file system
        if obj.file and hasattr(obj.file, 'path') and os.path.exists(obj.file.path):
            return os.path.getsize(obj.file.path)
        return 0

class CsvFileSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CsvFile
        fields = ['id', 'name', 'file', 'file_url', 'uploaded_by', 'uploaded_at', 'processed']
        read_only_fields = ['id', 'uploaded_at', 'processed', 'uploaded_by', 'file_url']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url') and request:
            return request.build_absolute_uri(obj.file.url)
        return None
