# 🚀 GitHub Setup & VM Deployment Guide

## 📋 Step 1: Setup GitHub Repository

### Option A: Create New Repository
1. Go to https://github.com/Boromrop
2. Click "New repository"
3. Name: `agri-platform` or `aquagreen-platform`
4. Set to Public or Private
5. **Don't** initialize with README (we have files already)
6. Click "Create repository"

### Option B: Use Existing Repository
If you have an existing repository, make sure it's accessible and update the remote URL.

## 📁 Step 2: Push Your Code to GitHub

### On Your Local Machine (Windows):

```powershell
# Navigate to your project
cd D:\DSE_Folder\Agri

# Check current git status
git status

# Add all deployment files
git add docker-compose.yml .env.example deploy.sh init-db.sql nginx/ DEPLOYMENT_GUIDE_DOCKER.md PRE_DEPLOYMENT_CHECKLIST.md

# Commit changes
git commit -m "🚀 Add production Docker deployment configuration"

# Set the correct remote URL (replace with your actual repo)
git remote set-url origin https://github.com/Boromrop/your-repo-name.git

# Push to GitHub
git push origin main
```

### If Git Push Fails:
```powershell
# Create a new repository and push
git remote remove origin
git remote add origin https://github.com/Boromrop/your-new-repo-name.git
git branch -M main
git push -u origin main
```

## 🖥️ Step 3: Deploy on Your Google Cloud VM

### A. Connect to Your VM
```bash
# SSH into your VM (you're already connected)
# Make sure you're in the home directory
cd ~
```

### B. Install Prerequisites
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git (if not installed)
sudo apt install git -y

# Restart session to apply docker group changes
exec sudo su -l $USER
```

### C. Clone and Deploy
```bash
# Clone your repository
git clone https://github.com/Boromrop/your-repo-name.git
cd your-repo-name

# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### D. Configure Environment (.env file)
```bash
# Edit these values in .env:
DB_PASSWORD=your_super_secure_password_123
SECRET_KEY=your_django_secret_key_50_characters_long
DOMAIN_NAME=your-vm-external-ip-or-domain.com
EMAIL_HOST_USER=your_gmail@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### E. Deploy Application
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh production

# Wait for deployment to complete (5-10 minutes)
```

## 🔗 Step 4: Access Your Application

### Find Your VM External IP:
```bash
# Get your VM's external IP
curl -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/network-interfaces/0/external-ip
```

### Access URLs:
- **Main Application**: `http://YOUR-VM-IP`
- **Django Admin**: `http://YOUR-VM-IP/admin/`
- **API Documentation**: `http://YOUR-VM-IP/api/`

### Default Login:
- **Username**: `admin`
- **Password**: `admin123`
- ⚠️ **Change immediately after first login!**

## 🛠️ Step 5: Post-Deployment Configuration

### A. Configure Firewall (Google Cloud)
```bash
# Allow HTTP traffic
gcloud compute firewall-rules create allow-http --allow tcp:80 --source-ranges 0.0.0.0/0 --description "Allow HTTP"

# Allow HTTPS traffic
gcloud compute firewall-rules create allow-https --allow tcp:443 --source-ranges 0.0.0.0/0 --description "Allow HTTPS"
```

### B. Monitor Services
```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f

# Check specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx
```

### C. Backup Database
```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres agri_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Schedule automatic backups (optional)
(crontab -l 2>/dev/null; echo "0 2 * * * cd /path/to/your/app && docker-compose exec postgres pg_dump -U postgres agri_db > backup_\$(date +\%Y\%m\%d_\%H\%M\%S).sql") | crontab -
```

## 🔐 Step 6: Security Hardening

### A. Change Default Passwords
```bash
# Connect to backend container
docker-compose exec backend python manage.py shell

# In Python shell:
from django.contrib.auth.models import User
admin = User.objects.get(username='admin')
admin.set_password('your_new_secure_password')
admin.save()
exit()
```

### B. Update Environment Variables
```bash
# Edit .env with secure values
nano .env

# Restart services
docker-compose down
docker-compose up -d
```

### C. Enable HTTPS (Optional)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate (if you have a domain)
sudo certbot --nginx -d your-domain.com

# Or use the nginx SSL configuration we provided
```

## 🚨 Troubleshooting

### Common Issues:

#### 1. Port 80 Already in Use
```bash
sudo lsof -i :80
sudo systemctl stop apache2  # or nginx
```

#### 2. Docker Permission Denied
```bash
sudo usermod -aG docker $USER
exec sudo su -l $USER
```

#### 3. Services Not Starting
```bash
# Check logs
docker-compose logs

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### 4. Database Connection Issues
```bash
# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

## 📊 Architecture Overview

```
Internet → Google Cloud Firewall → VM → Nginx (Port 80/443) → Frontend/Backend → PostgreSQL
```

### Service Components:
- **Nginx**: Reverse proxy and static file server
- **Frontend**: Vue.js application (Port 8080 internal)
- **Backend**: Django REST API (Port 8000 internal) 
- **Database**: PostgreSQL (Port 5432 internal)

## 🎯 Success Indicators

✅ All services running: `docker-compose ps`  
✅ Website accessible: `http://YOUR-VM-IP`  
✅ Admin panel working: `http://YOUR-VM-IP/admin/`  
✅ API responding: `http://YOUR-VM-IP/api/`  
✅ File uploads working  
✅ Database encryption active  

## 🔄 Updating Your Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Run migrations if needed
docker-compose exec backend python manage.py migrate
```

## 📞 Support Checklist

If you encounter issues:
1. Check service logs: `docker-compose logs`
2. Verify environment variables in `.env`
3. Ensure VM firewall allows HTTP/HTTPS
4. Check disk space: `df -h`
5. Verify DNS settings (if using domain)

---

## 🚀 Quick Deployment Summary

```bash
# On VM:
git clone https://github.com/Boromrop/your-repo-name.git
cd your-repo-name
cp .env.example .env
nano .env  # Configure your settings
chmod +x deploy.sh
./deploy.sh production

# Access: http://YOUR-VM-IP
# Admin: http://YOUR-VM-IP/admin/ (admin/admin123)
```

**🌱 Your AquaGreen Platform is Ready to Grow! 🚀** 