from rest_framework import serializers
from django.contrib.auth.models import User
from .crop_models import CsvFile, CropImage, CropMetadata

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CropMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropMetadata
        fields = ['id', 'label', 'value']

class CropImageSerializer(serializers.ModelSerializer):
    metadata = CropMetadataSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = CropImage
        fields = ['id', 'image', 'image_url', 'sample_id', 'description', 'csv_file', 
                 'uploaded_at', 'user', 'user_details', 'metadata']
        extra_kwargs = {
            'user': {'write_only': True}
        }
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url') and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class CsvFileSerializer(serializers.ModelSerializer):
    crop_images_count = serializers.SerializerMethodField()
    metadata = CropMetadataSerializer(many=True, read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = CsvFile
        fields = ['id', 'title', 'file', 'uploaded_at', 'user', 'user_details', 'crop_images_count', 'metadata']
        extra_kwargs = {
            'user': {'write_only': True}
        }
    
    def get_crop_images_count(self, obj):
        return obj.crop_images.count()
