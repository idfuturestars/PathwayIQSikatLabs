#!/bin/bash
# PathwayIQ Docker Build and Deployment Script

set -e

echo "🚀 PathwayIQ Deployment Script Starting..."

# Configuration
IMAGE_NAME="pathwayiq"
IMAGE_TAG="latest"
CONTAINER_NAME="pathwayiq-app"
PORT="8001"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker service."
    exit 1
fi

print_status "Docker is available and running"

# Stop existing container if running
if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
    print_status "Stopping existing container..."
    docker stop $CONTAINER_NAME
fi

# Remove existing container if it exists
if docker ps -a -q -f name=$CONTAINER_NAME | grep -q .; then
    print_status "Removing existing container..."
    docker rm $CONTAINER_NAME
fi

# Build Docker image
print_status "Building Docker image..."
if docker build -t $IMAGE_NAME:$IMAGE_TAG .; then
    print_status "Docker image built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

# Run container
print_status "Starting PathwayIQ container..."
if docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:8001 \
    -e MONGO_URL="${MONGO_URL:-mongodb://host.docker.internal:27017}" \
    -e DB_NAME="${DB_NAME:-pathwayiq_production}" \
    -e JWT_SECRET="${JWT_SECRET:-pathwayiq_production_secret}" \
    -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
    -e CLAUDE_API_KEY="${CLAUDE_API_KEY:-}" \
    -e GEMINI_API_KEY="${GEMINI_API_KEY:-}" \
    --restart unless-stopped \
    $IMAGE_NAME:$IMAGE_TAG; then
    print_status "Container started successfully"
else
    print_error "Container failed to start"
    exit 1
fi

# Wait for container to be ready
print_status "Waiting for application to start..."
sleep 10

# Health check
print_status "Performing health check..."
if curl -f http://localhost:$PORT/api/health &> /dev/null; then
    print_status "✅ PathwayIQ is running successfully!"
    print_status "🌐 Application URL: http://localhost:$PORT"
    print_status "🔍 API Health: http://localhost:$PORT/api/health"
    print_status "📊 Metrics: http://localhost:$PORT/api/metrics"
else
    print_error "Health check failed"
    print_status "Container logs:"
    docker logs $CONTAINER_NAME
    exit 1
fi

# Show container status
print_status "Container Status:"
docker ps -f name=$CONTAINER_NAME

print_status "🎉 PathwayIQ deployment completed successfully!"
print_status "📋 To view logs: docker logs -f $CONTAINER_NAME"
print_status "🛑 To stop: docker stop $CONTAINER_NAME"