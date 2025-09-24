# Coding Standards and Development Guidelines
## IRMS System - Internal Audit Webapp

**Component**: Development Standards and Best Practices
**For**: Development Team Implementation Guidelines
**Priority**: Phase 1A - Ongoing (Quality Foundation)

---

## Technology Stack Standards

### Backend Development Standards (FastAPI + Python)

#### Code Structure and Organization
```python
# Project structure standard
irms-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # Environment configuration
│   │   └── database.py         # Database connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── kpi.py
│   │   └── audit.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   └── kpi.py
│   ├── routers/                # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   ├── kpis.py
│   │   └── assignments.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── task_service.py
│   │   ├── kpi_service.py
│   │   └── assignment_service.py
│   ├── core/                   # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── permissions.py
│   │   └── audit.py
│   └── utils/                  # Helper functions
│       ├── __init__.py
│       ├── validators.py
│       └── formatters.py
├── tests/
├── alembic/                    # Database migrations
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

#### Python Code Standards
```python
# Example: Proper service class structure
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..core.audit import AuditService
from ..core.permissions import require_permission

class TaskService:
    """Service class for task management operations."""

    def __init__(self, db_session: AsyncSession, audit_service: AuditService):
        self.db = db_session
        self.audit = audit_service

    async def create_task(
        self,
        task_data: TaskCreate,
        created_by: UUID,
        current_user: User
    ) -> TaskResponse:
        """
        Create a new task with proper validation and audit trail.

        Args:
            task_data: Task creation data
            created_by: UUID of user creating the task
            current_user: Current authenticated user

        Returns:
            TaskResponse: Created task data

        Raises:
            PermissionError: If user lacks task creation permissions
            ValidationError: If task data is invalid
        """
        # Validate permissions
        require_permission(current_user, "task:create")

        # Create task entity
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            work_group_id=task_data.work_group_id,
            created_by_user_id=created_by,
            difficulty_level=task_data.difficulty_level,
            estimated_hours=task_data.estimated_hours,
            sla_target_hours=task_data.sla_target_hours
        )

        # Add to database
        self.db.add(new_task)
        await self.db.flush()  # Get ID without committing

        # Log audit event
        await self.audit.log_event(
            event_type="data.create",
            user_id=current_user.id,
            resource_type="task",
            resource_id=str(new_task.id),
            after_data=new_task.to_dict(),
            event_details={"method": "create_task"}
        )

        await self.db.commit()
        return TaskResponse.from_orm(new_task)

    async def get_tasks_by_user(
        self,
        user_id: UUID,
        status_filter: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TaskResponse]:
        """Get tasks assigned to a specific user with filtering."""
        query = select(Task).where(Task.assigned_user_id == user_id)

        if status_filter:
            query = query.where(Task.status.in_(status_filter))

        query = query.order_by(Task.priority_score.desc(), Task.created_at.desc())
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        return [TaskResponse.from_orm(task) for task in tasks]
```

#### API Endpoint Standards
```python
# Example: Proper FastAPI router structure
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from ..dependencies import get_current_user, get_db, get_task_service
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..models.user import User

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """
    Create a new task.

    **Required Permissions**: task:create

    **Business Rules**:
    - Task title must be unique within work group
    - SLA target hours must be positive
    - Difficulty level must be 1-5
    """
    try:
        return await task_service.create_task(
            task_data=task_data,
            created_by=current_user.id,
            current_user=current_user
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create tasks"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[List[str]] = Query(None),
    assigned_to: Optional[UUID] = Query(None),
    work_group: Optional[UUID] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
) -> List[TaskResponse]:
    """
    Get tasks with filtering options.

    **Query Parameters**:
    - status: Filter by task status (multiple values allowed)
    - assigned_to: Filter by assigned user ID
    - work_group: Filter by work group ID
    - limit: Maximum number of results (1-1000)
    - offset: Pagination offset
    """
    return await task_service.get_filtered_tasks(
        current_user=current_user,
        status_filter=status,
        assigned_to=assigned_to,
        work_group_id=work_group,
        limit=limit,
        offset=offset
    )
```

---

### Frontend Development Standards (React + TypeScript)

#### Component Structure Standards
```typescript
// File: src/components/TaskCard/TaskCard.tsx
import React, { useState, useCallback } from 'react';
import { Task, TaskStatus } from '../../types/task';
import { usePermissions } from '../../hooks/usePermissions';
import { useAuditTrail } from '../../hooks/useAuditTrail';
import './TaskCard.styles.css';

interface TaskCardProps {
  task: Task;
  onStatusChange?: (taskId: string, newStatus: TaskStatus) => void;
  onEdit?: (task: Task) => void;
  showAssignee?: boolean;
  compact?: boolean;
}

/**
 * TaskCard component displays task information with interactive controls
 * based on user permissions and role.
 *
 * @param task - Task object to display
 * @param onStatusChange - Callback for status changes
 * @param onEdit - Callback for edit actions
 * @param showAssignee - Whether to show assignee information
 * @param compact - Whether to use compact layout
 */
export const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onStatusChange,
  onEdit,
  showAssignee = true,
  compact = false
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const { canUpdate, canReview } = usePermissions();
  const { logUserAction } = useAuditTrail();

  const handleStatusChange = useCallback(async (newStatus: TaskStatus) => {
    if (!canUpdate(task) || !onStatusChange) return;

    setIsLoading(true);
    try {
      await onStatusChange(task.id, newStatus);
      logUserAction('task_status_change', {
        taskId: task.id,
        oldStatus: task.status,
        newStatus
      });
    } catch (error) {
      console.error('Failed to update task status:', error);
      // Handle error (show toast, etc.)
    } finally {
      setIsLoading(false);
    }
  }, [task, onStatusChange, canUpdate, logUserAction]);

  const getPriorityColor = useCallback((priority: number): string => {
    if (priority >= 80) return 'priority-critical';
    if (priority >= 60) return 'priority-high';
    if (priority >= 40) return 'priority-medium';
    return 'priority-low';
  }, []);

  const formatSLAStatus = useCallback((slaHoursRemaining: number): string => {
    if (slaHoursRemaining < 0) return 'Overdue';
    if (slaHoursRemaining < 4) return `${Math.floor(slaHoursRemaining)}h remaining`;
    if (slaHoursRemaining < 24) return `${Math.floor(slaHoursRemaining)}h remaining`;
    return `${Math.floor(slaHoursRemaining / 24)}d remaining`;
  }, []);

  return (
    <div className={`task-card ${compact ? 'compact' : ''} ${getPriorityColor(task.priorityScore)}`}>
      <div className="task-card__header">
        <h3 className="task-card__title" title={task.title}>
          {task.title}
        </h3>
        <span className="task-card__priority-score">
          {task.priorityScore.toFixed(1)}
        </span>
      </div>

      {!compact && (
        <div className="task-card__description">
          {task.description}
        </div>
      )}

      <div className="task-card__metadata">
        <div className="task-card__sla">
          <span className={`sla-status ${task.slaHoursRemaining < 4 ? 'critical' : ''}`}>
            ⏱️ {formatSLAStatus(task.slaHoursRemaining)}
          </span>
        </div>

        {showAssignee && task.assignedUser && (
          <div className="task-card__assignee">
            👤 {task.assignedUser.fullName}
          </div>
        )}

        <div className="task-card__work-group">
          🏢 {task.workGroup.name}
        </div>
      </div>

      {(canUpdate(task) || canReview(task)) && (
        <div className="task-card__actions">
          {task.status !== 'done' && (
            <button
              type="button"
              className="btn btn-primary btn-sm"
              disabled={isLoading}
              onClick={() => handleStatusChange(getNextStatus(task.status))}
            >
              {getNextStatusLabel(task.status)}
            </button>
          )}

          {canUpdate(task) && onEdit && (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => onEdit(task)}
            >
              Edit
            </button>
          )}
        </div>
      )}
    </div>
  );
};

// Helper functions
const getNextStatus = (currentStatus: TaskStatus): TaskStatus => {
  const statusFlow: Record<TaskStatus, TaskStatus> = {
    'backlog': 'in_progress',
    'in_progress': 'review',
    'review': 'done',
    'done': 'done'
  };
  return statusFlow[currentStatus];
};

const getNextStatusLabel = (currentStatus: TaskStatus): string => {
  const labels: Record<TaskStatus, string> = {
    'backlog': 'Start',
    'in_progress': 'Review',
    'review': 'Complete',
    'done': 'Done'
  };
  return labels[currentStatus];
};

export default TaskCard;
```

#### TypeScript Standards
```typescript
// File: src/types/task.ts
export interface Task {
  readonly id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priorityScore: number;
  priorityFactors: PriorityFactors;
  difficultyLevel: number; // 1-5
  businessImpact: number;  // 1-5
  estimatedHours?: number;
  actualHours?: number;
  plannedStartDate?: Date;
  plannedEndDate?: Date;
  actualStartDate?: Date;
  actualEndDate?: Date;
  slaTargetHours?: number;
  slaHoursRemaining: number;
  assignedUser?: User;
  createdBy: User;
  workGroup: WorkGroup;
  kpiAlignments: string[];
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}

export type TaskStatus = 'backlog' | 'in_progress' | 'review' | 'done' | 'cancelled';

export interface PriorityFactors {
  deadlineUrgency: number;
  slaRisk: number;
  businessImpact: number;
  kpiAlignment: number;
  difficulty: number;
}

export interface TaskCreate {
  title: string;
  description?: string;
  workGroupId: string;
  difficultyLevel: number;
  businessImpact: number;
  estimatedHours?: number;
  plannedStartDate?: Date;
  plannedEndDate?: Date;
  slaTargetHours?: number;
  kpiAlignments?: string[];
  tags?: string[];
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priorityScore?: number;
  difficultyLevel?: number;
  businessImpact?: number;
  estimatedHours?: number;
  actualHours?: number;
  plannedStartDate?: Date;
  plannedEndDate?: Date;
  actualStartDate?: Date;
  actualEndDate?: Date;
  kpiAlignments?: string[];
  tags?: string[];
}

// API Response types
export interface TaskResponse {
  data: Task;
  metadata: {
    timestamp: string;
    version: string;
    requestId: string;
  };
}

export interface TaskListResponse {
  data: Task[];
  pagination: {
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
  };
  metadata: {
    timestamp: string;
    version: string;
    requestId: string;
  };
}
```

---

## Error Handling Standards

### Backend Error Handling
```python
# Custom exception classes
class IRMSException(Exception):
    """Base exception class for IRMS application."""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(IRMSException):
    """Raised when data validation fails."""
    pass

class PermissionError(IRMSException):
    """Raised when user lacks required permissions."""
    pass

class BusinessRuleError(IRMSException):
    """Raised when business rule validation fails."""
    pass

# Global exception handler
@app.exception_handler(IRMSException)
async def irms_exception_handler(request: Request, exc: IRMSException):
    """Global exception handler for IRMS-specific exceptions."""
    await audit_service.log_event(
        event_type="error.application",
        user_id=getattr(request.state, 'user_id', None),
        event_details={
            "error_type": exc.__class__.__name__,
            "error_message": exc.message,
            "error_code": exc.error_code,
            "endpoint": str(request.url),
            "method": request.method
        }
    )

    status_code = {
        ValidationError: 422,
        PermissionError: 403,
        BusinessRuleError: 400
    }.get(type(exc), 500)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "code": exc.error_code,
                "timestamp": datetime.now().isoformat(),
                "request_id": request.state.request_id
            }
        }
    )
```

### Frontend Error Handling
```typescript
// Error handling service
export class ErrorHandler {
  private static instance: ErrorHandler;
  private auditService: AuditService;

  static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  async handleError(error: unknown, context?: string): Promise<void> {
    const errorInfo = this.parseError(error);

    // Log to audit trail
    await this.auditService.logClientError({
      type: errorInfo.type,
      message: errorInfo.message,
      context: context,
      stack: errorInfo.stack,
      timestamp: new Date().toISOString()
    });

    // Show user-friendly message
    this.showUserMessage(errorInfo);

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Application Error:', errorInfo);
    }
  }

  private parseError(error: unknown): ErrorInfo {
    if (error instanceof APIError) {
      return {
        type: 'api_error',
        message: error.message,
        code: error.code,
        stack: error.stack
      };
    }

    if (error instanceof NetworkError) {
      return {
        type: 'network_error',
        message: 'Connection problem. Please check your internet connection.',
        code: 'NETWORK_ERROR',
        stack: error.stack
      };
    }

    return {
      type: 'unknown_error',
      message: 'An unexpected error occurred. Please try again.',
      code: 'UNKNOWN_ERROR',
      stack: error instanceof Error ? error.stack : undefined
    };
  }

  private showUserMessage(errorInfo: ErrorInfo): void {
    // Integration with toast/notification system
    NotificationService.error(errorInfo.message);
  }
}

// Usage in components
const handleTaskUpdate = async (taskId: string, updates: TaskUpdate) => {
  try {
    await taskService.updateTask(taskId, updates);
    NotificationService.success('Task updated successfully');
  } catch (error) {
    await ErrorHandler.getInstance().handleError(error, 'task_update');
  }
};
```

---

## Testing Standards

### Backend Testing
```python
# Test file: tests/services/test_task_service.py
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, Mock
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate
from app.models.task import Task
from app.models.user import User, UserRole

@pytest.fixture
async def task_service():
    """Create TaskService instance with mocked dependencies."""
    mock_db = AsyncMock()
    mock_audit = AsyncMock()
    return TaskService(mock_db, mock_audit)

@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id=uuid4(),
        employee_id="EMP001",
        email="test@company.com",
        full_name="Test User",
        role=UserRole.SENIOR_AUDITOR,
        active=True
    )

@pytest.fixture
def sample_task_data():
    """Create sample task data for testing."""
    return TaskCreate(
        title="Test Task",
        description="Test task description",
        work_group_id=uuid4(),
        difficulty_level=3,
        business_impact=4,
        estimated_hours=8.0,
        sla_target_hours=24
    )

@pytest.mark.asyncio
async def test_create_task_success(task_service, sample_user, sample_task_data):
    """Test successful task creation."""
    # Arrange
    expected_task = Task(**sample_task_data.dict(), created_by_user_id=sample_user.id)
    task_service.db.flush = AsyncMock()
    task_service.db.commit = AsyncMock()

    # Act
    result = await task_service.create_task(
        task_data=sample_task_data,
        created_by=sample_user.id,
        current_user=sample_user
    )

    # Assert
    assert result.title == sample_task_data.title
    assert result.description == sample_task_data.description
    task_service.db.add.assert_called_once()
    task_service.db.flush.assert_called_once()
    task_service.db.commit.assert_called_once()
    task_service.audit.log_event.assert_called_once()

@pytest.mark.asyncio
async def test_create_task_permission_denied(task_service, sample_task_data):
    """Test task creation with insufficient permissions."""
    # Arrange
    unauthorized_user = User(
        id=uuid4(),
        role=UserRole.AUDIT_ASSISTANT,  # Doesn't have task:create permission
        active=True
    )

    # Act & Assert
    with pytest.raises(PermissionError):
        await task_service.create_task(
            task_data=sample_task_data,
            created_by=unauthorized_user.id,
            current_user=unauthorized_user
        )

    # Verify no database operations occurred
    task_service.db.add.assert_not_called()
    task_service.db.commit.assert_not_called()
```

### Frontend Testing
```typescript
// Test file: src/components/TaskCard/__tests__/TaskCard.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { TaskCard } from '../TaskCard';
import { Task, TaskStatus } from '../../../types/task';
import * as PermissionsHook from '../../../hooks/usePermissions';
import * as AuditHook from '../../../hooks/useAuditTrail';

// Mock dependencies
jest.mock('../../../hooks/usePermissions');
jest.mock('../../../hooks/useAuditTrail');

const mockTask: Task = {
  id: 'task-123',
  title: 'Test Task',
  description: 'Test task description',
  status: 'in_progress',
  priorityScore: 75.5,
  priorityFactors: {
    deadlineUrgency: 80,
    slaRisk: 70,
    businessImpact: 75,
    kpiAlignment: 60,
    difficulty: 65
  },
  difficultyLevel: 3,
  businessImpact: 4,
  slaHoursRemaining: 12,
  assignedUser: {
    id: 'user-123',
    fullName: 'John Doe',
    role: 'senior_auditor'
  },
  createdBy: {
    id: 'user-456',
    fullName: 'Jane Smith',
    role: 'department_head'
  },
  workGroup: {
    id: 'group-123',
    name: 'Core Audit'
  },
  kpiAlignments: ['effectiveness', 'quality'],
  tags: ['urgent', 'compliance'],
  createdAt: new Date('2025-01-01T10:00:00Z'),
  updatedAt: new Date('2025-01-01T14:00:00Z')
};

describe('TaskCard Component', () => {
  const mockOnStatusChange = jest.fn();
  const mockOnEdit = jest.fn();
  const mockCanUpdate = jest.fn();
  const mockCanReview = jest.fn();
  const mockLogUserAction = jest.fn();

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Setup hook mocks
    (PermissionsHook.usePermissions as jest.Mock).mockReturnValue({
      canUpdate: mockCanUpdate,
      canReview: mockCanReview
    });

    (AuditHook.useAuditTrail as jest.Mock).mockReturnValue({
      logUserAction: mockLogUserAction
    });
  });

  test('renders task information correctly', () => {
    render(
      <TaskCard
        task={mockTask}
        onStatusChange={mockOnStatusChange}
        onEdit={mockOnEdit}
      />
    );

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('Test task description')).toBeInTheDocument();
    expect(screen.getByText('75.5')).toBeInTheDocument(); // Priority score
    expect(screen.getByText('👤 John Doe')).toBeInTheDocument();
    expect(screen.getByText('🏢 Core Audit')).toBeInTheDocument();
  });

  test('displays correct SLA status', () => {
    render(<TaskCard task={mockTask} />);
    expect(screen.getByText('⏱️ 12h remaining')).toBeInTheDocument();
  });

  test('handles status change correctly', async () => {
    mockCanUpdate.mockReturnValue(true);

    render(
      <TaskCard
        task={mockTask}
        onStatusChange={mockOnStatusChange}
      />
    );

    const statusButton = screen.getByText('Review');
    fireEvent.click(statusButton);

    await waitFor(() => {
      expect(mockOnStatusChange).toHaveBeenCalledWith('task-123', 'review');
    });

    expect(mockLogUserAction).toHaveBeenCalledWith('task_status_change', {
      taskId: 'task-123',
      oldStatus: 'in_progress',
      newStatus: 'review'
    });
  });

  test('hides actions when user lacks permissions', () => {
    mockCanUpdate.mockReturnValue(false);
    mockCanReview.mockReturnValue(false);

    render(
      <TaskCard
        task={mockTask}
        onStatusChange={mockOnStatusChange}
        onEdit={mockOnEdit}
      />
    );

    expect(screen.queryByText('Review')).not.toBeInTheDocument();
    expect(screen.queryByText('Edit')).not.toBeInTheDocument();
  });

  test('renders in compact mode correctly', () => {
    render(<TaskCard task={mockTask} compact={true} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.queryByText('Test task description')).not.toBeInTheDocument();
  });
});
```

---

## Performance Standards

### Code Performance Guidelines
```python
# Database query optimization
class TaskQueryOptimizer:
    @staticmethod
    async def get_user_tasks_optimized(db: AsyncSession, user_id: UUID) -> List[Task]:
        """Optimized query for user tasks with minimal N+1 queries."""
        query = (
            select(Task)
            .options(
                selectinload(Task.assigned_user),
                selectinload(Task.work_group),
                selectinload(Task.created_by)
            )
            .where(Task.assigned_user_id == user_id)
            .where(Task.status != 'cancelled')
            .order_by(Task.priority_score.desc())
        )

        result = await db.execute(query)
        return result.scalars().unique().all()

    @staticmethod
    def build_dashboard_query(user_role: UserRole, user_id: UUID):
        """Build optimized dashboard query based on user role."""
        base_query = select(Task)

        if user_role in [UserRole.AUDIT_ASSISTANT]:
            # Only personal tasks
            base_query = base_query.where(Task.assigned_user_id == user_id)
        elif user_role == UserRole.SENIOR_AUDITOR:
            # Personal + team tasks
            base_query = base_query.where(
                or_(
                    Task.assigned_user_id == user_id,
                    Task.assigned_user_id.in_(
                        select(User.id).where(User.manager_id == user_id)
                    )
                )
            )
        elif user_role in [UserRole.DEPARTMENT_HEAD, UserRole.LEADERSHIP]:
            # Department/organization-wide tasks
            pass  # No additional filtering needed

        return base_query
```

### Frontend Performance Standards
```typescript
// React performance optimization patterns
export const KanbanBoard = React.memo<KanbanBoardProps>(({
  tasks,
  onTaskMove,
  userRole
}) => {
  // Memoize expensive calculations
  const tasksByStatus = useMemo(() => {
    return tasks.reduce((acc, task) => {
      if (!acc[task.status]) acc[task.status] = [];
      acc[task.status].push(task);
      return acc;
    }, {} as Record<TaskStatus, Task[]>);
  }, [tasks]);

  // Memoize column configuration
  const columns = useMemo(() => {
    return getColumnsForRole(userRole);
  }, [userRole]);

  // Debounced task move handler
  const debouncedTaskMove = useCallback(
    debounce(async (taskId: string, newStatus: TaskStatus) => {
      await onTaskMove(taskId, newStatus);
    }, 300),
    [onTaskMove]
  );

  return (
    <div className="kanban-board">
      {columns.map(column => (
        <KanbanColumn
          key={column.status}
          status={column.status}
          title={column.title}
          tasks={tasksByStatus[column.status] || []}
          onTaskMove={debouncedTaskMove}
        />
      ))}
    </div>
  );
});

// Virtualization for large lists
export const VirtualizedTaskList: React.FC<TaskListProps> = ({ tasks, itemHeight = 120 }) => {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: tasks.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => itemHeight,
    overscan: 5
  });

  return (
    <div ref={parentRef} className="task-list-container">
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map(virtualItem => (
          <div
            key={virtualItem.key}
            data-index={virtualItem.index}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`
            }}
          >
            <TaskCard task={tasks[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
};
```

This comprehensive coding standards document ensures consistent, maintainable, and performant code across the IRMS System development.