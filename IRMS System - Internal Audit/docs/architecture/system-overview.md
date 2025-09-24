# System Overview
## IRMS System - Internal Audit Webapp Architecture

**Component**: System Architecture Overview
**For**: Development Team Setup and Understanding
**Dependencies**: Foundation for all other architecture components

---

## High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │────│   Load Balancer  │────│   Web Server    │
│   (React SPA)   │    │   (HAProxy/Nginx)│    │   (Nginx/Apache)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Gateway   │────│   Auth Service   │    │   Application   │
│   (FastAPI)     │    │   (OAuth2/JWT)   │    │   Layer         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Background    │    │   Audit Trail    │    │   Business      │
│   Jobs (Celery) │    │   Service        │    │   Logic Layer   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Message Queue │    │   Cache Layer    │    │   Data Access   │
│   (Redis)       │    │   (Redis)        │    │   Layer (SQLAlchemy)
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                        ┌──────────────────┐    ┌─────────────────┐
                        │   File Storage   │    │   Primary DB    │
                        │   (S3/MinIO)     │    │   (PostgreSQL)  │
                        └──────────────────┘    └─────────────────┘
```

## Core Components

| Component | Technology | Purpose | Development Priority |
|-----------|------------|---------|---------------------|
| **Frontend** | React 18 + TypeScript | User interface and experience | Phase 1A - Week 1 |
| **API Layer** | FastAPI + Pydantic | Business logic and data validation | Phase 1A - Week 1 |
| **Database** | PostgreSQL 15+ | Primary data storage with JSONB | Phase 1A - Week 1 |
| **Cache** | Redis 7+ | Performance optimization | Phase 1A - Week 2 |
| **Message Queue** | Celery + Redis | Background processing | Phase 1A - Week 3 |
| **Auth Service** | OAuth2 + JWT | Authentication and authorization | Phase 1A - Week 1 |
| **Audit Service** | Custom Python Service | Compliance and audit trails | Phase 1A - Week 2 |

---

## Development Environment Setup

### Required Tools and Versions
```yaml
Backend:
  - Python 3.11+
  - FastAPI 0.104+
  - SQLAlchemy 2.0+
  - PostgreSQL 15+
  - Redis 7+

Frontend:
  - Node.js 18+
  - React 18+
  - TypeScript 5+
  - Vite or Create React App

Development Tools:
  - Docker & Docker Compose
  - Git
  - Pre-commit hooks
  - ESLint + Prettier
  - pytest + coverage
```

### Local Development Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Dev     │    │   FastAPI Dev   │    │   PostgreSQL    │
│   Server        │────│   Server        │────│   Container     │
│   :3000         │    │   :8000         │    │   :5432         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Redis         │
                       │   Container     │
                       │   :6379         │
                       └─────────────────┘
```

---

## Phase 1A Architecture Focus

### Minimum Viable Architecture Components

#### Week 1: Foundation
- **Database Setup**: PostgreSQL with basic schema
- **API Framework**: FastAPI with authentication
- **Frontend Framework**: React with TypeScript
- **Basic Security**: OAuth2/JWT implementation

#### Week 2: Core Services
- **Caching Layer**: Redis integration
- **Audit Logging**: Basic compliance logging
- **Background Jobs**: Celery setup for KPI calculations
- **Email Service**: Basic notification system

#### Week 3: Integration
- **Real-time Updates**: WebSocket implementation
- **File Handling**: Basic file upload/download
- **Monitoring**: Basic health checks and logging
- **Testing Framework**: Unit and integration test setup

#### Week 4: Optimization
- **Performance Tuning**: Query optimization
- **Security Hardening**: Production security settings
- **Deployment Prep**: Docker containerization
- **Documentation**: API documentation with OpenAPI

---

## Technology Stack Rationale

### Backend Framework: FastAPI
**Why FastAPI**:
- ✅ **Performance**: High performance comparable to NodeJS and Go
- ✅ **Developer Experience**: Automatic API documentation with OpenAPI
- ✅ **Type Safety**: Full Python type hints with Pydantic validation
- ✅ **Modern Python**: Async/await support for high concurrency
- ✅ **Rapid Development**: Minimal boilerplate code

### Database: PostgreSQL
**Why PostgreSQL**:
- ✅ **JSONB Support**: Perfect for flexible KPI framework storage
- ✅ **ACID Compliance**: Essential for audit trail integrity
- ✅ **Performance**: Excellent query optimization and indexing
- ✅ **Compliance**: Strong audit and security features
- ✅ **Scalability**: Supports read replicas and partitioning

### Frontend: React + TypeScript
**Why React + TypeScript**:
- ✅ **Component Architecture**: Perfect for role-based interfaces
- ✅ **Type Safety**: Reduces bugs with compile-time checking
- ✅ **Ecosystem**: Rich library ecosystem for Kanban, Calendar, Charts
- ✅ **Performance**: Virtual DOM and optimization features
- ✅ **Team Familiarity**: Widely adopted and documented

### Caching: Redis
**Why Redis**:
- ✅ **Performance**: In-memory storage for sub-millisecond responses
- ✅ **Data Structures**: Native support for complex data types
- ✅ **Pub/Sub**: Real-time messaging for WebSocket updates
- ✅ **Session Storage**: Distributed session management
- ✅ **Message Queuing**: Celery broker for background jobs

---

## Security Architecture Integration

### Authentication Flow
```
User → React App → FastAPI → OAuth2 Provider → JWT Token → Redis Session
```

### Authorization Levels
- **Role-Based Access Control (RBAC)**: 4 distinct user roles
- **Resource-Level Permissions**: Task, KPI, and assignment access control
- **API Endpoint Security**: All endpoints protected with JWT validation
- **Frontend Route Protection**: Role-based route access in React

### Data Protection Strategy
- **Encryption at Rest**: Database and file storage encryption
- **Encryption in Transit**: TLS 1.3 for all communications
- **Application-Level Encryption**: Sensitive KPI data encrypted
- **Audit Trail**: Complete activity logging for compliance

---

## Performance Architecture

### Response Time Targets
- **Page Load**: <2 seconds for all interfaces
- **API Responses**: <500ms for most operations
- **Real-time Updates**: <100ms WebSocket latency
- **Database Queries**: <50ms for indexed queries

### Scalability Strategy
- **Horizontal Scaling**: Stateless API servers behind load balancer
- **Database Scaling**: Read replicas for reporting queries
- **Caching Strategy**: Multi-layer caching (Redis + application level)
- **Background Processing**: Async job queue for heavy operations

### Concurrent User Support
- **Target**: 100+ concurrent users in Phase 1A
- **Scaling**: Auto-scaling groups for increased demand
- **Resource Management**: Connection pooling and query optimization
- **Performance Monitoring**: Real-time performance metrics

---

## Development Workflow Integration

### Code Quality Standards
```python
# Example: FastAPI endpoint structure
@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    # Validate permissions
    if not has_permission(current_user, "task:create"):
        raise HTTPException(403, "Insufficient permissions")

    # Create task with audit trail
    new_task = await task_service.create(db, task, current_user.id)

    # Trigger background KPI recalculation
    await kpi_calculation.delay(new_task.assigned_user_id)

    return new_task
```

### Testing Strategy
- **Unit Tests**: 90%+ code coverage requirement
- **Integration Tests**: API endpoint and database integration
- **Frontend Tests**: Component and user interaction testing
- **End-to-End Tests**: Complete user workflow validation

### Documentation Requirements
- **API Documentation**: Automatically generated with OpenAPI
- **Component Documentation**: React component prop documentation
- **Architecture Decisions**: ADR (Architecture Decision Records)
- **Deployment Guides**: Step-by-step deployment instructions

---

## Integration with Other Architecture Components

### Dependencies
- **Security Architecture**: Authentication and authorization implementation
- **Data Architecture**: Database schema and data models
- **KPI Calculation Engine**: Background job processing architecture
- **API Design**: RESTful endpoint structure and documentation

### Next Steps
1. **Review Security Architecture** for authentication implementation
2. **Study Data Architecture** for database schema setup
3. **Understand KPI Engine** for background job requirements
4. **Plan API Design** for endpoint development sequence

This system overview provides the foundation for understanding and implementing the IRMS System architecture with focus on Phase 1A development priorities.