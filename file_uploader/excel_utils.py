import pandas as pd
import logging
import json

logger = logging.getLogger(__name__)

def process_excel_file(excel_file_instance):
    try:
        file_path = excel_file_instance.file.path
        logger.info(f"Processing Excel file: {file_path}")
        
        df = pd.read_excel(file_path)
        
        json_data = json.loads(df.to_json(orient='records'))
        
        excel_file_instance.processed = True
        excel_file_instance.save()
        
        logger.info(f"Successfully processed Excel file: {file_path}")
        return json_data
    
    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}")
        raise e
