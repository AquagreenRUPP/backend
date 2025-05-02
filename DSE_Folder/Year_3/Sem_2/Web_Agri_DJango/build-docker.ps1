Write-Host "Building and starting Docker containers one by one..." -ForegroundColor Green

# Create network if it doesn't exist
Write-Host "Creating network..." -ForegroundColor Cyan
docker network create agri_network 2>$null

# PostgreSQL
Write-Host "Building and starting PostgreSQL..." -ForegroundColor Cyan
docker-compose up -d --build postgres
Write-Host "Waiting for PostgreSQL to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Zookeeper
Write-Host "Building and starting Zookeeper..." -ForegroundColor Cyan
docker-compose up -d --build zookeeper
Write-Host "Waiting for Zookeeper to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Kafka
Write-Host "Building and starting Kafka..." -ForegroundColor Cyan
docker-compose up -d --build kafka
Write-Host "Waiting for Kafka to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Kafka UI
Write-Host "Building and starting Kafka UI..." -ForegroundColor Cyan
docker-compose up -d --build kafka-ui
Write-Host "Waiting for Kafka UI to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Backend
Write-Host "Building and starting Django Backend..." -ForegroundColor Cyan
docker-compose up -d --build backend
Write-Host "Waiting for Django Backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Frontend
Write-Host "Building and starting Vue.js Frontend..." -ForegroundColor Cyan
docker-compose up -d --build frontend

Write-Host "All containers have been built and started!" -ForegroundColor Green
Write-Host "You can access the applications at:" -ForegroundColor Green
Write-Host "- Frontend: http://localhost:8081" -ForegroundColor Cyan
Write-Host "- Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "- Kafka UI: http://localhost:8080" -ForegroundColor Cyan
