#!/bin/bash

# QueryMind Docker Setup
echo "🚀 Starting QueryMind with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start services
echo "📦 Building and starting services..."
docker-compose up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 15

# Check service status
echo "📊 Service Status:"
docker-compose ps

# Show access information
echo ""
echo "✅ QueryMind is ready!"
echo "🌐 Frontend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🐘 Demo DB: localhost:5432 (querymind/querymind123)"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f"