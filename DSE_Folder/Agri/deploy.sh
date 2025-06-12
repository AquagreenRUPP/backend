#!/bin/bash

# AquaGreen Agricultural Platform Deployment Script
# Usage: ./deploy.sh [production|staging|development]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
PROJECT_NAME="agri-platform"

echo -e "${BLUE}🚀 Starting deployment for ${ENVIRONMENT} environment...${NC}"

# Check if Docker and Docker Compose are installed
check_requirements() {
    echo -e "${YELLOW}Checking requirements...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Requirements check passed${NC}"
}

# Generate secure secrets if they don't exist
generate_secrets() {
    echo -e "${YELLOW}Generating secure secrets...${NC}"
    
    # Generate Django secret key
    DJANGO_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || openssl rand -base64 32)
    
    # Generate database password
    DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 24)
    
    # Update .env file
    sed -i "s/your-super-secret-key-for-production-change-this-immediately/$DJANGO_SECRET/g" .env
    sed -i "s/your_secure_password_here/$DB_PASSWORD/g" .env
    
    echo -e "${GREEN}✅ Secrets generated${NC}"
}

# Build and start services
deploy_services() {
    echo -e "${YELLOW}Building and starting services...${NC}"
    
    # Stop existing containers
    docker-compose down --remove-orphans || true
    
    # Build images
    echo -e "${BLUE}Building Docker images...${NC}"
    docker-compose build --no-cache
    
    # Start services
    echo -e "${BLUE}Starting services...${NC}"
    docker-compose up -d
    
    echo -e "${GREEN}✅ Services started${NC}"
}

# Initialize database
init_database() {
    echo -e "${YELLOW}Initializing database...${NC}"
    
    # Wait for database to be ready
    echo -e "${BLUE}Waiting for database to be ready...${NC}"
    sleep 15
    
    # Run migrations
    docker-compose exec -T backend python manage.py migrate
    
    # Create superuser
    docker-compose exec -T backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"
    
    echo -e "${GREEN}✅ Database initialized${NC}"
}

# Health check
health_check() {
    echo -e "${YELLOW}Performing health check...${NC}"
    
    # Wait for services to be ready
    sleep 30
    
    # Check if services are running
    if ! docker-compose ps | grep -q "Up"; then
        echo -e "${RED}❌ Services are not running${NC}"
        docker-compose logs
        exit 1
    fi
    
    echo -e "${GREEN}✅ All services are running${NC}"
}

# Show deployment info
show_info() {
    echo -e "${GREEN}"
    echo "================================="
    echo "🎉 Deployment completed successfully!"
    echo "================================="
    echo ""
    echo "📊 Service URLs:"
    echo "  • Main Application: http://localhost"
    echo "  • Django Admin: http://localhost/admin/"
    echo "  • Backend API: http://localhost/api/"
    echo "  • Frontend: http://localhost:8080/"
    echo ""
    echo "🔐 Default Admin Credentials:"
    echo "  • Username: admin"
    echo "  • Password: admin123"
    echo "  • ⚠️  Change these credentials immediately!"
    echo ""
    echo "📋 Useful Commands:"
    echo "  • View logs: docker-compose logs -f [service]"
    echo "  • Stop services: docker-compose down"
    echo "  • Restart: docker-compose restart [service]"
    echo ""
    echo -e "${NC}"
}

# Main deployment flow
main() {
    echo -e "${BLUE}🌱 AquaGreen Agricultural Platform Deployment${NC}"
    echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
    echo ""
    
    check_requirements
    generate_secrets
    deploy_services
    init_database
    health_check
    show_info
}

# Run main function
main "$@" 