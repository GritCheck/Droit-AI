# Sentinel RAG - Innovation Challenge

A production-ready RAG (Retrieval-Augmented Generation) application with Next.js frontend and FastAPI backend, designed for the Innovation Challenge.

## Architecture

- **Frontend**: Next.js 15+ with App Router
- **Backend**: FastAPI with async/await
- **Authentication**: Azure AD via Auth.js/NextAuth
- **Search**: Azure AI Search
- **AI**: Azure OpenAI
- **Document Processing**: Azure Document Intelligence (with local fallback)
- **History**: Browser storage (with CosmosDB option)
- **Governance**: Responsible AI metrics and evaluation

## Project Structure

```
/droitai
├── /frontend (Next.js 15+ App Router)
│   ├── /app
│   │   ├── /api/auth          # Auth.js / NextAuth config for Azure AD
│   │   ├── /chat              # Main chat interface
│   │   └── layout.tsx         # Context providers (Auth, Theme, Config)
│   ├── /components
│   │   ├── /chat              # Message list, Citation bubbles
│   │   └── /governance        # Toggle switches for (Local vs Azure, etc.)
│   ├── /hooks                 # useChat, useOboToken
│   └── /lib                   # LocalStorage / IndexedDB persistence logic
│
├── /backend (FastAPI)
│   ├── /app
│   │   ├── /api               # Route handlers (v1/chat, v1/ingest)
│   │   ├── /core              # Security (OBO flow), Config (pydantic settings)
│   │   ├── /services          # Business logic
│   │   │   ├── search_service.py  # Azure AI Search logic
│   │   │   ├── parser_service.py  # Local (Docling) vs. Azure Doc Intelligence
│   │   │   └── history_service.py # Browser (None) vs. CosmosDB logic
│   │   └── main.py
│   ├── /evaluators            # Responsible AI Toolbox & custom metrics
│   └── /models                # Pydantic schemas for Request/Response
│
├── /data
│   ├── /raw                   # WHO SOPs, Stanford Contracts (for local testing)
│   └── /processed             # JSON metadata/embeddings (if local parsing used)
│
├── /infra (Infrastructure as Code)
│   ├── bicep/terraform        # To show "Deployment Automation" (Bonus Points!)
│   └── Dockerfile             # Multi-stage build for Backend
│
├── .env.example               # Template for Azure Client IDs/Secrets
└── docker-compose.yml         # To run Next.js + FastAPI + Local Redis/DB
```

## Quick Start

1. **Clone and setup**
   ```bash
   git clone <repository>
   cd droitai
   cp .env.example .env
   # Fill in your Azure credentials in .env
   ```

2. **Run with Docker**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Development

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Key Features

- **Hybrid Processing**: Switch between Azure Document Intelligence and local Docling parsing
- **Flexible Storage**: Browser storage for development, CosmosDB for production
- **Governance Controls**: Toggle between local and Azure services
- **Responsible AI**: Built-in evaluation metrics and content filtering
- **Enterprise Auth**: Azure AD integration with OBO token flow
- **Scalable Architecture**: Microservices design with Docker support

## Innovation Challenge Highlights

- **Production-Ready Structure**: Organized for scalability and maintainability
- **Deployment Automation**: Infrastructure as Code with Bicep/Terraform
- **Multi-Modal Processing**: Support for various document formats
- **Responsible AI**: Evaluation framework and governance controls
- **Cloud-Native**: Designed for Azure with local development fallbacks

## License

MIT License - see LICENSE file for details
