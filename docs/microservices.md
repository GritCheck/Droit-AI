# Microservices Design

This document outlines the microservices architecture for the Droit AI RAG system, detailing service boundaries, communication patterns, and implementation details.

## Architecture Overview

The Droit AI system follows a microservices architecture with three primary services:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                Application Gateway                              │
│                           (SSL Termination, WAF)                                │
└─────────────────────┬───────────────────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌────▼────┐ ┌─────▼─────┐
│   Frontend    │ │ Backend │ │ AI Service │
│   Service     │ │ Service │ │ Functions  │
│   (React)     │ │(FastAPI)│ │ (Python)   │
│ Port: 3000    │ │Port:8000│ │ HTTP/Queue │
└───────────────┘ └─────────┘ └────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
        ┌─────────────▼─────────────┐
        │      Shared Services       │
        │  ┌─────────┐ ┌─────────────┐│
        │  │Storage  │ │   Search    ││
        │  │Account  │ │  Service    ││
        │  └─────────┘ └─────────────┘│
        │  ┌─────────┐ ┌─────────────┐│
        │  │Key Vault│ │ Cognitive   ││
        │  └─────────┘ │  Services   ││
        │              └─────────────┘│
        └─────────────────────────────┘
```

## Service Boundaries

### 1. Frontend Service (React)

**Responsibilities:**
- User interface and experience
- Client-side authentication state management
- API communication with backend
- File upload and preview
- Real-time updates via WebSockets

**Technology Stack:**
- React 18 with TypeScript
- Next.js 14 (App Router)
- Material-UI (MUI) components
- Zustand for state management
- Axios for HTTP client

**Key Features:**
- Server-side rendering (SSR)
- Progressive Web App (PWA) capabilities
- Responsive design
- Accessibility compliance

### 2. Backend Service (FastAPI)

**Responsibilities:**
- Authentication and authorization
- API orchestration
- Business logic implementation
- Document metadata management
- User session management

**Technology Stack:**
- FastAPI with Python 3.11
- SQLAlchemy with Azure SQL
- Redis for caching
- Azure SDK integrations
- Pydantic for data validation

**Key Features:**
- OpenAPI documentation
- Async request handling
- Background task processing
- Comprehensive error handling

### 3. AI Service Functions (Serverless)

**Responsibilities:**
- Document processing and analysis
- Vector embeddings generation
- Content safety filtering
- Semantic search processing
- Legal clause analysis

**Technology Stack:**
- Azure Functions (Python)
- OpenAI API integration
- Azure Document Intelligence
- Azure Content Safety
- NumPy/Pandas for data processing

**Key Features:**
- Event-driven processing
- Scalable compute
- Cost-effective execution
- Parallel processing capabilities

## Service Communication Patterns

### 1. Synchronous Communication

#### Frontend ↔ Backend
```typescript
// Frontend API client
class BackendAPI {
  private baseURL: string;
  
  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }
  
  async getContracts(): Promise<Contract[]> {
    const response = await fetch(`${this.baseURL}/api/v1/contracts`, {
      headers: {
        'Authorization': `Bearer ${this.getAuthToken()}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }
  
  async uploadContract(file: File): Promise<Contract> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${this.baseURL}/api/v1/contracts/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.getAuthToken()}`
      },
      body: formData
    });
    
    return response.json();
  }
  
  private getAuthToken(): string {
    return localStorage.getItem('azure_access_token') || '';
  }
}
```

#### Backend ↔ AI Services
```python
# Backend AI service client
class AIServiceClient:
    def __init__(self):
        self.base_url = os.getenv('AI_FUNCTIONS_URL')
        self.credential = DefaultAzureCredential()
    
    async def process_document(self, document_url: str) -> ProcessResult:
        """Process document through AI service."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/process-document",
                json={"document_url": document_url},
                headers={"Authorization": f"Bearer {await self.get_token()}"}
            )
            
            if response.status_code != 200:
                raise Exception(f"AI service error: {response.text}")
            
            return ProcessResult(**response.json())
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json={"text": text},
                headers={"Authorization": f"Bearer {await self.get_token()}"}
            )
            
            return response.json()["embeddings"]
    
    async def get_token(self) -> str:
        """Get access token for AI service."""
        token = await self.credential.get_token("https://cognitiveservices.azure.com/.default")
        return token.token
```

### 2. Asynchronous Communication

#### Queue-Based Processing
```python
# Backend queue producer
class DocumentQueueProducer:
    def __init__(self):
        self.connection_string = os.getenv('STORAGE_CONNECTION_STRING')
        self.queue_service = QueueServiceClient.from_connection_string(self.connection_string)
        self.queue_client = self.queue_service.get_queue_client("document-processing")
    
    async def queue_document_processing(self, document_id: str, document_url: str):
        """Queue document for AI processing."""
        message = json.dumps({
            "document_id": document_id,
            "document_url": document_url,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "normal"
        })
        
        await self.queue_client.send_message(
            content=message,
            visibility_timeout=30
        )
```

```python
# AI Functions queue consumer
import azure.functions as func

async def process_document_queue(message: func.QueueMessage) -> func.HttpResponse:
    """Process document from queue."""
    try:
        message_data = json.loads(message.get_body())
        document_id = message_data["document_id"]
        document_url = message_data["document_url"]
        
        # Process document
        result = await process_document(document_url)
        
        # Update search index
        await update_search_index(document_id, result)
        
        # Notify completion
        await notify_processing_complete(document_id, result)
        
        return func.HttpResponse("Document processed successfully")
        
    except Exception as e:
        logging.error(f"Document processing failed: {str(e)}")
        raise
```

### 3. Event-Driven Communication

#### Event Bus Pattern
```python
# Backend event publisher
class EventPublisher:
    def __init__(self):
        self.event_grid_client = EventGridPublisherClient(
            endpoint=os.getenv('EVENT_GRID_ENDPOINT'),
            credential=DefaultAzureCredential()
        )
    
    async def publish_document_processed(self, document_id: str, result: ProcessResult):
        """Publish document processed event."""
        event = EventGridEvent(
            data={
                "document_id": document_id,
                "processing_result": result.dict(),
                "timestamp": datetime.utcnow().isoformat()
            },
            event_type="DocumentProcessed",
            subject=f"documents/{document_id}",
            data_version="1.0"
        )
        
        await self.event_grid_client.send([event])
```

## Data Management

### 1. Service-Specific Data

#### Backend Service Data
```python
# Database models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    display_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    tenant_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    status = Column(Enum(ContractStatus), default=ContractStatus.UPLOADED)
```

#### Search Service Data
```python
# Search index schema
class ContractSearchSchema:
    """Azure Search index schema for contracts."""
    
    @staticmethod
    def get_index_schema():
        return {
            "name": "contracts-index",
            "fields": [
                {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
                {"name": "name", "type": "Edm.String", "searchable": True, "retrievable": True},
                {"name": "content", "type": "Edm.String", "searchable": True, "retrievable": True},
                {"name": "content_vector", "type": "Collection(Edm.Single)", "searchable": True, "dimensions": 1536},
                {"name": "clauses", "type": "Collection(Edm.ComplexType)", "fields": [
                    {"name": "type", "type": "Edm.String"},
                    {"name": "text", "type": "Edm.String"},
                    {"name": "confidence", "type": "Edm.Double"}
                ]},
                {"name": "uploaded_by", "type": "Edm.String", "filterable": True},
                {"name": "uploaded_at", "type": "Edm.DateTimeOffset", "filterable": True, "sortable": True},
                {"name": "file_type", "type": "Edm.String", "filterable": True},
                {"name": "risk_score", "type": "Edm.Double", "filterable": True, "sortable": True}
            ]
        }
```

### 2. Shared Data Access Patterns

#### Repository Pattern
```python
# Base repository
class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, model: Base) -> Base:
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model
    
    async def get_by_id(self, model_class: Type[Base], id: str) -> Optional[Base]:
        return await self.session.get(model_class, id)
    
    async def update(self, model: Base) -> Base:
        await self.session.commit()
        await self.session.refresh(model)
        return model
    
    async def delete(self, model: Base) -> None:
        await self.session.delete(model)
        await self.session.commit()

# Contract repository
class ContractRepository(BaseRepository):
    async def get_user_contracts(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Contract]:
        result = await self.session.execute(
            select(Contract)
            .where(Contract.uploaded_by == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Contract.uploaded_at.desc())
        )
        return result.scalars().all()
    
    async def search_contracts(self, query: str, user_id: str) -> List[Contract]:
        # Search implementation using Azure Search
        search_client = SearchClient(
            endpoint=os.getenv('SEARCH_ENDPOINT'),
            index_name="contracts-index",
            credential=DefaultAzureCredential()
        )
        
        results = await search_client.search(
            search_text=query,
            filter=f"uploaded_by eq '{user_id}'"
        )
        
        return [Contract(**result) for result in results]
```

## API Design

### 1. RESTful API Standards

#### Backend API Endpoints
```python
# Contract management API
@router.get("/contracts", response_model=List[ContractResponse])
async def get_contracts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get user's contracts with pagination."""
    contracts = await contract_repo.get_user_contracts(current_user.id, skip, limit)
    return contracts

@router.post("/contracts/upload", response_model=ContractResponse)
async def upload_contract(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and process a new contract."""
    # Validate file
    if not file.filename.endswith(('.pdf', '.docx', '.doc')):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Upload to storage
    contract_url = await upload_to_storage(file, current_user.id)
    
    # Create contract record
    contract = Contract(
        id=str(uuid.uuid4()),
        name=file.filename,
        file_path=contract_url,
        file_size=file.size,
        content_type=file.content_type,
        uploaded_by=current_user.id
    )
    
    contract = await contract_repo.create(contract)
    
    # Queue for processing
    await queue_document_processing(contract.id, contract_url)
    
    return contract

@router.get("/contracts/{contract_id}/search")
async def search_contract(
    contract_id: str,
    query: str,
    current_user: User = Depends(get_current_user)
):
    """Search within a specific contract."""
    # Verify ownership
    contract = await contract_repo.get_by_id(Contract, contract_id)
    if not contract or contract.uploaded_by != current_user.id:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Search within contract
    results = await search_within_contract(contract_id, query)
    return results
```

### 2. GraphQL API (Optional)

#### GraphQL Schema
```python
# GraphQL schema definition
class Query(graphene.ObjectType):
    contracts = graphene.List(ContractType, user_id=graphene.String(required=True))
    contract = graphene.Field(ContractType, id=graphene.String(required=True))
    search_contracts = graphene.List(ContractType, query=graphene.String(required=True))
    
    async def resolve_contracts(self, info, user_id):
        return await contract_repo.get_user_contracts(user_id)
    
    async def resolve_contract(self, info, id):
        return await contract_repo.get_by_id(Contract, id)
    
    async def resolve_search_contracts(self, info, query):
        return await contract_repo.search_contracts(query)

class Mutation(graphene.ObjectType):
    upload_contract = graphene.Field(ContractType, file=graphene.String(required=True))
    delete_contract = graphene.Boolean(id=graphene.String(required=True))
    
    async def resolve_upload_contract(self, info, file):
        # File upload logic
        pass
    
    async def resolve_delete_contract(self, info, id):
        # Delete logic
        pass

schema = graphene.Schema(query=Query, mutation=Mutation)
```

## Security Implementation

### 1. Authentication Flow

```python
# JWT token validation
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        # Decode and validate token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        user = await user_repo.get_by_id(User, user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Role-based access control
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

### 2. Service-to-Service Authentication

```python
# Managed identity for service communication
class ServiceAuthenticator:
    def __init__(self):
        self.credential = DefaultAzureCredential()
    
    async def get_service_token(self, scope: str) -> str:
        token = await self.credential.get_token(scope)
        return token.token
    
    async def authenticate_request(self, request: httpx.Request) -> httpx.Request:
        token = await self.get_service_token("https://management.azure.com/.default")
        request.headers["Authorization"] = f"Bearer {token}"
        return request
```

## Error Handling & Resilience

### 1. Circuit Breaker Pattern

```python
# Circuit breaker for external services
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func: Callable, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e

# Usage
circuit_breaker = CircuitBreaker()

async def call_ai_service(text: str):
    return await circuit_breaker.call(ai_service_client.process_text, text)
```

### 2. Retry Pattern

```python
# Retry with exponential backoff
async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
):
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries:
                raise e
            
            delay = min(base_delay * (2 ** attempt), max_delay)
            await asyncio.sleep(delay)
```

## Monitoring & Observability

### 1. Distributed Tracing

```python
# OpenTelemetry integration
from opentelemetry import trace
from opentelemetry.exporter.azure.monitor import AzureMonitorTraceExporter

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("process_document")
async def process_document(document_id: str):
    span = trace.get_current_span()
    span.set_attribute("document.id", document_id)
    
    try:
        # Process document
        result = await ai_service.process_document(document_id)
        span.set_attribute("document.status", "success")
        return result
    except Exception as e:
        span.set_attribute("document.status", "error")
        span.set_attribute("error.message", str(e))
        raise
```

### 2. Metrics Collection

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
document_processed_counter = Counter('documents_processed_total', 'Total documents processed')
processing_duration = Histogram('document_processing_duration_seconds', 'Document processing duration')
active_connections = Gauge('active_connections', 'Number of active connections')

async def process_document_with_metrics(document_id: str):
    with processing_duration.time():
        active_connections.inc()
        try:
            result = await process_document(document_id)
            document_processed_counter.inc()
            return result
        finally:
            active_connections.dec()
```

## Testing Strategy

### 1. Unit Testing

```python
# Service unit tests
@pytest.mark.asyncio
async def test_contract_upload():
    # Mock dependencies
    mock_storage = AsyncMock()
    mock_queue = AsyncMock()
    
    service = ContractService(
        storage_client=mock_storage,
        queue_client=mock_queue
    )
    
    # Test upload
    result = await service.upload_contract("test.pdf", b"file content", "user123")
    
    # Assertions
    assert result.name == "test.pdf"
    mock_storage.upload.assert_called_once()
    mock_queue.send_message.assert_called_once()
```

### 2. Integration Testing

```python
# Service integration tests
@pytest.mark.asyncio
async def test_end_to_end_document_processing():
    # Setup test environment
    async with TestClient(app) as client:
        # Upload document
        response = await client.post("/api/v1/contracts/upload", files={"file": ("test.pdf", b"content")})
        assert response.status_code == 200
        
        contract_id = response.json()["id"]
        
        # Wait for processing (poll)
        for _ in range(10):
            response = await client.get(f"/api/v1/contracts/{contract_id}")
            if response.json()["status"] == "processed":
                break
            await asyncio.sleep(1)
        
        # Verify processing
        response = await client.get(f"/api/v1/contracts/{contract_id}")
        assert response.json()["status"] == "processed"
        assert "clauses" in response.json()
```

## Deployment Strategy

### 1. Container Configuration

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Kubernetes Configuration

```yaml
# Backend deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend-service
  template:
    metadata:
      labels:
        app: backend-service
    spec:
      containers:
      - name: backend
        image: droit-ai/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Next Steps

1. [Data Processing Pipeline](./data-pipeline.md) - Document processing workflow
2. [Legal AI Integration](./legal-ai-integration.md) - AI services integration
3. [Testing Strategy](./testing.md) - Comprehensive testing approach

## References

- [Microservices Patterns](https://microservices.io/patterns/)
- [Azure Microservices Best Practices](https://docs.microsoft.com/en-us/azure/architecture/microservices)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
