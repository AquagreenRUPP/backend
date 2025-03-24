from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import os
import pandas as pd
from io import BytesIO
from .models import ExcelFile, ProcessedData

class FileUploadTest(TestCase):
    """Test case for file upload functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = APIClient()
        
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
        
        # Check if file was processed
        excel_file = ExcelFile.objects.first()
        self.assertTrue(excel_file.processed)
        
        # Check if processed data was created
        self.assertEqual(ProcessedData.objects.count(), 1)
        
        # Check processed data content
        processed_data = ProcessedData.objects.first()
        self.assertEqual(len(processed_data.data_json), 3)  # 3 rows in our test data
