# DroitAI - Enterprise RAG System

A production-ready RAG (Retrieval-Augmented Generation) application with enterprise-grade security, built for Azure with Next.js frontend and FastAPI backend.

## 🏗️ Architecture

DroitAI is a **full-stack enterprise RAG system** with separate frontend and backend services:

### Frontend (Next.js)
- **Framework**: Next.js 15+ with App Router
- **Hosting**: Azure App Service (Node.js 20 LTS)
- **Authentication**: Entra ID SPA registration
- **Features**: Document upload, chat interface, document management

### Backend (FastAPI) 
- **Framework**: FastAPI with async/await
- **Hosting**: Azure App Service (Python 3.11)
- **Authentication**: Entra ID Web API with OBO token flow
- **Features**: RAG processing, document intelligence, AI orchestration

### Azure Services
- **Authentication**: Entra ID with On-Behalf-Of (OBO) flow
- **Search**: Azure AI Search with semantic ranking
- **AI**: Azure OpenAI (GPT-4o) for answer generation
- **Document Processing**: Azure Document Intelligence (F0 tier)
- **Content Safety**: Azure Content Safety (F0 tier)
- **Storage**: Azure Storage with security best practices
- **Monitoring**: Application Insights + Log Analytics
- **Deployment**: Azure Developer CLI (azd) with Bicep

### Security Architecture
- **Separate Identities**: Frontend and backend have dedicated Entra ID registrations
- **OBO Flow**: Frontend exchanges tokens for backend API access
- **Least Privilege**: Managed identities with minimal required permissions
- **HTTPS Only**: All services enforce TLS 1.2+

## 🚀 Quick Start

### Prerequisites
- Azure CLI installed
- Azure Developer CLI (azd) installed
- Access to Azure subscription with Owner permissions

### 1. Clone Repository
```bash
git clone <repository>
cd droitai
```

### 2. Setup Entra ID Applications (Critical)

This creates **separate** Entra ID registrations for frontend and backend:

```bash
# Windows Command Prompt
cd scripts
setup-entra-app.cmd

# Follow the prompts to create both app registrations
# This will generate Client IDs and Secrets for both services
```

### 3. Configure Environment

```bash
# Set backend authentication variables
azd env set ENTRA_APP_CLIENT_ID <backend-client-id>
azd env set ENTRA_APP_CLIENT_SECRET <backend-client-secret>
azd env set ENTRA_APP_TENANT_ID <tenant-id>

# Set frontend authentication variables
azd env set FRONTEND_ENTRA_CLIENT_ID <frontend-client-id>
azd env set FRONTEND_ENTRA_CLIENT_SECRET <frontend-client-secret>
```

### 4. Configure Cross-App Access

**Required for OBO flow to work:**

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Microsoft Entra ID** → **App registrations**
3. Find **DroitAI-RAG-Backend-App**
4. Click **Expose an API** → **Add a client application**
5. Enter the **Frontend Client ID** from Step 2
6. Select authorized scope: `api://<backend-app-id>/access_as_user`

### 5. Deploy to Azure

```bash
# Deploy all infrastructure and both applications
azd up

# Get deployment URLs and environment variables
azd env get-values
```

### 6. Verify Deployment

```bash
# Test backend health
curl https://<backend-app-name>.azurewebsites.net/health

# Test frontend health
curl https://<frontend-app-name>.azurewebsites.net/api/health

# Access the application
# Frontend: https://<frontend-app-name>.azurewebsites.net
# Backend API: https://<backend-app-name>.azurewebsites.net/docs
```

📖 **For detailed deployment instructions**, see [DEPLOYMENT.md](./DEPLOYMENT.md)

## 🔧 Local Development

### Setup Environment
```bash
# Get Azure credentials
azd env get-values > .env.local

# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Development
```bash
docker-compose -f docker-compose.dev.yml up --build
```

## 📁 Project Structure

```
/droitai
├── /frontend (Next.js 15+ App Router)
│   ├── /app
│   │   ├── /api/auth          # Entra ID authentication
│   │   ├── /chat              # Main chat interface
│   │   └── layout.tsx         # Context providers
│   ├── /components
│   │   ├── /chat              # Message components
│   │   └── /governance        # Feature toggles
│   ├── /hooks                 # useChat, useOboToken
│   └── /lib                   # Client utilities

├── /backend (FastAPI)
│   ├── /app
│   │   ├── /api               # API routes (v1/chat, v1/ingest)
│   │   ├── /core              # Security, Config
│   │   ├── /services          # Business logic
│   │   │   ├── search_service.py    # Azure AI Search
│   │   │   ├── openai_service.py    # OpenAI integration
│   │   │   ├── docintel_service.py  # Document Intelligence
│   │   │   └── safety_service.py    # Content Safety
│   │   └── main.py
│   ├── /evaluators            # Responsible AI metrics
│   └── /models                # Pydantic schemas

├── /infra (Infrastructure as Code)
│   ├── main.bicep            # Azure resources orchestration
│   ├── /modules
│   │   ├── host.bicep        # Frontend + backend app services
│   │   ├── frontend.bicep     # Dedicated frontend module
│   │   ├── storage.bicep      # Azure Storage
│   │   ├── search.bicep       # Azure AI Search
│   │   ├── ai-services.bicep  # OpenAI, Document Intelligence
│   │   └── monitoring.bicep   # App Insights, Log Analytics
│   └── azure.yaml            # AZD service configuration

├── /scripts
│   └── setup-entra-app.cmd   # Windows Entra ID setup (both apps)

├── /docs
│   └── DEPLOYMENT.md         # Comprehensive deployment guide

├── azure.yaml                 # AZD configuration
├── docker-compose.dev.yml     # Local development
└── README-AZD.md             # Azure-specific instructions
```

## 🔐 Security Features

### Enterprise Security
- **Separate Identities**: Frontend and backend have dedicated Entra ID registrations
- **OBO Token Flow**: Frontend exchanges tokens for backend API access
- **Least Privilege Access**: Granular role assignments for each service
- **Managed Identity**: No secrets in code, uses Azure AD identities
- **Network Security**: Storage with deny-by-default, HTTPS only
- **Content Safety**: Built-in content filtering and moderation

### Compliance
- **Data Encryption**: All data encrypted at rest and in transit
- **Audit Logging**: Complete audit trail with Application Insights
- **CORS Configuration**: Secure cross-origin resource sharing
- **Token Validation**: Both frontend and backend validate tokens

## 💰 Cost Optimization

- **Free Tiers**: Search (Free), Document Intelligence (F0), Content Safety (F0)
- **Basic Tiers**: App Service (B1), Storage (Standard_LRS)
- **Pay-as-you-go**: OpenAI (S0) with usage-based billing
- **Monitoring**: Free tier for Application Insights and Log Analytics

## 🌟 Key Features

- **Enterprise Authentication**: Entra ID with dual-app OBO flow
- **Full-Stack Architecture**: Separate frontend and backend Azure App Services
- **Document Intelligence**: Support for PDF, Word, images, and more
- **Intelligent Search**: Azure AI Search with semantic capabilities
- **Content Safety**: Built-in moderation and filtering
- **Scalable Architecture**: Microservices with container support
- **Responsible AI**: Evaluation metrics and governance controls
- **Developer Experience**: Full local development with Docker

## 🛠️ Development Workflows

### Infrastructure Changes
```bash
# Preview infrastructure changes
azd provision --preview

# Deploy infrastructure only
azd provision

# Deploy application only
azd deploy
```

### Environment Management
```bash
# List environments
azd env list

# Create new environment
azd env new dev

# Set environment variables
azd env set LOG_LEVEL DEBUG
```

## 📊 Monitoring & Observability

- **Application Insights**: Request tracking, performance monitoring
- **Log Analytics**: Centralized logging and querying
- **Health Checks**: Application health monitoring
- **Error Tracking**: Comprehensive error reporting

## 🌍 Multi-Environment Support

- **Development**: Local Docker with hot reload
- **Staging**: Azure with reduced resources
- **Production**: Azure with full security and monitoring

## 📚 Documentation

- [📋 Deployment Guide](./DEPLOYMENT.md) - Step-by-step deployment instructions
- [🔧 Azure Setup Guide](./README-AZD.md) - Azure Developer CLI specific instructions
- [📖 API Documentation](https://<backend-app-name>.azurewebsites.net/docs) - Interactive API docs
- [🏗️ Architecture Overview](./ARCHITECTURE.md) - System design and security

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `azd up`
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

---

**Built with ❤️ for Azure Innovation Challenge**
