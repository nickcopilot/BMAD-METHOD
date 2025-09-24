# Security Framework
## IRMS System - Internal Audit Webapp

**Component**: Security Architecture and Implementation
**For**: Development Team Security Implementation
**Priority**: Phase 1A - Week 1 (Critical Foundation)

---

## Zero-Trust Security Model

### Authentication & Authorization Framework

#### Authentication Protocol: OAuth2 with PKCE
```python
# Authentication configuration
class AuthConfig:
    OAUTH2_PROVIDER = "custom"  # Or Azure AD, Google, etc.
    JWT_ALGORITHM = "RS256"
    ACCESS_TOKEN_EXPIRE_HOURS = 8
    REFRESH_TOKEN_EXPIRE_DAYS = 30
    REQUIRE_HTTPS = True

    # Multi-Factor Authentication
    MFA_REQUIRED_ROLES = ["department_head", "leadership"]
    MFA_METHOD = "TOTP"  # Time-based One-Time Password

    # Password Policy
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_SPECIAL_CHARS = True
    PASSWORD_ROTATION_DAYS = 90
```

#### JWT Token Structure
```json
{
  "sub": "user-uuid-here",
  "role": "senior_auditor",
  "permissions": [
    "task:read",
    "task:update_own",
    "task:review_team",
    "kpi:read_own",
    "assignment:suggest"
  ],
  "department": "internal_audit",
  "exp": 1674567890,
  "iat": 1674538090,
  "iss": "irms-auth-service"
}
```

---

## Role-Based Access Control (RBAC)

### User Roles and Permissions

#### Role Hierarchy
```python
class UserRole(Enum):
    AUDIT_ASSISTANT = "audit_assistant"      # Level 1-3
    SENIOR_AUDITOR = "senior_auditor"        # Level 4-5
    DEPARTMENT_HEAD = "department_head"      # Management
    LEADERSHIP = "leadership"                # Directors/VPs

class Permission(Enum):
    # Task Management
    TASK_CREATE = "task:create"
    TASK_READ_OWN = "task:read_own"
    TASK_READ_TEAM = "task:read_team"
    TASK_READ_DEPT = "task:read_department"
    TASK_READ_ALL = "task:read_all"
    TASK_UPDATE_OWN = "task:update_own"
    TASK_UPDATE_TEAM = "task:update_team"
    TASK_DELETE = "task:delete"
    TASK_REVIEW = "task:review"

    # KPI Management
    KPI_READ_OWN = "kpi:read_own"
    KPI_READ_TEAM = "kpi:read_team"
    KPI_READ_DEPT = "kpi:read_department"
    KPI_READ_ALL = "kpi:read_all"
    KPI_UPDATE_MANUAL = "kpi:update_manual"
    KPI_CALCULATE = "kpi:calculate"

    # Assignment Management
    ASSIGNMENT_SUGGEST = "assignment:suggest"
    ASSIGNMENT_APPROVE = "assignment:approve"
    ASSIGNMENT_OVERRIDE = "assignment:override"

    # System Administration
    USER_MANAGE = "user:manage"
    SYSTEM_CONFIG = "system:configure"
    AUDIT_LOG_VIEW = "audit:view_logs"
```

#### Permission Matrix
```python
ROLE_PERMISSIONS = {
    UserRole.AUDIT_ASSISTANT: [
        Permission.TASK_READ_OWN,
        Permission.TASK_UPDATE_OWN,
        Permission.KPI_READ_OWN,
    ],
    UserRole.SENIOR_AUDITOR: [
        Permission.TASK_READ_OWN,
        Permission.TASK_READ_TEAM,
        Permission.TASK_UPDATE_OWN,
        Permission.TASK_UPDATE_TEAM,
        Permission.TASK_REVIEW,
        Permission.KPI_READ_OWN,
        Permission.KPI_READ_TEAM,
        Permission.ASSIGNMENT_SUGGEST,
    ],
    UserRole.DEPARTMENT_HEAD: [
        Permission.TASK_READ_DEPT,
        Permission.TASK_CREATE,
        Permission.TASK_DELETE,
        Permission.KPI_READ_DEPT,
        Permission.KPI_UPDATE_MANUAL,
        Permission.ASSIGNMENT_APPROVE,
        Permission.ASSIGNMENT_OVERRIDE,
    ],
    UserRole.LEADERSHIP: [
        Permission.TASK_READ_ALL,
        Permission.KPI_READ_ALL,
        Permission.KPI_CALCULATE,
        Permission.USER_MANAGE,
        Permission.SYSTEM_CONFIG,
        Permission.AUDIT_LOG_VIEW,
    ]
}
```

---

## Data Protection Architecture

### Encryption Strategy

#### Encryption at Rest
```python
# Database encryption configuration
class DatabaseEncryption:
    # PostgreSQL transparent data encryption
    TDE_ENABLED = True
    ENCRYPTION_ALGORITHM = "AES-256"
    KEY_MANAGEMENT = "AWS_KMS"  # or "Azure_KeyVault", "HashiCorp_Vault"

    # Application-level field encryption
    ENCRYPTED_FIELDS = [
        "kpi_scores.manual_score",
        "users.salary_info",
        "audit_findings.sensitive_details"
    ]

    # Key rotation schedule
    KEY_ROTATION_INTERVAL_DAYS = 90
```

#### Encryption in Transit
```yaml
TLS_Configuration:
  version: "1.3"
  cipher_suites:
    - "TLS_AES_256_GCM_SHA384"
    - "TLS_CHACHA20_POLY1305_SHA256"
  certificate_authority: "LetsEncrypt"
  hsts_enabled: true
  hsts_max_age: 31536000
```

#### Application-Level Encryption
```python
from cryptography.fernet import Fernet
import os

class FieldEncryption:
    def __init__(self):
        # Key from environment or key management service
        self.key = os.environ.get("FIELD_ENCRYPTION_KEY")
        self.fernet = Fernet(self.key)

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data before database storage"""
        if not data:
            return data
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data after database retrieval"""
        if not encrypted_data:
            return encrypted_data
        return self.fernet.decrypt(encrypted_data.encode()).decode()
```

---

## Network Security Implementation

### Web Application Firewall (WAF)
```yaml
WAF_Rules:
  # OWASP Top 10 Protection
  sql_injection_protection: enabled
  xss_protection: enabled
  csrf_protection: enabled

  # Rate Limiting
  api_rate_limit:
    requests_per_minute: 1000
    requests_per_hour: 10000
    burst_capacity: 100

  # IP Restrictions (Optional)
  ip_allowlist:
    enabled: false  # Configure for production if needed
    allowed_ranges: []

  # Geographic Restrictions
  geo_blocking:
    enabled: false  # Configure if required by policy
    blocked_countries: []
```

### API Security Headers
```python
# FastAPI security middleware
from fastapi.middleware.security import SecurityMiddleware

security_headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' ws: wss:;"
    ),
    "Referrer-Policy": "strict-origin-when-cross-origin"
}
```

---

## Audit Trail Implementation

### Comprehensive Audit Logging

#### Audit Event Categories
```python
class AuditEventType(Enum):
    # Authentication Events
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    SESSION_TIMEOUT = "auth.session.timeout"
    PASSWORD_CHANGE = "auth.password.change"
    MFA_SUCCESS = "auth.mfa.success"
    MFA_FAILURE = "auth.mfa.failure"

    # Authorization Events
    PERMISSION_GRANTED = "authz.permission.granted"
    PERMISSION_DENIED = "authz.permission.denied"
    ROLE_CHANGE = "authz.role.change"

    # Data Access Events
    DATA_READ = "data.read"
    DATA_CREATE = "data.create"
    DATA_UPDATE = "data.update"
    DATA_DELETE = "data.delete"

    # KPI Events
    KPI_CALCULATE = "kpi.calculate"
    KPI_MANUAL_OVERRIDE = "kpi.manual_override"
    KPI_REVIEW_CYCLE = "kpi.review_cycle"

    # Administrative Events
    USER_CREATE = "admin.user.create"
    USER_UPDATE = "admin.user.update"
    USER_DEACTIVATE = "admin.user.deactivate"
    SYSTEM_CONFIG_CHANGE = "admin.config.change"
```

#### Audit Log Data Model
```python
from sqlalchemy import Column, UUID, String, TIMESTAMP, JSONB, Text
from sqlalchemy.dialects.postgresql import INET

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID, primary_key=True, server_default="gen_random_uuid()")
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(UUID, ForeignKey("users.id"), index=True)
    session_id = Column(String(255), index=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default="NOW()")
    ip_address = Column(INET)
    user_agent = Column(Text)

    # Resource information
    resource_type = Column(String(50), index=True)
    resource_id = Column(String(255), index=True)
    action = Column(String(50), nullable=False)

    # Data snapshots for compliance
    before_data = Column(JSONB)  # State before change
    after_data = Column(JSONB)   # State after change
    event_details = Column(JSONB)  # Additional context

    # Compliance and correlation
    correlation_id = Column(UUID, index=True)
    compliance_tags = Column(ARRAY(String))  # ["SOX", "COSO", "ISO27001"]
    retention_date = Column(Date, nullable=False)  # 7 years for compliance
```

#### Audit Logging Service
```python
class AuditService:
    def __init__(self, db_session):
        self.db = db_session

    async def log_event(
        self,
        event_type: AuditEventType,
        user_id: UUID,
        session_id: str,
        resource_type: str = None,
        resource_id: str = None,
        before_data: dict = None,
        after_data: dict = None,
        event_details: dict = None,
        compliance_tags: list = None,
        request: Request = None
    ):
        """Log audit event with comprehensive context"""

        audit_entry = AuditLog(
            event_type=event_type.value,
            user_id=user_id,
            session_id=session_id,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            resource_type=resource_type,
            resource_id=resource_id,
            before_data=before_data,
            after_data=after_data,
            event_details=event_details or {},
            compliance_tags=compliance_tags or [],
            retention_date=datetime.now().date() + timedelta(days=7*365)  # 7 years
        )

        self.db.add(audit_entry)
        await self.db.commit()

        # Send to external SIEM if configured
        await self._send_to_siem(audit_entry)
```

---

## Security Implementation Checklist

### Phase 1A Security Requirements

#### Week 1: Authentication Foundation
- [ ] **OAuth2/JWT Implementation**
  - [ ] JWT token generation and validation
  - [ ] Refresh token rotation
  - [ ] Token revocation capability
  - [ ] Secure token storage in Redis

- [ ] **Role-Based Access Control**
  - [ ] User role assignment
  - [ ] Permission validation middleware
  - [ ] API endpoint protection
  - [ ] Frontend route protection

#### Week 2: Data Protection
- [ ] **Encryption Implementation**
  - [ ] Database connection encryption
  - [ ] TLS certificate configuration
  - [ ] Application-level field encryption
  - [ ] Key management setup

- [ ] **Audit Trail System**
  - [ ] Audit log database table
  - [ ] Event logging middleware
  - [ ] Audit service implementation
  - [ ] Compliance tag system

### Security Testing Requirements

#### Security Test Categories
```python
# Example security test structure
class SecurityTests:
    async def test_authentication_required(self):
        """Verify all endpoints require authentication"""
        response = await client.get("/api/tasks")
        assert response.status_code == 401

    async def test_role_based_access(self):
        """Verify role-based access control"""
        junior_token = create_test_token(role="audit_assistant")
        response = await client.get(
            "/api/users/all",
            headers={"Authorization": f"Bearer {junior_token}"}
        )
        assert response.status_code == 403

    async def test_sql_injection_protection(self):
        """Verify SQL injection protection"""
        malicious_payload = "'; DROP TABLE users; --"
        response = await client.get(f"/api/users/{malicious_payload}")
        assert response.status_code in [400, 404]  # Not 500

    async def test_audit_logging(self):
        """Verify audit events are logged"""
        await create_task_as_user(test_user)
        audit_logs = await get_audit_logs(event_type="data.create")
        assert len(audit_logs) == 1
        assert audit_logs[0].user_id == test_user.id
```

---

## Compliance Framework Integration

### SOX Compliance Requirements
```python
class SOXCompliance:
    REQUIRED_AUDIT_EVENTS = [
        "kpi.manual_override",
        "assignment.approve",
        "data.delete",
        "admin.user.role_change",
        "system.config.change"
    ]

    SEGREGATION_OF_DUTIES = {
        "kpi_calculation": ["senior_auditor", "system"],
        "kpi_approval": ["department_head", "leadership"],
        "user_management": ["leadership", "system_admin"]
    }

    RETENTION_PERIOD_YEARS = 7
    IMMUTABLE_AUDIT_TRAIL = True
```

### COSO Framework Integration
```python
class COSOControls:
    CONTROL_ACTIVITIES = {
        "authorization_controls": "Role-based access control implementation",
        "segregation_duties": "Multi-level approval workflows",
        "information_processing": "Automated audit trail generation",
        "physical_controls": "Infrastructure access controls",
        "performance_reviews": "KPI monitoring and alerting"
    }

    MONITORING_COMPONENTS = [
        "ongoing_monitoring",     # Real-time audit trail
        "separate_evaluations",   # Compliance assessments
        "reporting_deficiencies"  # Security incident reporting
    ]
```

---

## Security Monitoring and Incident Response

### Security Event Monitoring
```python
class SecurityMonitoring:
    MONITORED_EVENTS = [
        "multiple_failed_logins",    # Potential brute force
        "privilege_escalation",      # Role change attempts
        "unusual_data_access",       # Off-hours or bulk access
        "failed_permission_checks",  # Potential unauthorized access
        "configuration_changes"      # System modification attempts
    ]

    ALERT_THRESHOLDS = {
        "failed_logins_per_hour": 5,
        "permission_denials_per_hour": 10,
        "bulk_data_access_records": 1000
    }
```

This security framework provides comprehensive protection for the IRMS System while maintaining usability and supporting the audit compliance requirements.