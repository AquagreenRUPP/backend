import pandas as pd
import os

# Create directory for sample data if it doesn't exist
os.makedirs('sample_data', exist_ok=True)

# Create sample data for testing
data = {
    'Product': ['Rice', 'Wheat', 'Corn', 'Soybeans', 'Coffee'],
    'Quantity': [1000, 1500, 2000, 800, 500],
    'Price': [25.50, 18.75, 15.20, 22.80, 35.60],
    'Date': ['2025-01-15', '2025-01-20', '2025-01-25', '2025-02-01', '2025-02-05'],
    'Supplier': ['Supplier A', 'Supplier B', 'Supplier A', 'Supplier C', 'Supplier B']
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
excel_path = os.path.join('sample_data', 'agricultural_products.xlsx')
df.to_excel(excel_path, index=False)

print(f"Sample Excel file created at: {excel_path}")
