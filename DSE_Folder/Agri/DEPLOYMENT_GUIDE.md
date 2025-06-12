# AquaGreen Monitoring - Google Cloud Deployment Guide

This guide will help you deploy the AquaGreen Monitoring application to Google Cloud Platform professionally and securely.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Google Cloud Setup](#google-cloud-setup)
3. [Database Setup](#database-setup)
4. [Application Configuration](#application-configuration)
5. [Deployment](#deployment)
6. [Post-Deployment](#post-deployment)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

Before starting, ensure you have:
- Google Cloud Platform account with billing enabled
- Google Cloud SDK (`gcloud`) installed and configured
- Python 3.10+ installed locally
- Node.js 18+ installed locally
- Basic understanding of Django and Vue.js

## Google Cloud Setup

### 1. Create a New Project
```bash
# Set your project ID (replace with your desired project ID)
export PROJECT_ID="aquagreen-monitoring-prod"

# Create the project
gcloud projects create $PROJECT_ID --name="AquaGreen Monitoring"

# Set the project as default
gcloud config set project $PROJECT_ID
```

### 2. Enable Required APIs
```bash
gcloud services enable appengine.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 3. Initialize App Engine
```bash
gcloud app create --region=us-central1
```

## Database Setup

### 1. Create Cloud SQL Instance
```bash
# Create PostgreSQL instance
gcloud sql instances create aquagreen-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=YOUR_SECURE_PASSWORD

# Create database
gcloud sql databases create aquagreen_prod --instance=aquagreen-db

# Create database user
gcloud sql users create django_user \
    --instance=aquagreen-db \
    --password=YOUR_DJANGO_USER_PASSWORD
```

### 2. Configure Database Connection
```bash
# Get the connection name
gcloud sql instances describe aquagreen-db --format="value(connectionName)"
```
Save this connection name - you'll need it for configuration.

## Application Configuration

### 1. Create Secret Manager Secrets
```bash
# Create secret key for Django
echo -n "$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" | \
gcloud secrets create django-secret-key --data-file=-

# Create database password
echo -n "YOUR_DJANGO_USER_PASSWORD" | \
gcloud secrets create db-password --data-file=-
```

### 2. Update app.yaml Configuration
Edit the `app.yaml` file and update the following values:
```yaml
env_variables:
  SECRET_KEY: "projects/YOUR_PROJECT_ID/secrets/django-secret-key/versions/latest"
  GOOGLE_CLOUD_PROJECT: "YOUR_PROJECT_ID"
  CLOUD_SQL_CONNECTION_NAME: "YOUR_PROJECT_ID:us-central1:aquagreen-db"
  DB_USER: "django_user"
  DB_PASSWORD: "projects/YOUR_PROJECT_ID/secrets/db-password/versions/latest"
  DB_NAME: "aquagreen_prod"

beta_settings:
  cloud_sql_instances: YOUR_PROJECT_ID:us-central1:aquagreen-db
```

### 3. Configure IAM Permissions
```bash
# Grant App Engine access to Cloud SQL
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
    --role="roles/cloudsql.client"

# Grant access to Secret Manager
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## Deployment

### 1. Build and Deploy Using Cloud Build
```bash
# Submit build to Cloud Build
gcloud builds submit --config=cloudbuild.yaml .
```

### 2. Alternative: Manual Deployment
If you prefer manual deployment:

```bash
# Build frontend
cd AquaGreen_Monitoring/frontend
npm install
npm run build

# Deploy to App Engine
cd ../..
gcloud app deploy app.yaml --quiet
```

### 3. Run Database Migrations
```bash
# Connect to your deployed app and run migrations
gcloud app browse
# Or use Cloud Shell to connect and run:
# python manage.py migrate --settings=data_processor.settings_production
```

## Post-Deployment

### 1. Create Superuser
```bash
# Use Cloud Shell or connect to your app
python manage.py createsuperuser --settings=data_processor.settings_production
```

### 2. Configure Custom Domain (Optional)
```bash
# Map custom domain
gcloud app domain-mappings create your-domain.com
```

### 3. Set up SSL Certificate
```bash
# Create managed SSL certificate
gcloud app ssl-certificates create --domains=your-domain.com
```

## Environment Variables Reference

### Required Environment Variables
- `SECRET_KEY`: Django secret key (use Secret Manager)
- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `CLOUD_SQL_CONNECTION_NAME`: Format: project:region:instance
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password (use Secret Manager)
- `DB_NAME`: Database name

### Optional Environment Variables
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `SENDGRID_API_KEY`: For email functionality
- `DEFAULT_FROM_EMAIL`: Default email sender
- `REDIS_URL`: For caching (if using Memorystore)
- `ALLOWED_ORIGINS`: CORS allowed origins

## Monitoring and Maintenance

### 1. Set up Monitoring
```bash
# Enable Error Reporting
gcloud services enable clouderrorreporting.googleapis.com

# Enable Cloud Monitoring
gcloud services enable monitoring.googleapis.com
```

### 2. Set up Logging
- Check logs: `gcloud app logs tail -s default`
- View logs in Cloud Console: https://console.cloud.google.com/logs

### 3. Backup Strategy
```bash
# Create automated backups for Cloud SQL
gcloud sql instances patch aquagreen-db --backup-start-time=02:00
```

### 4. Security Best Practices
- Regularly rotate secrets in Secret Manager
- Monitor IAM permissions
- Enable VPC firewall rules if needed
- Use least privilege principle for service accounts

## Scaling Configuration

### Automatic Scaling (Default)
```yaml
automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6
  target_throughput_utilization: 0.6
```

### Manual Scaling (For consistent performance)
```yaml
manual_scaling:
  instances: 2
```

## Cost Optimization

1. **Database**: Start with `db-f1-micro` and upgrade as needed
2. **App Engine**: Use automatic scaling with appropriate min/max instances
3. **Storage**: Use Cloud Storage for media files instead of instance storage
4. **Monitoring**: Set up billing alerts

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify Cloud SQL connection name
   - Check IAM permissions
   - Ensure database user exists

2. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check STATIC_URL and STATIC_ROOT settings

3. **CORS Issues**
   - Update CORS_ALLOWED_ORIGINS in settings
   - Check frontend API endpoint configuration

### Support Commands
```bash
# View application logs
gcloud app logs tail -s default

# Check deployment status
gcloud app versions list

# Access Cloud Shell
gcloud cloud-shell ssh

# Connect to Cloud SQL
gcloud sql connect aquagreen-db --user=django_user
```

## Production Checklist

- [ ] Secret key is generated and stored in Secret Manager
- [ ] Database is created and configured
- [ ] All required APIs are enabled
- [ ] IAM permissions are properly configured
- [ ] Environment variables are set
- [ ] Static files are collected
- [ ] Database migrations are applied
- [ ] Superuser account is created
- [ ] HTTPS is configured (if using custom domain)
- [ ] Monitoring and logging are set up
- [ ] Backup strategy is implemented

## Security Considerations

1. **Never commit sensitive data** to version control
2. **Use Secret Manager** for all secrets
3. **Enable HTTPS** for production
4. **Regularly update dependencies**
5. **Monitor security advisories**
6. **Use strong passwords** and enable 2FA
7. **Limit IAM permissions** to minimum required

---

**Need Help?** 
- Google Cloud Documentation: https://cloud.google.com/docs
- Django on Google Cloud: https://cloud.google.com/python/django
- App Engine Documentation: https://cloud.google.com/appengine/docs