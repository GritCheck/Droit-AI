# Azure Developer CLI (azd) Setup for DroitAI

This guide walks you through deploying DroitAI system using Azure Developer CLI (azd) with Azure Document Intelligence as exclusive document processing service.

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

1. **Initialize and Provision**
   ```bash
   cd droitai
   azd init
   azd provision
   ```

2. **Deploy Services**
   ```bash
   azd deploy
   ```

## Architecture Overview

The azd template deploys the following Azure services:

### Core Azure Services
- **Azure AI Search** - Enterprise knowledge store with semantic ranking
- **Azure OpenAI** - GPT-4 for answer generation
- **Azure Document Intelligence** - High-fidelity document processing (exclusive)
- **Azure Content Safety** - Regulatory compliance filtering
- **Azure Storage Account** - Document storage with metadata
- **Azure App Service** - Backend API hosting
- **Azure Static Web App** - Frontend hosting
- **Azure Monitor & Application Insights** - Monitoring and logging

### Key Features
- **Azure-First Design**: Only Azure Document Intelligence (no local Docling)
- **Enterprise Security**: Azure AD integration with group-based access
- **Governed Search**: Row-level security with Azure AD groups
- **Scalable Processing**: Cloud-based document ingestion pipeline

## Configuration

### Environment Variables
The following environment variables are automatically configured by azd:

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

# Azure AD
AZURE_AD_TENANT_ID=<tenant_id>
AZURE_AD_CLIENT_ID=<client_id>
AZURE_AD_CLIENT_SECRET=<client_secret>
```

## Document Processing Pipeline

### Azure Document Intelligence Only
The system now exclusively uses Azure Document Intelligence for document processing:

1. **Upload** → Documents uploaded to Azure Storage
2. **Process** → Azure Document Intelligence extracts content and metadata
3. **Chunk** → Intelligent chunking with layout awareness
4. **Index** → Chunks indexed in Azure AI Search with security metadata
5. **Search** → Governed search with Azure AD group filtering

### Supported Formats
- PDF, DOCX, DOC
- Images: JPG, PNG, BMP, TIFF
- HTML, TXT
- And more via Azure Document Intelligence models

## API Endpoints

### Document Ingestion
```bash
# Process folder
POST /api/v1/ingestion/folder
{
  "folder_path": "/path/to/documents",
  "allowed_groups": ["healthcare-staff", "medical-personnel"],
  "container_name": "documents"
}

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

### Chat and Search
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
   cp .env.example .env
   # Fill in your Azure credentials
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

### Testing Document Processing
```bash
# Test folder processing
curl -X POST "http://localhost:8000/api/v1/ingestion/folder" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "./data/raw",
    "allowed_groups": ["test-users"]
  }'

# Test file upload
curl -X POST "http://localhost:8000/api/v1/ingestion/upload" \
  -F "files=@document.pdf" \
  -F "allowed_groups=test-users"
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

### Common Issues

1. **Azure Document Intelligence Not Configured**
   ```bash
   # Check health endpoint
   curl http://localhost:8000/api/v1/ingestion/health
   ```

2. **Storage Access Issues**
   ```bash
   # Verify storage connection
   az storage account show-connection-string --name <account-name>
   ```

3. **Search Index Issues**
   ```bash
   # Check search service
   az search service show --name <search-name> --resource-group <rg-name>
   ```

### Logs and Monitoring
```bash
# View application logs
azd logs --app backend

# Monitor Azure services
az monitor metrics list --resource <resource-id>
```

## Next Steps

1. **Customize Models**: Configure Azure OpenAI deployments
2. **Set Up Azure AD**: Configure enterprise authentication
3. **Define Access Groups**: Set up Azure AD groups for document access
4. **Configure Content Safety**: Set up custom regulatory categories
5. **Monitor Performance**: Set up Azure Monitor alerts

## Support

- **Azure Documentation**: https://docs.microsoft.com/azure/
- **Azure Developer CLI**: https://learn.microsoft.com/azure/developer/azure-developer-cli/
- **Issues**: Create GitHub issues for bugs and feature requests
