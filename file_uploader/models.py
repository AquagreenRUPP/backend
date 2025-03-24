from django.db import models
import uuid
import os
from django.contrib.auth.models import User

def get_file_path(instance, filename):
    """Generate a unique file path for the uploaded file."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('excel_files', filename)

class ExcelFile(models.Model):
    """Model to store uploaded Excel files."""
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=get_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='excel_files', null=True, blank=True)
    
    def __str__(self):
        return self.title

class ProcessedData(models.Model):
    """Model to store data extracted from Excel files."""
    excel_file = models.ForeignKey(ExcelFile, on_delete=models.CASCADE, related_name='processed_data')
    data_json = models.JSONField()  # Store the processed data as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Data from {self.excel_file.title}"
