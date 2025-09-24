# Database Schema
## IRMS System - Internal Audit Webapp

**Component**: Data Architecture and Database Design
**For**: Development Team Database Implementation
**Priority**: Phase 1A - Week 1 (Critical Foundation)

---

## Database Technology and Configuration

### PostgreSQL 15+ Configuration
```sql
-- Database creation with optimal settings
CREATE DATABASE irms_audit
  WITH OWNER = irms_user
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       CONNECTION LIMIT = 100;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For JSONB indexing
```

### Connection Configuration
```python
# Database configuration for development
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "irms_audit",
    "username": "irms_user",
    "password": "secure_password",
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "echo": False,  # Set to True for SQL debugging
}
```

---

## Core Database Schema (Phase 1A)

### User Management Schema

#### Users Table
```sql
CREATE TYPE user_role_enum AS ENUM (
    'audit_assistant',
    'senior_auditor',
    'department_head',
    'leadership'
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role_enum NOT NULL,
    department_id UUID REFERENCES departments(id),
    manager_id UUID REFERENCES users(id),
    skills JSONB DEFAULT '[]'::jsonb,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_employee_id_format CHECK (employee_id ~ '^[A-Z0-9]{3,10}$')
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_employee_id ON users(employee_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_department ON users(department_id);
CREATE INDEX idx_users_manager ON users(manager_id);
CREATE INDEX idx_users_active ON users(active) WHERE active = true;
CREATE INDEX idx_users_skills_gin ON users USING gin(skills);
```

#### Departments Table
```sql
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    head_user_id UUID REFERENCES users(id),
    budget_code VARCHAR(20),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_departments_name ON departments(name);
CREATE INDEX idx_departments_head ON departments(head_user_id);
CREATE INDEX idx_departments_active ON departments(active) WHERE active = true;
```

---

### Task Management Schema

#### Tasks Table (Core Entity)
```sql
CREATE TYPE task_status_enum AS ENUM (
    'backlog',
    'in_progress',
    'review',
    'done',
    'cancelled'
);

CREATE TYPE task_priority_enum AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    work_group_id UUID REFERENCES work_groups(id),
    assigned_user_id UUID REFERENCES users(id),
    created_by_user_id UUID REFERENCES users(id) NOT NULL,
    reviewed_by_user_id UUID REFERENCES users(id),

    -- Status and priority
    status task_status_enum NOT NULL DEFAULT 'backlog',
    priority task_priority_enum NOT NULL DEFAULT 'medium',
    priority_score DECIMAL(5,2) DEFAULT 0.00,
    priority_factors JSONB DEFAULT '{}'::jsonb,

    -- Effort and difficulty
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
    business_impact INTEGER CHECK (business_impact BETWEEN 1 AND 5),
    estimated_hours DECIMAL(5,2),
    actual_hours DECIMAL(5,2),

    -- Scheduling
    planned_start_date DATE,
    planned_end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,
    sla_target_hours INTEGER,

    -- KPI and metadata
    kpi_alignments JSONB DEFAULT '[]'::jsonb,
    tags TEXT[],
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_date_logic CHECK (
        planned_end_date IS NULL OR
        planned_start_date IS NULL OR
        planned_end_date >= planned_start_date
    ),
    CONSTRAINT chk_actual_dates CHECK (
        actual_end_date IS NULL OR
        actual_start_date IS NULL OR
        actual_end_date >= actual_start_date
    ),
    CONSTRAINT chk_priority_score_range CHECK (priority_score >= 0 AND priority_score <= 100)
);

-- Performance indexes
CREATE INDEX idx_tasks_assigned_user ON tasks(assigned_user_id);
CREATE INDEX idx_tasks_created_by ON tasks(created_by_user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority, priority_score DESC);
CREATE INDEX idx_tasks_work_group ON tasks(work_group_id);
CREATE INDEX idx_tasks_dates ON tasks(planned_start_date, planned_end_date);
CREATE INDEX idx_tasks_sla_monitoring ON tasks(sla_target_hours, planned_end_date, status)
    WHERE status IN ('in_progress', 'review');
CREATE INDEX idx_tasks_kpi_alignments ON tasks USING gin(kpi_alignments);
CREATE INDEX idx_tasks_tags ON tasks USING gin(tags);
CREATE INDEX idx_tasks_updated_at ON tasks(updated_at DESC);

-- Full-text search index
CREATE INDEX idx_tasks_search ON tasks USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));
```

#### Work Groups Table
```sql
CREATE TABLE work_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    department_id UUID REFERENCES departments(id) NOT NULL,
    kpi_framework JSONB NOT NULL DEFAULT '{}'::jsonb,
    lead_user_id UUID REFERENCES users(id),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uk_work_group_name_dept UNIQUE (name, department_id)
);

CREATE INDEX idx_work_groups_department ON work_groups(department_id);
CREATE INDEX idx_work_groups_lead ON work_groups(lead_user_id);
CREATE INDEX idx_work_groups_active ON work_groups(active) WHERE active = true;
CREATE INDEX idx_work_groups_kpi_framework ON work_groups USING gin(kpi_framework);
```

---

### KPI Management Schema

#### KPI Definitions Table
```sql
CREATE TYPE kpi_calculation_method AS ENUM (
    'automatic',
    'manual',
    'hybrid'
);

CREATE TABLE kpi_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL, -- 'effectiveness', 'innovation', 'development'
    subcategory VARCHAR(100),
    weight DECIMAL(5,2) NOT NULL CHECK (weight >= 0 AND weight <= 100),
    calculation_method kpi_calculation_method NOT NULL DEFAULT 'automatic',
    calculation_formula JSONB,
    target_value DECIMAL(10,2),
    unit VARCHAR(50), -- '%', 'hours', 'count', etc.
    work_group_id UUID REFERENCES work_groups(id),
    active BOOLEAN DEFAULT true,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_weight_valid CHECK (weight >= 0 AND weight <= 100)
);

CREATE INDEX idx_kpi_definitions_category ON kpi_definitions(category, subcategory);
CREATE INDEX idx_kpi_definitions_work_group ON kpi_definitions(work_group_id);
CREATE INDEX idx_kpi_definitions_active ON kpi_definitions(active) WHERE active = true;
CREATE INDEX idx_kpi_definitions_method ON kpi_definitions(calculation_method);
```

#### KPI Scores Table (Phase 1A: Monthly periods)
```sql
CREATE TABLE kpi_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    kpi_definition_id UUID REFERENCES kpi_definitions(id) NOT NULL,
    score_period DATE NOT NULL, -- Monthly periods (YYYY-MM-01)

    -- Scoring
    calculated_score DECIMAL(5,2),
    manual_score DECIMAL(5,2),
    final_score DECIMAL(5,2) NOT NULL,
    target_score DECIMAL(5,2),

    -- Metadata
    calculation_details JSONB DEFAULT '{}'::jsonb,
    notes TEXT,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    locked BOOLEAN DEFAULT false,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uk_kpi_scores_user_period UNIQUE (user_id, kpi_definition_id, score_period),
    CONSTRAINT chk_kpi_score_range CHECK (final_score >= 0 AND final_score <= 100),
    CONSTRAINT chk_calculated_score_range CHECK (calculated_score IS NULL OR (calculated_score >= 0 AND calculated_score <= 100)),
    CONSTRAINT chk_manual_score_range CHECK (manual_score IS NULL OR (manual_score >= 0 AND manual_score <= 100))
);

-- Performance indexes for KPI queries
CREATE INDEX idx_kpi_scores_user_period ON kpi_scores(user_id, score_period DESC);
CREATE INDEX idx_kpi_scores_definition ON kpi_scores(kpi_definition_id);
CREATE INDEX idx_kpi_scores_period ON kpi_scores(score_period DESC);
CREATE INDEX idx_kpi_scores_final_score ON kpi_scores(final_score DESC);
CREATE INDEX idx_kpi_scores_reviewed ON kpi_scores(reviewed_by, reviewed_at);
CREATE INDEX idx_kpi_scores_updated_at ON kpi_scores(updated_at DESC);

-- Partial index for unlocked scores (for ongoing calculations)
CREATE INDEX idx_kpi_scores_unlocked ON kpi_scores(user_id, score_period) WHERE locked = false;
```

---

### Assignment and Workload Schema

#### Assignments Table
```sql
CREATE TYPE assignment_status AS ENUM (
    'suggested',
    'approved',
    'active',
    'completed',
    'cancelled'
);

CREATE TABLE assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) NOT NULL,
    user_id UUID REFERENCES users(id) NOT NULL,
    assigned_by UUID REFERENCES users(id) NOT NULL,

    -- Assignment scoring
    assignment_score DECIMAL(5,2),
    scoring_factors JSONB DEFAULT '{}'::jsonb,
    alternative_candidates JSONB DEFAULT '[]'::jsonb,

    -- Status and workflow
    status assignment_status NOT NULL DEFAULT 'suggested',
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_assignment_score_range CHECK (assignment_score >= 0 AND assignment_score <= 100)
);

CREATE INDEX idx_assignments_task ON assignments(task_id);
CREATE INDEX idx_assignments_user ON assignments(user_id);
CREATE INDEX idx_assignments_assigned_by ON assignments(assigned_by);
CREATE INDEX idx_assignments_status ON assignments(status);
CREATE INDEX idx_assignments_approved ON assignments(approved_by, approved_at);
CREATE INDEX idx_assignments_score ON assignments(assignment_score DESC);
```

#### Workload Snapshots Table
```sql
CREATE TYPE workload_alert_level AS ENUM (
    'green',   -- < 80% capacity
    'yellow',  -- 80-95% capacity
    'red'      -- > 95% capacity
);

CREATE TABLE workload_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,

    -- Workload calculations
    total_estimated_hours DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    weekly_capacity_hours DECIMAL(5,2) NOT NULL DEFAULT 40.00,
    capacity_percentage DECIMAL(5,2) NOT NULL,
    active_tasks_count INTEGER NOT NULL DEFAULT 0,
    overdue_tasks_count INTEGER NOT NULL DEFAULT 0,

    -- Alert information
    alert_level workload_alert_level NOT NULL,
    alert_triggered BOOLEAN DEFAULT false,
    alert_acknowledged_at TIMESTAMPTZ,

    -- Calculation details
    calculation_details JSONB DEFAULT '{}'::jsonb,
    snapshot_time TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_capacity_percentage CHECK (capacity_percentage >= 0)
);

-- Indexes for workload monitoring
CREATE INDEX idx_workload_user_time ON workload_snapshots(user_id, snapshot_time DESC);
CREATE INDEX idx_workload_alert_level ON workload_snapshots(alert_level);
CREATE INDEX idx_workload_alert_triggered ON workload_snapshots(alert_triggered) WHERE alert_triggered = true;
CREATE INDEX idx_workload_capacity ON workload_snapshots(capacity_percentage DESC);
CREATE INDEX idx_workload_snapshot_time ON workload_snapshots(snapshot_time DESC);
```

---

### Audit Trail Schema

#### Audit Log Table (Compliance Critical)
```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    user_id UUID REFERENCES users(id),
    session_id VARCHAR(255),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,

    -- Resource information
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    action VARCHAR(50) NOT NULL,

    -- Data snapshots for compliance
    before_data JSONB,
    after_data JSONB,
    event_details JSONB DEFAULT '{}'::jsonb,

    -- Compliance and correlation
    correlation_id UUID,
    compliance_tags TEXT[] DEFAULT '{}',
    retention_date DATE NOT NULL,

    -- Immutability check
    checksum VARCHAR(64) -- SHA-256 hash for integrity verification
);

-- Critical indexes for audit queries
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_log_user_timestamp ON audit_log(user_id, timestamp DESC);
CREATE INDEX idx_audit_log_event_type ON audit_log(event_type, timestamp DESC);
CREATE INDEX idx_audit_log_resource ON audit_log(resource_type, resource_id);
CREATE INDEX idx_audit_log_compliance_tags ON audit_log USING gin(compliance_tags);
CREATE INDEX idx_audit_log_session ON audit_log(session_id);
CREATE INDEX idx_audit_log_correlation ON audit_log(correlation_id);

-- Compliance retention index
CREATE INDEX idx_audit_log_retention ON audit_log(retention_date) WHERE retention_date > CURRENT_DATE;
```

---

### Database Partitioning Strategy (Performance)

#### Partition Audit Log by Month
```sql
-- Create partitioned audit_log table for performance
CREATE TABLE audit_log_partitioned (LIKE audit_log INCLUDING ALL)
PARTITION BY RANGE (timestamp);

-- Create monthly partitions (example for 2025)
CREATE TABLE audit_log_y2025m01 PARTITION OF audit_log_partitioned
    FOR VALUES FROM ('2025-01-01 00:00:00') TO ('2025-02-01 00:00:00');

CREATE TABLE audit_log_y2025m02 PARTITION OF audit_log_partitioned
    FOR VALUES FROM ('2025-02-01 00:00:00') TO ('2025-03-01 00:00:00');

-- Automated partition creation function
CREATE OR REPLACE FUNCTION create_monthly_partition(table_name text, start_date date)
RETURNS void AS $$
DECLARE
    partition_name text;
    end_date date;
BEGIN
    partition_name := table_name || '_y' || TO_CHAR(start_date, 'YYYY') || 'm' || TO_CHAR(start_date, 'MM');
    end_date := start_date + INTERVAL '1 month';

    EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF %I
                    FOR VALUES FROM (%L) TO (%L)',
                   partition_name, table_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;
```

---

## Data Integrity and Business Rules

### Database Constraints and Triggers

#### Updated At Trigger
```sql
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables with updated_at column
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_kpi_scores_updated_at BEFORE UPDATE ON kpi_scores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### Business Rule Constraints
```sql
-- Task assignment constraint
ALTER TABLE tasks ADD CONSTRAINT chk_task_assignment_logic
    CHECK (
        (status = 'backlog' AND assigned_user_id IS NULL) OR
        (status IN ('in_progress', 'review', 'done') AND assigned_user_id IS NOT NULL)
    );

-- KPI score validation
ALTER TABLE kpi_scores ADD CONSTRAINT chk_kpi_manual_score_logic
    CHECK (
        (manual_score IS NULL) OR
        (manual_score IS NOT NULL AND calculated_score IS NOT NULL)
    );

-- SLA target validation
ALTER TABLE tasks ADD CONSTRAINT chk_sla_target_positive
    CHECK (sla_target_hours IS NULL OR sla_target_hours > 0);

-- Workload capacity validation
ALTER TABLE workload_snapshots ADD CONSTRAINT chk_capacity_realistic
    CHECK (capacity_percentage <= 200); -- Allow up to 200% for emergency situations
```

---

## Database Performance Optimization

### Query Performance Configuration
```sql
-- PostgreSQL configuration for optimal performance
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Reload configuration
SELECT pg_reload_conf();
```

### Materialized Views for Dashboard Performance
```sql
-- User dashboard performance view
CREATE MATERIALIZED VIEW mv_user_dashboard_stats AS
SELECT
    u.id as user_id,
    u.full_name,
    u.role,
    COUNT(t.id) as total_tasks,
    COUNT(CASE WHEN t.status = 'done' THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN t.status = 'in_progress' THEN 1 END) as active_tasks,
    COUNT(CASE WHEN t.actual_end_date > (t.planned_start_date + INTERVAL '1 hour' * t.sla_target_hours)
          THEN 1 END) as sla_breaches,
    COALESCE(AVG(k.final_score), 0) as avg_kpi_score,
    MAX(t.updated_at) as last_task_update
FROM users u
LEFT JOIN tasks t ON u.id = t.assigned_user_id
    AND t.created_at > NOW() - INTERVAL '3 months'
LEFT JOIN kpi_scores k ON u.id = k.user_id
    AND k.score_period > (CURRENT_DATE - INTERVAL '6 months')
WHERE u.active = true
GROUP BY u.id, u.full_name, u.role;

-- Create index on materialized view
CREATE UNIQUE INDEX idx_mv_user_dashboard_stats_user ON mv_user_dashboard_stats(user_id);
CREATE INDEX idx_mv_user_dashboard_stats_role ON mv_user_dashboard_stats(role);
CREATE INDEX idx_mv_user_dashboard_stats_kpi ON mv_user_dashboard_stats(avg_kpi_score DESC);

-- Refresh materialized view function
CREATE OR REPLACE FUNCTION refresh_dashboard_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_user_dashboard_stats;
    -- Log refresh for monitoring
    INSERT INTO audit_log (event_type, action, event_details)
    VALUES ('system.materialized_view.refresh', 'refresh',
            '{"view": "mv_user_dashboard_stats", "timestamp": "' || NOW()::text || '"}');
END;
$$ LANGUAGE plpgsql;
```

---

## Database Setup and Migration Scripts

### Initial Database Setup Script
```bash
#!/bin/bash
# setup_database.sh

# Create database user
sudo -u postgres createuser --createdb --login irms_user

# Set password
sudo -u postgres psql -c "ALTER USER irms_user PASSWORD 'secure_password_here';"

# Create database
sudo -u postgres createdb -O irms_user irms_audit

# Run initial schema
psql -U irms_user -d irms_audit -f schema/01_extensions.sql
psql -U irms_user -d irms_audit -f schema/02_enums.sql
psql -U irms_user -d irms_audit -f schema/03_tables.sql
psql -U irms_user -d irms_audit -f schema/04_indexes.sql
psql -U irms_user -d irms_audit -f schema/05_constraints.sql
psql -U irms_user -d irms_audit -f schema/06_functions.sql
psql -U irms_user -d irms_audit -f schema/07_triggers.sql
psql -U irms_user -d irms_audit -f schema/08_partitions.sql
psql -U irms_user -d irms_audit -f schema/09_materialized_views.sql

echo "Database setup complete!"
```

This database schema provides a robust foundation for the IRMS System with focus on performance, compliance, and scalability requirements for Phase 1A development.