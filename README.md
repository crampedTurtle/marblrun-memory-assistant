# AI Assistant Platform

A full-stack AI-powered assistant platform inspired by Marblism, featuring multiple AI agents with unique personalities and specialized capabilities.

## 🚀 Features

- **Multiple AI Agents**: Choose from Cara (Customer Support), Penny (SEO Writer), and Eva (Executive Assistant)
- **Persistent Memory**: Each agent maintains their own vector-based memory using Qdrant
- **Real-time Chat**: Interactive chat interface with typing indicators and message history
- **Semantic Search**: Search through agent memories and conversations
- **Modern UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS
- **Docker Deployment**: Easy containerized deployment with Docker Compose

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: High-performance Python web framework
- **PostgreSQL**: Relational database for structured data
- **Qdrant**: Vector database for semantic search and memory
- **OpenAI API**: Embeddings and LLM for AI capabilities

### Frontend Stack
- **Next.js 14**: React framework with App Router
- **Tailwind CSS**: Utility-first CSS framework
- **TypeScript**: Type-safe JavaScript
- **Axios**: HTTP client for API communication

### Infrastructure
- **Docker Compose**: Container orchestration
- **Qdrant**: Vector similarity search
- **PostgreSQL**: External database (assumes `postgres.home.lan:5432`)

## 🛠️ Setup

### Prerequisites
- Docker and Docker Compose
- PostgreSQL database running at `postgres.home.lan:5432`
- OpenAI API key

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-assistant-platform
```

### 2. Environment Setup
Create a `.env` file in the root directory:
```bash
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://postgres:password@postgres.home.lan:5432/ai_assistants
QDRANT_URL=http://localhost:6333
```

### 3. Database Setup
Create the database in your PostgreSQL instance:
```sql
CREATE DATABASE ai_assistants;
```

### 4. Launch the Application
```bash
docker-compose up --build
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Qdrant**: http://localhost:6333

## 📚 API Documentation

### Agents Endpoints

#### List All Agents
```http
GET /api/agents
```

#### Chat with Agent
```http
POST /api/agent/{agent_name}/chat
Content-Type: application/json

{
  "message": "Hello, how can you help me?",
  "context": "Optional conversation context"
}
```

#### Store Note
```http
POST /api/agent/{agent_name}/note
Content-Type: application/json

{
  "content": "Important information to remember",
  "metadata": {
    "category": "meeting",
    "priority": "high"
  }
}
```

#### Search Agent Memory
```http
GET /api/agent/{agent_name}/search?q=search_query&limit=10
```

### Available Agents

#### Cara - Customer Support Specialist
- **Personality**: Empathetic, patient, solution-oriented
- **Expertise**: Customer service, problem resolution, communication
- **Use Cases**: Customer inquiries, support tickets, feedback handling

#### Penny - SEO Content Strategist
- **Personality**: Witty, creative, data-driven
- **Expertise**: SEO, content strategy, copywriting, social media
- **Use Cases**: Blog writing, content planning, SEO optimization

#### Eva - Executive Assistant
- **Personality**: Organized, efficient, detail-oriented
- **Expertise**: Scheduling, project management, communication coordination
- **Use Cases**: Calendar management, meeting preparation, task tracking

## 🎨 UI Components

### Agent Selection Grid
- Pop-art style cards with gradient backgrounds
- Hover animations and smooth transitions
- Agent-specific icons and color schemes

### Chat Interface
- Real-time message exchange
- Typing indicators
- Message timestamps
- Responsive design for mobile and desktop

### Search Functionality
- Semantic search through agent memories
- Relevance scoring
- Source attribution (conversation vs note)

## 🔧 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Adding New Agents
1. Create agent class in `backend/app/agents/`
2. Add system prompt in `backend/prompts/`
3. Register agent in `backend/app/routers/agents.py`
4. Add UI configuration in `frontend/components/AgentGrid.tsx`

## 🚀 Deployment

### Production Deployment
1. Set environment variables for production
2. Build and push Docker images
3. Deploy with Docker Compose or Kubernetes
4. Configure reverse proxy (NGINX) for SSL termination

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: PostgreSQL connection string
- `QDRANT_URL`: Qdrant service URL
- `NEXT_PUBLIC_API_URL`: Frontend API endpoint

## 🔮 Future Enhancements

### Planned Integrations
- **n8n Workflow Automation**: Connect agents to automated workflows
- **Zoho Mail Integration**: Email ingestion for Cara and Eva
- **Cal.com Scheduling**: Calendar integration for Eva
- **File Upload**: Document processing and analysis
- **Multi-user Support**: User authentication and permissions

### Advanced Features
- **Agent Collaboration**: Agents working together on complex tasks
- **Custom Agent Creation**: User-defined agent personalities
- **Analytics Dashboard**: Usage statistics and performance metrics
- **API Rate Limiting**: Protect against abuse
- **Webhook Support**: Real-time notifications and integrations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at http://localhost:8000/docs
- Review the Qdrant documentation for vector search features 