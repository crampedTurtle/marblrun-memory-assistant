# MarblRun - Local Memory Assistant

A local memory assistant application similar to Marblism, built with FastAPI, PostgreSQL, Qdrant vector database, and Next.js. Store your thoughts, memories, and notes with semantic search capabilities powered by OpenAI embeddings.

## 🚀 Features

- **Note Management**: Create, view, and delete notes with optional titles
- **Semantic Search**: Search through your memories using natural language queries
- **Vector Storage**: Fast similarity search using Qdrant vector database
- **Modern UI**: Clean, responsive interface built with Next.js and Tailwind CSS
- **Real-time Search**: Instant search results with similarity scores
- **Timeline View**: Chronological view of all your notes
- **Search Suggestions**: AI-powered search suggestions based on recent notes

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Primary database for storing note metadata
- **Qdrant**: Vector database for semantic search
- **OpenAI API**: Text embeddings and semantic understanding
- **SQLAlchemy**: Database ORM and migrations

### Frontend (Next.js)
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **Axios**: HTTP client for API communication

## 📋 Prerequisites

- Docker and Docker Compose
- PostgreSQL database (accessible at `postgres.home.lan:5432`)
- OpenAI API key
- Node.js 18+ (for local development)

## 🛠️ Setup Instructions

### 1. Environment Configuration

Create a `.env` file in the root directory:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration (adjust if needed)
DATABASE_URL=postgresql://postgres:postgres@postgres.home.lan:5432/marblrun

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=memories

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Database Setup

Ensure your PostgreSQL database is running and accessible. The application will automatically create the required tables on first startup.

### 3. Launch the Application

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## 🔧 Development

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## 📚 API Endpoints

### Notes
- `POST /api/notes` - Create a new note
- `GET /api/notes` - Get all notes (with pagination)
- `GET /api/notes/{note_id}` - Get a specific note
- `DELETE /api/notes/{note_id}` - Delete a note
- `GET /api/notes/stats` - Get system statistics

### Search
- `POST /api/query` - Search memories semantically
- `GET /api/query/similar/{note_id}` - Find similar notes
- `GET /api/query/suggestions` - Get search suggestions

## 🗄️ Database Schema

### Notes Table
```sql
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    title VARCHAR(255),
    vector_id VARCHAR(255) UNIQUE NOT NULL,
    embedding_model VARCHAR(100) DEFAULT 'text-embedding-ada-002',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## 🔍 How It Works

1. **Note Creation**: When you create a note, the content is sent to OpenAI to generate embeddings
2. **Vector Storage**: The embedding is stored in Qdrant with metadata
3. **Metadata Storage**: Note details are stored in PostgreSQL
4. **Semantic Search**: When you search, your query is embedded and compared against stored vectors
5. **Results**: Similar notes are retrieved and ranked by similarity score

## 🎨 UI Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Mode Ready**: CSS variables for easy theming
- **Loading States**: Smooth loading indicators
- **Error Handling**: User-friendly error messages
- **Keyboard Navigation**: Full keyboard accessibility
- **Search Suggestions**: AI-powered search recommendations

## 🔒 Security Considerations

- No authentication implemented (as requested)
- API endpoints are publicly accessible
- Consider adding authentication for production use
- OpenAI API key should be kept secure

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Use proper environment management
2. **Database**: Use managed PostgreSQL service
3. **Vector Database**: Consider Qdrant Cloud for production
4. **API Keys**: Secure OpenAI API key management
5. **SSL/TLS**: Enable HTTPS for production
6. **Monitoring**: Add logging and monitoring
7. **Backup**: Regular database backups

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection**: Ensure PostgreSQL is accessible
2. **OpenAI API**: Verify API key is valid and has credits
3. **Qdrant**: Check if vector database is running
4. **Port Conflicts**: Ensure ports 3000, 8000, and 6333 are available

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs qdrant
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Check the logs for error messages
4. Open an issue on GitHub 