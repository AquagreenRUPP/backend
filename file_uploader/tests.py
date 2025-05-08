from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import os
import pandas as pd
from io import BytesIO
from .models import ExcelFile
from django.contrib.auth.models import User

class FileUploadTest(TestCase):
    """Test case for file upload functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = APIClient()
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create a test Excel file
        self.excel_data = {
            'Name': ['John', 'Jane', 'Bob'],
            'Age': [30, 25, 40],
            'Salary': [50000, 60000, 70000]
        }
        self.df = pd.DataFrame(self.excel_data)
        
        # Save DataFrame to a BytesIO object
        self.excel_file = BytesIO()
        self.df.to_excel(self.excel_file, index=False)
        self.excel_file.seek(0)
        
    def test_file_upload(self):
        """Test file upload functionality."""
        url = reverse('excelfile-list')
        
        # Prepare file upload data
        upload_data = {
            'title': 'Test Excel File',
            'file': self.excel_file
        }
        
        # Upload file
        response = self.client.post(url, upload_data, format='multipart')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExcelFile.objects.count(), 1)
        
        # Check file details
        excel_file = ExcelFile.objects.first()
        self.assertEqual(excel_file.title, 'Test Excel File')
        self.assertEqual(excel_file.uploaded_by, self.user)

class CropImageTest(TestCase):
    """Test case for crop image functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = APIClient()
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_crop_image_list(self):
        """Test crop image listing."""
        url = reverse('cropimage-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
