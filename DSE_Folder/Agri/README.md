# AquaGreen Monitoring Platform

A comprehensive agricultural monitoring platform built with Django REST Framework and Vue.js, designed for greenhouse management, crop monitoring, and data analytics.

## 🌱 Overview

AquaGreen Monitoring is a full-stack web application that enables agricultural professionals to:
- Monitor greenhouse conditions and crop health
- Upload and process Excel data files for analysis
- Manage crop images with metadata
- Integrate CSV mapping files for data processing
- Visualize agricultural data through interactive dashboards
- Stream real-time data using Kafka integration

## 🏗️ Architecture

### Backend
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Message Queue**: Apache Kafka for real-time data processing
- **Authentication**: JWT-based authentication system
- **File Processing**: Pandas, OpenPyXL for Excel/CSV handling

### Frontend
- **Framework**: Vue.js 3 with Composition API
- **UI Library**: Bootstrap 5 for responsive design
- **State Management**: Vuex for centralized state management
- **Routing**: Vue Router for SPA navigation
- **Charts**: Chart.js integration for data visualization

### Infrastructure
- **Cloud Platform**: Google Cloud Platform
- **Deployment**: Google App Engine
- **Database**: Google Cloud SQL (PostgreSQL)
- **Storage**: Google Cloud Storage for media files
- **Security**: Google Secret Manager for sensitive data

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Cloud SDK
- PostgreSQL (for local development)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AquaGreen_Monitoring
   ```

2. **Backend Setup**
   ```bash
   cd AquaGreen_Monitoring
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your configuration
   
   # Run migrations
   cd backend
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run serve
   ```

4. **Access the application**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:8080
   - Admin Panel: http://localhost:8000/admin

## 🌐 Production Deployment

### Google Cloud Platform

This project is optimized for deployment on Google Cloud Platform. Follow the comprehensive deployment guide:

📖 **[Complete Deployment Guide](DEPLOYMENT_GUIDE.md)**

### Quick Deploy Commands
```bash
# Set up Google Cloud project
gcloud projects create your-project-id
gcloud config set project your-project-id
gcloud app create --region=us-central1

# Deploy to App Engine
gcloud builds submit --config=cloudbuild.yaml .
```

## 📁 Project Structure

```
AquaGreen_Monitoring/
├── backend/                    # Django backend
│   ├── data_processor/        # Main Django project
│   ├── file_uploader/         # File upload and processing
│   ├── kafka_producer/        # Kafka integration
│   ├── media/                 # Uploaded files
│   ├── static/                # Static files
│   └── templates/             # HTML templates
├── frontend/                   # Vue.js frontend
│   ├── src/
│   │   ├── components/        # Vue components
│   │   ├── views/             # Page components
│   │   ├── store/             # Vuex store
│   │   └── router/            # Vue Router config
│   ├── dist/                  # Production build
│   └── public/                # Static assets
├── app.yaml                   # App Engine configuration
├── cloudbuild.yaml           # Cloud Build configuration
├── main.py                   # WSGI entry point
└── DEPLOYMENT_GUIDE.md       # Deployment instructions
```

## 🔧 Configuration

### Environment Variables

#### Development
```bash
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
KAFKA_ENABLED=True
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

#### Production
```bash
SECRET_KEY=projects/PROJECT_ID/secrets/django-secret-key/versions/latest
DEBUG=False
DJANGO_SETTINGS_MODULE=data_processor.settings_production
CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:INSTANCE
DB_USER=django_user
DB_PASSWORD=projects/PROJECT_ID/secrets/db-password/versions/latest
DB_NAME=aquagreen_prod
```

## 🔒 Security Features

- **Authentication**: JWT-based user authentication
- **HTTPS**: TLS/SSL encryption for all communications
- **Secret Management**: Google Secret Manager integration
- **Input Validation**: Server-side validation for all inputs
- **CORS Protection**: Configurable cross-origin resource sharing
- **SQL Injection Prevention**: Django ORM protection
- **XSS Protection**: Content Security Policy headers

## 📊 Features

### Core Features
- ✅ User authentication and authorization
- ✅ Excel file upload and processing
- ✅ Crop image management with metadata
- ✅ CSV mapping file integration
- ✅ Data visualization and analytics
- ✅ Real-time data streaming with Kafka
- ✅ Responsive web interface

### Planned Features
- 🔄 Mobile application support
- 🔄 Advanced analytics dashboard
- 🔄 Email notifications
- 🔄 API rate limiting
- 🔄 Multi-tenant support

## 🧪 Testing

```bash
# Backend tests
cd AquaGreen_Monitoring/backend
python manage.py test

# Frontend tests
cd frontend
npm run test:unit
```

## 🔍 Monitoring and Logging

### Google Cloud Monitoring
- Application performance monitoring
- Error reporting and tracking
- Custom metrics and alerts
- Log aggregation and analysis

### Local Development
```bash
# View Django logs
python manage.py runserver --verbosity=2

# View frontend build logs
npm run serve
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript/Vue.js
- Write comprehensive tests for new features
- Update documentation for API changes
- Use conventional commit messages

## 📝 API Documentation

### Authentication Endpoints
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/refresh/` - Token refresh
- `POST /api/auth/logout/` - User logout

### Data Processing Endpoints
- `GET /api/files/` - List uploaded files
- `POST /api/files/upload/` - Upload Excel/CSV files
- `GET /api/data/` - Retrieve processed data
- `POST /api/images/` - Upload crop images

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database credentials in environment variables
   - Ensure PostgreSQL service is running
   - Verify network connectivity to Cloud SQL

2. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check STATIC_URL and STATIC_ROOT settings
   - Verify file permissions

3. **Frontend Build Errors**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility
   - Verify environment variables

### Getting Help

- 📖 Check the [Deployment Guide](DEPLOYMENT_GUIDE.md)
- 🐛 Report issues on GitHub
- 💬 Contact the development team
- 📚 Review Google Cloud documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Backend Development**: Django REST Framework specialists
- **Frontend Development**: Vue.js experts
- **DevOps**: Google Cloud Platform engineers
- **Agriculture Specialists**: Domain experts

## 🙏 Acknowledgments

- Django and Vue.js communities
- Google Cloud Platform documentation
- Open source contributors
- Agricultural research institutions

---

**Made with ❤️ for sustainable agriculture**