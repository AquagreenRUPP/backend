# 🚀 AquaGreen Agricultural Platform - Docker Deployment Guide

## 📋 Overview

This guide will help you deploy the AquaGreen Agricultural Platform using Docker on your VM. The platform consists of:

- **Backend**: Django REST API with encryption features
- **Frontend**: Vue.js SPA with modern UI
- **Database**: PostgreSQL with persistence
- **Reverse Proxy**: Nginx for production routing

## 🛠️ Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB minimum
- **Network**: Port 80 and 443 accessible

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git

## 🔧 Installation Steps

### 1. Install Docker on Your VM

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

# Verify installation
docker --version
docker-compose --version
```

### 2. Deploy the Application

```bash
# Clone the repository
git clone <your-repo-url>
cd Agri

# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh production
```

## 🔐 Security Features

### Built-in Security
✅ **Database Encryption**: AES-256 encryption for sensitive data  
✅ **File Encryption**: Encrypted file storage  
✅ **JWT Authentication**: Secure token-based auth  
✅ **Rate Limiting**: API rate limiting  
✅ **Security Headers**: OWASP recommended headers  

## 📊 Service Management

### Basic Commands
```bash
# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Backup database
docker-compose exec postgres pg_dump -U postgres agri_db > backup.sql
```

## 🎯 Default Credentials

**Admin Login**: admin / admin123  
⚠️ **Change immediately after deployment!**

## 📞 Access URLs

- **Main App**: http://your-server-ip
- **Admin Panel**: http://your-server-ip/admin/
- **API**: http://your-server-ip/api/

---

**🌱 Ready for Production Deployment! 🚀** 