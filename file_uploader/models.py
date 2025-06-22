from django.db import models
from django.contrib.auth.models import User
import uuid
import os
from .encryption_utils import encryption_manager

def get_file_path(instance, filename):
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
    columns = models.JSONField(default=list, blank=True)
    data_hash = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return self.name

class CropImage(models.Model):
    sample_id = models.CharField(max_length=255)
    image = models.ImageField(upload_to='crop_images/')
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crop_images')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    csv_file = models.ForeignKey(CsvFile, on_delete=models.SET_NULL, related_name='images', null=True, blank=True)
    
    def __str__(self):
        return self.sample_id

class ImageMetadata(models.Model):
    image = models.ForeignKey(CropImage, on_delete=models.CASCADE, related_name='metadata')
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.label}: {self.value}"

class GeneticData(models.Model):
    file = models.FileField(upload_to='genetic_data/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=10, choices=[('csv', 'CSV'), ('xlsx', 'Excel')])
    total_records = models.IntegerField(default=0)
    processed = models.BooleanField(default=False)
    is_encrypted = models.BooleanField(default=False)
    encrypted_metadata = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Genetic Data - {self.uploaded_at}"
    
    def get_file_content(self):
        if self.is_encrypted and self.file:
            with open(self.file.path, 'rb') as f:
                encrypted_content = f.read()
            return encryption_manager.decrypt_file(encrypted_content)
        elif self.file:
            with open(self.file.path, 'rb') as f:
                return f.read()
        return None

class GeneticRecord(models.Model):
    genetic_data = models.ForeignKey(GeneticData, on_delete=models.CASCADE, related_name='records')
    record_number = models.IntegerField()
    location = models.CharField(max_length=100)
    f5_fruit_number = models.CharField(max_length=50)
    f5_code = models.CharField(max_length=50)
    f6_full_name = models.CharField(max_length=200)
    sixth_code = models.CharField(max_length=50)
    fruit_number = models.CharField(max_length=50)
    pollination_date = models.DateField(null=True)
    harvest_date = models.DateField(null=True)
    pedicel_length = models.FloatField(null=True)
    pedicel_width = models.FloatField(null=True)
    insertion_peduncle_size = models.FloatField(null=True)
    fruit_weight = models.FloatField(null=True)
    fruit_length = models.FloatField(null=True)
    fruit_width = models.FloatField(null=True)
    rind_thickness = models.FloatField(null=True)
    rind_hardness = models.FloatField(null=True)
    apex_size = models.FloatField(null=True)
    rind_stripe = models.CharField(max_length=100, null=True)
    flesh_hardness = models.CharField(max_length=100, null=True)
    flesh_color = models.CharField(max_length=100, null=True)
    brix_content = models.FloatField(null=True)
    seeds_quantity = models.IntegerField(null=True)
    remained_seeds = models.IntegerField(null=True)
    image = models.ForeignKey(CropImage, on_delete=models.SET_NULL, null=True, related_name='genetic_records')
    
    encrypted_genetic_signature = models.TextField(blank=True, null=True)
    encrypted_breeding_data = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('genetic_data', 'record_number', 'f5_code')

    def __str__(self):
        return f"Record {self.record_number} - {self.f5_code}"
    
    def set_encrypted_genetic_signature(self, data):
        if data:
            self.encrypted_genetic_signature = encryption_manager.encrypt_json(data)
    
    def get_encrypted_genetic_signature(self):
        if self.encrypted_genetic_signature:
            return encryption_manager.decrypt_json(self.encrypted_genetic_signature)
        return None
    
    def set_encrypted_breeding_data(self, data):
        if data:
            self.encrypted_breeding_data = encryption_manager.encrypt_json(data)
    
    def get_encrypted_breeding_data(self):
        if self.encrypted_breeding_data:
            return encryption_manager.decrypt_json(self.encrypted_breeding_data)
        return None
