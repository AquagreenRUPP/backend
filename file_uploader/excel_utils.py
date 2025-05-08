import pandas as pd
import logging
import json
from .models import ProcessedData

logger = logging.getLogger(__name__)

def process_excel_file(excel_file_instance):
    """
    Process an uploaded Excel file using pandas.
    
    Args:
        excel_file_instance: ExcelFile model instance
        
    Returns:
        ProcessedData: The created ProcessedData instance
    """
    try:
        file_path = excel_file_instance.file.path
        logger.info(f"Processing Excel file: {file_path}")
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Convert DataFrame to JSON
        json_data = json.loads(df.to_json(orient='records'))
        
        # Create ProcessedData instance
        processed_data = ProcessedData.objects.create(
            excel_file=excel_file_instance,
            data_json=json_data
        )
        
        # Mark the file as processed
        excel_file_instance.processed = True
        excel_file_instance.save()
        
        logger.info(f"Successfully processed Excel file: {file_path}")
        return [processed_data]  # Return as a list for compatibility with existing code
    
    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}")
        raise e
