FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBUG=0 \
    DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn psycopg2-binary

# Create media and static directories
RUN mkdir -p /app/backend/media /app/backend/static

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Command to run on container start
CMD ["sh", "-c", "cd backend && python manage_docker.py migrate && python manage_docker.py collectstatic --noinput && DJANGO_SETTINGS_MODULE=data_processor.settings_docker gunicorn data_processor.wsgi:application --bind 0.0.0.0:8000"]
