# DroitAI - Enterprise RAG System

A production-ready RAG (Retrieval-Augmented Generation) application with enterprise-grade security, built for Azure with Next.js frontend and FastAPI backend.

## 🏗️ Architecture

- **Frontend**: Next.js 15+ with App Router
- **Backend**: FastAPI with async/await
- **Authentication**: Entra ID with OBO token flow
- **Search**: Azure AI Search (S2 and above to support Semantic Reranker, Vector Search and True Vecotr Search)
- **AI**: Azure OpenAI (GPT-4o)
- **Document Processing**: Azure Document Intelligence (F0 tier)
- **Content Safety**: Azure Content Safety (F0 tier)
- **Storage**: Azure Storage with security best practices
- **Monitoring**: Application Insights + Log Analytics
- **Deployment**: Azure Developer CLI (azd) with Bicep

## 🚀 Quick Start

### Prerequisites
- Azure CLI installed
- Azure Developer CLI (azd) installed
- Access to Azure subscription

### 1. Clone Repository
```bash
git clone <repository>
cd droitai
```

### 2. Setup Entra ID (Required)
```bash
# Windows Command Prompt
cd scripts
setup-entra-app.cmd

# Linux/Mac Bash
cd scripts
./setup-entra-app.sh
```

### 3. Deploy to Azure
```bash
# Deploy all infrastructure and applications
azd up

# Get environment variables for local development
azd env get-values
```

### 4. Access the Application
- Frontend: `https://<app-name>.azurewebsites.net`
- Backend API: `https://<app-name>-app.azurewebsites.net`
- API Docs: `https://<app-name>-app.azurewebsites.net/docs`

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
│   ├── main.bicep            # Azure resources with security
│   └── azure.yaml            # AZD configuration

├── /scripts
│   ├── setup-entra-app.ps1   # Windows Entra ID setup
│   └── setup-entra-app.sh    # Linux/Mac Entra ID setup

├── /docs
│   └── entra-id-setup.md     # Detailed setup guide

└── docker-compose.dev.yml    # Local development
```

## 🔐 Security Features

### Enterprise Security
- **Least Privilege Access**: Granular role assignments for each service
- **Managed Identity**: No secrets in code, uses Azure AD identities
- **Network Security**: Storage with deny-by-default, HTTPS only
- **OBO Token Flow**: Secure user delegation across services
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

- **Enterprise Authentication**: Entra ID with single app setup
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

- [Entra ID Setup Guide](docs/entra-id-setup.md)
- [API Documentation](https://<app-name>-app.azurewebsites.net/docs)
- [Architecture Overview](docs/architecture.md)

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
