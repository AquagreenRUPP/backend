import os
import sys

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data_processor.settings_production')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

# Create the WSGI application
application = get_wsgi_application()

# App Engine looks for 'app' 
app = application 