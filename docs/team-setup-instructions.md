# Team Setup Instructions

## Quick Start for Team Members (Sue, Sushma, Aruselvi)

### 🚀 One-Command Setup
```bash
# Clone and setup
git clone <repository-url>
cd sentinel-rag
cp .env.example .env
# Fill in your Azure credentials in .env

# Start everything
docker-compose up --build
```

### 📋 Environment Variables Checklist

Each team member needs to configure these Azure values in their `.env` file:

#### **Required for All Team Members**
```bash
# Azure AD (Get from your Azure Admin)
AZURE_TENANT_ID=your-tenant-id

# Azure AI Search (Create in Azure Portal)
AZURE_SEARCH_ENDPOINT=https://your-team-search.search.windows.net
AZURE_SEARCH_KEY=your-search-admin-key

# Azure OpenAI (Create in Azure Portal)
AZURE_OPENAI_ENDPOINT=https://your-team-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-openai-api-key
```

#### **For OBO Flow Testing**
```bash
# Frontend App Registration
AZURE_AD_CLIENT_ID=frontend-app-client-id
AZURE_AD_CLIENT_SECRET=frontend-app-secret

# Backend App Registration  
AZURE_CLIENT_ID=backend-app-client-id
AZURE_CLIENT_SECRET=backend-app-secret
```

#### **Optional Services**
```bash
# Document Intelligence (for advanced parsing)
AZURE_DOC_INTELLIGENCE_ENDPOINT=https://your-doc-intelligence.cognitiveservices.azure.com/
AZURE_DOC_INTELLIGENCE_KEY=your-doc-intelligence-key

# Content Safety (for Responsible AI)
AZURE_CONTENT_SAFETY_ENDPOINT=https://your-content-safety.cognitiveservices.azure.com/
AZURE_CONTENT_SAFETY_KEY=your-content-safety-key
```

### 🔧 Development Options

#### **Option 1: Full Docker Stack (Recommended)**
```bash
# Everything including Cosmos DB emulator
docker-compose -f docker-compose.yml -f docker-compose.cosmos.yml up --build

# With local parsing enabled
ENABLE_LOCAL_PARSING=true docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

#### **Option 2: Local Development**
```bash
# Frontend (Terminal 1)
cd frontend
npm install
npm run dev

# Backend (Terminal 2)  
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Redis (Terminal 3)
docker run -p 6379:6379 redis:7-alpine
```

### 📁 Project Structure Overview
```
sentinel-rag/
├── frontend/          # Next.js app (port 3000)
├── backend/           # FastAPI app (port 8000)  
├── data/             # Local documents for testing
├── infra/            # Infrastructure as Code
├── docs/             # Setup guides
└── docker-compose.yml # Full stack setup
```

### 🧪 Testing the Setup

#### **1. Test Frontend**
```bash
curl http://localhost:3000
# Should return Next.js page
```

#### **2. Test Backend**
```bash
curl http://localhost:8000/health
# Should return {"status": "healthy"}
```

#### **3. Test OBO Flow**
1. Open http://localhost:3000
2. Click "Sign in with Azure AD"
3. After login, try sending a chat message
4. Check browser network tab for successful API calls

#### **4. Test Local Parsing**
```bash
# Add a PDF to data/raw/
echo "ENABLE_LOCAL_PARSING=true" >> .env
docker-compose restart backend
# Try uploading the PDF in the UI
```

### 🎯 Feature Toggles

Use these to test different configurations:

```bash
# Enable local document parsing
ENABLE_LOCAL_PARSING=true

# Disable Azure Document Intelligence  
ENABLE_AZURE_DOC_INTELLIGENCE=false

# Enable detailed logging
ENABLE_DETAILED_LOGGING=true

# Use Cosmos DB emulator
COSMOS_DB_EMULATOR=true
```

### 🐛 Common Issues & Solutions

#### **Port Conflicts**
```bash
# Kill processes on ports 3000/8000
netstat -tulpn | grep :3000
sudo kill -9 <PID>
```

#### **Azure AD Issues**
- Check that redirect URIs match exactly
- Verify API permissions are granted
- Ensure both frontend and backend apps are registered

#### **Docker Issues**
```bash
# Clean rebuild
docker-compose down -v
docker system prune -f
docker-compose up --build
```

### 📞 Team Communication

#### **Daily Standup Updates**
- What Azure services are working/not working
- Any OBO flow authentication issues
- Local parsing vs Azure parsing results
- Docker/container issues

#### **Shared Resources**
- Azure resource names and endpoints
- App registration client IDs (not secrets!)
- Working document samples for testing
- Performance benchmarks

### 🎨 Innovation Challenge Tips

#### **For High Scores:**
1. **Responsible AI**: Enable content safety filters
2. **Innovation**: Test both local and Azure parsing
3. **Enterprise Ready**: Use OBO flow properly
4. **Governance**: Document your feature toggles
5. **Performance**: Measure response times

#### **Demo Preparation:**
```bash
# Prepare demo data
mkdir -p data/raw
# Add WHO SOPs, contracts, etc.

# Test all features
ENABLE_LOCAL_PARSING=true docker-compose up
ENABLE_LOCAL_PARSING=false docker-compose up

# Check logs
docker-compose logs -f backend
```

### 📚 Documentation Links
- [Azure AD OBO Flow Guide](./azure-ad-setup.md)
- [Docker Configuration](../docker-compose.yml)
- [Project README](../README.md)

---

**Need help?** Message the team channel with:
1. Error message (full text)
2. What you were trying to do
3. Your .env values (without secrets)
