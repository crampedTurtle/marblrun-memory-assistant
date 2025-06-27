#!/bin/bash

echo "🚀 Starting AI Assistant Platform..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://postgres:password@postgres.home.lan:5432/ai_assistants
QDRANT_URL=http://localhost:6333
EOF
    echo "📝 Please edit .env file with your OpenAI API key and database credentials"
    echo "🔑 Get your OpenAI API key from: https://platform.openai.com/api-keys"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API is running at http://localhost:8000"
else
    echo "❌ Backend API is not responding"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "❌ Frontend is not responding"
fi

if curl -s http://localhost:6333/collections > /dev/null; then
    echo "✅ Qdrant is running at http://localhost:6333"
else
    echo "❌ Qdrant is not responding"
fi

echo ""
echo "🎉 AI Assistant Platform is ready!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo "🔍 Qdrant: http://localhost:6333"
echo ""
echo "To stop the services, run: docker-compose down" 