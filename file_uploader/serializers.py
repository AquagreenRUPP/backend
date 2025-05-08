from rest_framework import serializers
from .models import ExcelFile, CropImage, ImageMetadata, CsvFile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

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
    
    class Meta:
        model = ExcelFile
        fields = ['id', 'title', 'file', 'file_url', 'uploaded_by', 'uploaded_at', 'processed']
        read_only_fields = ['id', 'uploaded_at', 'processed', 'uploaded_by', 'file_url']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url') and request:
            return request.build_absolute_uri(obj.file.url)
        return None

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
