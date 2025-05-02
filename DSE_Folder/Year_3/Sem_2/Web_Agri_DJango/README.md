# AquaGreen Excel Data Processor

A full-stack web application for uploading, processing, and visualizing Excel data. The system features a Django backend for data processing and a Vue.js frontend for user interaction.

## Features

- User authentication with JWT
- Excel file upload and processing
- Data extraction and analysis using pandas
- Integration with Kafka for data streaming (optional)
- Interactive data visualization
- RESTful API for file management and data retrieval
- Responsive Vue.js frontend

## Project Structure

```
project_root/
├── data_processor/           # Django backend
│   ├── data_processor/       # Main project settings
│   ├── file_uploader/        # App for file uploads and processing
│   ├── media/                # Uploaded files storage
│   └── manage.py             # Django management script
├── frontend/                 # Vue.js frontend
│   ├── public/               # Static assets
│   ├── src/                  # Source code
│   │   ├── components/       # Vue components
│   │   ├── views/            # Vue views
│   │   ├── store/            # Vuex store
│   │   ├── router/           # Vue Router
│   │   └── App.vue           # Root component
│   ├── package.json          # NPM dependencies
│   └── vue.config.js         # Vue configuration
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables
```

## Setup Instructions

### Backend Setup

1. **Install Python Dependencies**

```bash
pip install -r requirements.txt
```

2. **Configure Environment Variables**

Copy the `env.sample` file to `.env` in the project root and update the values:

```bash
cp env.sample .env
```

3. **Database Setup**

For development, SQLite is configured by default. For production, uncomment the PostgreSQL configuration in `settings.py` and ensure your PostgreSQL server is running.

4. **Run Migrations**

```bash
cd data_processor
python manage.py makemigrations
python manage.py migrate
```

5. **Create Superuser**

```bash
python manage.py createsuperuser
```

6. **Run the Django Development Server**

```bash
python manage.py runserver
```

The backend server will be available at http://localhost:8000/

### Frontend Setup

1. **Install Node.js Dependencies**

```bash
cd frontend
npm install
```

2. **Run the Vue.js Development Server**

```bash
npm run serve
```

The frontend application will be available at http://localhost:8080/

## Authentication

The application uses JWT (JSON Web Tokens) for authentication:

- Register a new account at `/register`
- Login at `/login`
- Authentication tokens are automatically managed by the frontend

## API Endpoints

### Authentication
- `POST /api/auth/register/`: Register a new user
- `POST /api/auth/login/`: Login and get JWT tokens
- `POST /api/auth/refresh/`: Refresh JWT token

### File Management
- `POST /api/excel-files/`: Upload a new Excel file
- `GET /api/excel-files/`: List all uploaded files
- `GET /api/excel-files/{id}/`: Get details of a specific file
- `DELETE /api/excel-files/{id}/`: Delete a specific file
- `POST /api/excel-files/{id}/process/`: Process a specific file

### Data Retrieval
- `GET /api/processed-data/`: Get all processed data
- `GET /api/processed-data/by_file/?file_id={id}`: Get processed data for a specific file

## Kafka Integration

Kafka integration is optional and can be enabled by setting the `KAFKA_ENABLED` environment variable to `true`. When enabled, the application will publish processed data to the configured Kafka topic.

```
KAFKA_ENABLED=true
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=excel_data
```

## Admin Interface

Access the Django admin interface at `/admin/` to manage users, files, and data.

## Technologies Used

- **Backend**: Django 4.2.10, Django REST Framework, pandas, kafka-python
- **Frontend**: Vue.js 3, Vuex 4, Vue Router, Bootstrap 5
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **Authentication**: JWT (JSON Web Tokens)
- **Data Processing**: pandas
- **Data Streaming**: Apache Kafka (optional)

## Development

### Running Tests

```bash
# Backend tests
cd data_processor
python manage.py test

# Frontend tests
cd frontend
npm run test
```

### Building for Production

```bash
# Build the frontend
cd frontend
npm run build

# Collect static files for Django
cd data_processor
python manage.py collectstatic
```

## Docker Deployment

The application is fully containerized and can be deployed using Docker Compose.

### Prerequisites

- Docker and Docker Compose installed on your system
- Git repository cloned to your local machine

### Deployment Steps

1. **Build and Start the Containers**

```bash
docker-compose up -d --build
```

This will build and start all services defined in the `docker-compose.yml` file:
- PostgreSQL database
- Zookeeper and Kafka for data streaming
- Kafka UI for monitoring Kafka
- Django backend
- Vue.js frontend

2. **Access the Application**

- Frontend: http://localhost:8081
- Backend API: http://localhost:8000
- Kafka UI: http://localhost:8080
- PostgreSQL: localhost:5432

3. **Create a Superuser in the Running Container**

```bash
docker exec -it agri_backend sh -c "cd backend && python manage_docker.py createsuperuser"
```

4. **View Container Logs**

```bash
# View logs for all containers
docker-compose logs

# View logs for a specific container
docker-compose logs backend
docker-compose logs frontend
```

5. **Stopping the Containers**

```bash
docker-compose down
```

6. **Restarting with Data Persistence**

The PostgreSQL data is persisted in a Docker volume. To restart the application with existing data:

```bash
docker-compose up -d
```

### Environment Configuration

The Docker environment is configured through environment variables in the `docker-compose.yml` file. Key configurations include:

- Database connection details
- Kafka settings
- Debug mode
- Allowed hosts

### Production Considerations

Before deploying to production, consider:

1. Changing default passwords in the `docker-compose.yml` file
2. Setting `DEBUG=0` for the Django backend
3. Configuring proper CORS settings
4. Setting up proper SSL/TLS certificates
5. Implementing a proper backup strategy for the PostgreSQL volume

## License

This project is licensed under the MIT License - see the LICENSE file for details.
