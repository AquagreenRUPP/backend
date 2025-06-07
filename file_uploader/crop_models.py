from django.db import models
import uuid
import os
from django.contrib.auth.models import User

def get_crop_image_path(instance, filename):
    """Generate a unique file path for the uploaded crop image."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('crop_images', filename)

def get_csv_file_path(instance, filename):
    """Generate a unique file path for the uploaded CSV file."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('csv_files', filename)

class CsvFile(models.Model):
    """Model to store uploaded CSV mapping files."""
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=get_csv_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='csv_files')
    
    def __str__(self):
        return self.title

class CropImage(models.Model):
    """Model to store uploaded crop images."""
    image = models.ImageField(upload_to=get_crop_image_path, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    sample_id = models.CharField(max_length=50)
    csv_file = models.ForeignKey(CsvFile, on_delete=models.CASCADE, related_name='crop_images')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crop_images')
    
    def __str__(self):
        return f"Image {self.id} - {self.sample_id}"

class CropMetadata(models.Model):
    """Model to store additional metadata for crop images."""
    crop_image = models.ForeignKey(CropImage, on_delete=models.CASCADE, related_name='metadata')
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.label}: {self.value} for {self.crop_image.sample_id}"

    class Meta:
        unique_together = ('crop_image', 'label')
