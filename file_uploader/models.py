from django.db import models
from django.contrib.auth.models import User
import uuid
import os

def get_file_path(instance, filename):
    """Generate a unique file path for the uploaded file."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('excel_files', filename)

class ExcelFile(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=get_file_path)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='excel_files', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    @property
    def file_size(self):
        """Return the file size in bytes if available"""
        if self.file and hasattr(self.file, 'size'):
            return self.file.size
        elif self.file and os.path.exists(self.file.path):
            return os.path.getsize(self.file.path)
        return 0

class CsvFile(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='csv_files/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='csv_files')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

# Define this class after CsvFile to avoid import issues
class CropImage(models.Model):
    sample_id = models.CharField(max_length=255)
    image = models.ImageField(upload_to='crop_images/')
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crop_images')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Use string reference to avoid circular imports
    csv_file = models.ForeignKey(CsvFile, on_delete=models.SET_NULL, related_name='images', null=True, blank=True)
    
    def __str__(self):
        return self.sample_id

class ImageMetadata(models.Model):
    image = models.ForeignKey(CropImage, on_delete=models.CASCADE, related_name='metadata')
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.label}: {self.value}"
