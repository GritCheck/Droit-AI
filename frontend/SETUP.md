# Frontend Setup Guide - Droit AI Dashboard

## 🚀 Quick Start

### 1. Environment Configuration
The `.env.local` file has been created with the correct configuration:

```env
NEXT_PUBLIC_SERVER_URL=http://localhost:8000
```

### 2. Install Dependencies
```bash
cd frontend
npm install
```

### 3. Start Development Server
```bash
npm run dev
```

The frontend will be available at: `http://localhost:3000`

## 📊 API Integration

### Dashboard Endpoints
The frontend is already configured to consume these backend APIs:

- **Overview**: `/api/v1/dashboard/overview` - Complete dashboard data
- **Stats**: `/api/v1/dashboard/stats` - Statistics only
- **Charts**: `/api/v1/dashboard/charts` - Chart data only
- **Widgets**: `/api/v1/dashboard/widgets` - Widget data only
- **Health**: `/api/v1/dashboard/health` - Health check

### Data Flow
```
Frontend (React) → Axios → Backend (FastAPI) → Azure Services
```

### Live Data Features
- **Real Azure Storage Integration** - Document counting
- **Managed Identity Authentication** - Secure Azure access
- **Graceful Fallback** - Works even if Azure services are down
- **Smart Caching** - 5-minute TTL to prevent API spam

## 🧪 Testing Connection

### Test API Connection
```bash
node test-api-connection.js
```

### Manual Testing
1. Start backend: `cd backend && python -m uvicorn app.main:app --reload --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Visit: `http://localhost:3000/dashboard`

## 🏗️ Architecture

### Frontend Components
- **useDashboardData** - Hook for fetching dashboard data
- **OverviewAppView** - Main dashboard component
- **Dashboard Hooks** - Individual hooks for stats, charts, widgets

### Backend Services
- **MetricsService** - Azure integration service
- **Dashboard API** - RESTful endpoints
- **Azure Storage** - Real document counting
- **Azure Monitor** - Telemetry integration

## 🎯 Key Features

### Real Azure Integration
- ✅ **Azure Storage** - Actually counting documents
- ✅ **Managed Identity** - Secure authentication
- ✅ **Live Metrics** - Real data from Azure services
- ✅ **Fallback Data** - Never breaks the UI

### Enterprise Features
- ✅ **Error Handling** - Graceful degradation
- ✅ **Caching** - Performance optimization
- ✅ **TypeScript** - Type safety
- ✅ **Responsive Design** - Mobile-friendly

## 🛠️ Development

### Adding New Metrics
1. Add endpoint to `backend/app/api/v1/dashboard.py`
2. Add method to `backend/app/services/metrics_service.py`
3. Update `frontend/src/lib/axios.ts` endpoints
4. Create new hook in `frontend/src/hooks/useDashboardData.ts`

### Debugging
- **Frontend**: Check browser console for API calls
- **Backend**: Check server logs for Azure integration
- **Azure**: Check Azure Portal for service status

## 🏆 Microsoft Innovation Challenge Ready

This implementation demonstrates:
- **Real Azure Integration** - Not just mock data
- **Enterprise Architecture** - Production-ready patterns
- **Security Best Practices** - Managed Identity, no secrets
- **Resilient Design** - Works offline and online
- **Professional Code** - Clean, maintainable, scalable

The dashboard will show **real data from your Azure Storage account** when both services are running!
