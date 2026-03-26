# Azure Developer CLI (azd) Setup for DroitAI

This guide walks you through deploying the DroitAI **full-stack RAG system** using Azure Developer CLI (azd). The system now consists of separate frontend and backend Azure App Services with dedicated Entra ID authentication.

## Prerequisites

1. **Install Azure Developer CLI**
   ```bash
   # Install azd
   curl -fsSL https://aka.ms/install-azd.sh | bash
   ```

2. **Azure Authentication**
   ```bash
   azd auth login
   ```

3. **Node.js and Python** (for local development)
   - Node.js 18+
   - Python 3.11+

## Quick Deploy

### Prerequisites
1. **Install Azure Developer CLI**
   ```bash
   # Install azd
   curl -fsSL https://aka.ms/install-azd.sh | bash
   ```

2. **Azure Authentication**
   ```bash
   azd auth login
   ```

3. **Node.js and Python** (for local development)
   - Node.js 18+
   - Python 3.11+

4. **Azure Subscription** with Owner permissions

### Step 1: Setup Entra ID Applications

**Critical**: Create separate Entra ID registrations for frontend and backend:

```bash
# Windows Command Prompt
cd scripts
setup-entra-app.cmd

# This creates two app registrations:
# - DroitAI-RAG-Backend-App (API)
# - DroitAI-RAG-Frontend-App (SPA)
```

### Step 2: Configure Environment

```bash
# Set backend authentication variables
azd env set ENTRA_APP_CLIENT_ID <backend-client-id>
azd env set ENTRA_APP_CLIENT_SECRET <backend-client-secret>
azd env set ENTRA_APP_TENANT_ID <tenant-id>

# Set frontend authentication variables
azd env set FRONTEND_ENTRA_CLIENT_ID <frontend-client-id>
azd env set FRONTEND_ENTRA_CLIENT_SECRET <frontend-client-secret>
```

### Step 3: Configure Cross-App Access

**Required for OBO flow:**

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Microsoft Entra ID** → **App registrations**
3. Find **DroitAI-RAG-Backend-App**
4. Click **Expose an API** → **Add a client application**
5. Enter the **Frontend Client ID** from Step 1
6. Select authorized scope: `api://<backend-app-id>/access_as_user`

### Step 4: Deploy

```bash
# Initialize and provision infrastructure
azd init
azd provision

# Deploy both frontend and backend
azd deploy

# Or do everything in one step
azd up
```

## Architecture Overview

The azd template deploys a **full-stack enterprise RAG system** with the following components:

### Azure App Services (Dual Architecture)
- **Frontend App Service**: Next.js 15+ application (Node.js 20 LTS)
- **Backend App Service**: FastAPI Python application (Python 3.11)
- **Separate Identities**: Each service has its own Entra ID registration
- **OBO Flow**: Frontend exchanges tokens for backend API access

### Core Azure Services
- **Azure AI Search** - Enterprise knowledge store with semantic ranking
- **Azure OpenAI** - GPT-4 for answer generation
- **Azure Document Intelligence** - High-fidelity document processing
- **Azure Content Safety** - Regulatory compliance filtering
- **Azure Storage Account** - Document storage with metadata
- **Application Insights** - Dual monitoring (frontend + backend)
- **Log Analytics Workspace** - Centralized logging

### Security Architecture
- **Entra ID Integration**: Dual app registrations for secure token flow
- **Managed Identities**: No secrets in application code
- **Least Privilege**: Granular role-based access control
- **HTTPS Only**: All services enforce TLS 1.2+

### Key Features
- **Azure-First Design**: Only Azure Document Intelligence (no local Docling)
- **Enterprise Security**: Azure AD integration with group-based access
- **Governed Search**: Row-level security with Azure AD groups
- **Scalable Processing**: Cloud-based document ingestion pipeline

## Configuration

### Environment Variables

The following environment variables are automatically configured by azd:

#### Azure Services
```bash
# Azure AI Search
AZURE_SEARCH_ENDPOINT=<endpoint>
AZURE_SEARCH_KEY=<key>
AZURE_SEARCH_INDEX_NAME=droitai-index

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=<endpoint>
AZURE_OPENAI_KEY=<key>
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002

# Azure Document Intelligence
AZURE_DOC_INTELLIGENCE_ENDPOINT=<endpoint>
AZURE_DOC_INTELLIGENCE_KEY=<key>

# Azure Content Safety
AZURE_CONTENT_SAFETY_ENDPOINT=<endpoint>
AZURE_CONTENT_SAFETY_KEY=<key>

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=<connection_string>
AZURE_STORAGE_CONTAINER_NAME=documents
```

#### Authentication (Set in Step 2)
```bash
# Backend Entra ID
ENTRA_APP_CLIENT_ID=<backend-client-id>
ENTRA_APP_CLIENT_SECRET=<backend-client-secret>
ENTRA_APP_TENANT_ID=<tenant-id>

# Frontend Entra ID
FRONTEND_ENTRA_CLIENT_ID=<frontend-client-id>
FRONTEND_ENTRA_CLIENT_SECRET=<frontend-client-secret>

# Application URLs
FRONTEND_URL=https://<frontend-app-name>.azurewebsites.net
BACKEND_URL=https://<backend-app-name>.azurewebsites.net
```

#### Application Settings
```bash
# Features
ENABLE_OBO_FLOW=true
ENABLE_LOCAL_PARSING=false
LOG_LEVEL=INFO
```

## Application Endpoints

After deployment, you'll have access to:

### Frontend Application
- **URL**: `https://<frontend-app-name>.azurewebsites.net`
- **Health Check**: `https://<frontend-app-name>.azurewebsites.net/api/health`
- **Features**: Document upload, chat interface, user management

### Backend API
- **URL**: `https://<backend-app-name>.azurewebsites.net`
- **API Docs**: `https://<backend-app-name>.azurewebsites.net/docs`
- **Health Check**: `https://<backend-app-name>.azurewebsites.net/health`

### API Endpoints

#### Document Ingestion
```bash
# Upload and process files
POST /api/v1/ingestion/upload
Content-Type: multipart/form-data
files: [file1.pdf, file2.docx]
allowed_groups: "healthcare-staff,medical-personnel"

# Get processing status
GET /api/v1/ingestion/status?container_name=documents

# Health check
GET /api/v1/ingestion/health
```

#### Chat and Search
```bash
# Chat with RAG
POST /api/v1/chat
{
  "message": "What are the latest medical guidelines?",
  "conversation_id": "optional-conversation-id"
}

# Governed search
POST /api/v1/search
{
  "query": "medical protocols",
  "top_k": 10
}
```

## Development Workflow

### Local Development
1. **Setup Environment**
   ```bash
   # Get Azure credentials
   azd env get-values > .env.local
   ```

2. **Run Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Run Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Docker Development
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Testing Document Processing
```bash
# Test file upload
curl -X POST "http://localhost:8000/api/v1/ingestion/upload" \
  -F "files=@document.pdf" \
  -F "allowed_groups=test-users"

# Test health check
curl http://localhost:8000/api/v1/ingestion/health
```

## Monitoring and Logging

### Azure Monitor Integration
- **Application Insights**: Request tracking and performance metrics
- **Log Analytics**: Centralized logging
- **Azure Monitor**: Health monitoring and alerts

### Key Metrics
- Document processing latency
- Search query performance
- Azure service health
- User activity and feedback

## Security and Governance

### Azure AD Integration
- **On-Behalf-Of (OBO) Flow**: Enterprise authentication
- **Group-Based Access**: Row-level security in Azure AI Search
- **Audit Trail**: Complete logging in Azure services

### Content Safety
- **Custom Categories**: Regulatory compliance filtering
- **Multi-Stage Filtering**: Pre and post-processing checks
- **Configurable Policies**: Industry-specific content rules

## Scaling and Performance

### Azure-Native Scaling
- **Azure AI Search**: Automatic scaling with semantic ranking
- **Azure App Service**: Auto-scaling based on demand
- **Azure Storage**: Geo-redundant storage options

### Performance Optimization
- **Semantic Caching**: Azure Cache for Redis integration
- **Batch Processing**: Efficient document ingestion
- **Parallel Processing**: Multi-threaded document processing

## Troubleshooting

### Common Deployment Issues

1. **Entra ID Configuration Errors**
   ```bash
   # Verify app registrations exist
   az ad app list --display-name "DroitAI-RAG-Backend-App"
   az ad app list --display-name "DroitAI-RAG-Frontend-App"
   ```

2. **Cross-App Access Issues**
   - Ensure Step 3 (Configure Cross-App Access) was completed
   - Verify frontend Client ID is in backend's "Authorized client applications"

3. **Build Failures**
   ```bash
   # Check deployment logs
   azd logs

   # Redeploy specific service
   azd deploy --service frontend
   azd deploy --service app
   ```

### Common Runtime Issues

1. **Authentication Failures**
   ```bash
   # Check environment variables
   azd env get-values
   
   # Verify redirect URIs match
   # Frontend: http://localhost:3000/auth/callback (dev)
   # Frontend: https://<frontend-url>/auth/callback (prod)
   ```

2. **Backend API Not Accessible**
   ```bash
   # Test backend health
   curl https://<backend-app-name>.azurewebsites.net/health
   
   # Check backend logs
   azd logs --service app
   ```

3. **Frontend Build Issues**
   ```bash
   # Test frontend health
   curl https://<frontend-app-name>.azurewebsites.net/api/health
   
   # Check frontend logs
   azd logs --service frontend
   ```

## Next Steps

1. **Test Authentication Flow**
   - Navigate to frontend URL
   - Complete Entra ID login
   - Verify API calls work

2. **Upload Test Documents**
   - Use the document upload feature
   - Verify processing in Azure Storage

3. **Test RAG Functionality**
   - Ask questions about uploaded documents
   - Verify responses include citations

4. **Configure Production Settings**
   - Update redirect URIs for production domain
   - Set up custom domains if needed
   - Configure backup and disaster recovery

5. **Monitor Performance**
   - Set up Azure Monitor alerts
   - Review Application Insights metrics
   - Configure Log Analytics queries

## Support

- **Azure Documentation**: https://docs.microsoft.com/azure/
- **Azure Developer CLI**: https://learn.microsoft.com/azure/developer/azure-developer-cli/
- **Issues**: Create GitHub issues for bugs and feature requests
