# Project Brief – Internal Audit Webapp

## 1. Executive Summary

The project aims to develop a **web application for the Internal Audit Department**, focusing on task management, staff assignment, SLA monitoring, and KPI measurement. The system prioritizes being **simple, effective, customizable, and sustainable**. A Kanban view will be applied across all user roles, complemented by Calendar and Dashboard views to track progress, workloads, and KPI performance. The system will not handle file storage; it will focus purely on task and KPI management.

---

## 2. Problem Statement

* Current staff assignment is manual and not optimized for workload balance or KPI achievement.
* Difficulties in tracking multiple concurrent audit activities (audit missions, core audit projects, ad-hoc tasks).
* Individual KPIs are not strongly linked to departmental and organizational KPIs.
* Lack of SLA monitoring and workload alerts.
* Reporting is mostly manual and not sufficiently visual or real-time.

---

## 3. Proposed Solution

### 3.1 Task Management

* **Kanban View for all roles** (Backlog → In Progress → Review → Done).
* **Calendar View**: display concurrent tasks, showing overlaps; planned vs. actual start and end dates for every task.
* **Priority Hint**: system calculates task order based on multiple weighted factors: deadline urgency, SLA risk, difficulty, business impact, and KPI alignment.
* **Task metadata**: title, planned/actual start & end, SLA target, difficulty, assignee, group, KPI link.

### 3.2 Assignment Engine

* **Rule-based staff suggestions** (criteria: workload, KPI gap, skills, department, experience, and rotation for newer auditors).
* Multiple candidates displayed with scoring.
* Final approval always by Department Head or Leadership.
* Alerts when workload exceeds defined thresholds; qualitative warnings when risk of overload is detected.

### 3.3 Work Group Customization

* Custom creation of work groups (Audit missions, Core Audit, Ad-hoc, Training).
* Each group linked to a specific KPI framework.
* Fully configurable to adapt to organizational strategy.

### 3.4 KPI Engine

* **Fixed KPI framework for the year** (as defined by the Internal Audit Department).
* **Automatic scoring**: based on completed tasks, SLA performance, and surveys.
* **Manual scoring**: for qualitative KPIs (quality of audit programs, internal service quality).
* **Review cycle**: every 6 months, specifically in **January and July**.
* **Career Path Suggestions**: KPI tracking used to suggest development and promotion paths.
* **Peer review**: auditors provide scoring for each other; integrated as a supporting metric for leadership decisions, not decisive.

### 3.5 SLA & Monitoring

* SLA dashboard: traffic-light style (green/yellow/red per task).
* Workload charts per individual (stacked bar view, effort vs. capacity); overload warnings when thresholds exceeded.
* Lead/lag charts comparing planned vs. actual dates.
* Throughput and cycle time metrics.

### 3.6 Reporting & Dashboard

* Unified Kanban + Calendar synchronization.
* KPI dashboards at individual, departmental, and organizational levels.
* SLA dashboard with alerts.
* Explicit reporting on concurrent tasks being executed in a given timeframe.
* Export options for PDF and Excel reports.

---

## 4. Role Perspectives

* **Audit Assistant, Auditor Levels 1–3**: Kanban personal tasks, Calendar view, priority hints, progress updates.
* **Senior Auditor, Expert**: Kanban for team/mission, review tasks, consolidate findings.
* **Department Heads**: Kanban for department, assignment approval, departmental KPI dashboard.
* **Leadership**: Organization-wide Kanban, consolidated KPI dashboard, approval of audit plans.

---

## 5. KPI Framework (Critical)

The KPI framework is central and mandatory to the system design.

### 5.1 Individual KPIs

* **Effectiveness & Quality (80%)**:

  1. Completion rate of personal audit plan.
  2. Quality of audit programs participated in.
  3. Completion rate of corrective actions (for operational/financial audit staff) or follow-up evaluations (for audit management staff).
  4. Quality of assigned action programs (evaluated by Department Head/Leadership).
  5. Internal service quality (measured via leadership satisfaction surveys).

* **Innovation & Digital Transformation (10%)**:

  1. Number of ideas contributed (minimum 2–3 per year, at least 50% implemented).
  2. New audit methods/process improvements proposed and implemented.
  3. Quality of innovation ideas (evaluated via surveys or leadership assessment).

* **Personal Development (10%)**:

  1. Number of training hours completed annually (tracked via training office, self-initiated courses, certifications).
  2. Contribution to risk culture, digital transformation culture, and capacity building (hours spent training peers, participation rate in internal training).

### 5.2 Audit Mission KPIs

* Findings/Advisory Quality & Quantity (60%): number, importance, and risk level of findings documented.
* Task Timeliness (20%): completion time vs. target.
* Innovation & Digital Transformation (20%): application of digital tools, new metrics, or methodologies.
* Bonus/Malus Factors:

  * Stakeholder satisfaction survey: +1% KPI (80–90%), +2% (90–99%), +3% (100%), –1% (≤60%).
  * Contribution to team support tasks: +1–3%.
  * Alignment of findings with strategic direction: +1–3%.

---

## 6. Technical Considerations

* **Backend**: Python (FastAPI), SQLAlchemy.
* **Database**: PostgreSQL (with JSONB for KPI frameworks and task configs).
* **Frontend**: React (Kanban library, FullCalendar for scheduling).
* **Background jobs**: Celery/RQ with Redis (SLA recalculation, alerting).
* **Authentication**: OAuth2/JWT.
* **Deployment**: Cloud or on-premise.
* **Future updates**: AI-based staff assignment suggestions once sufficient data is available.

---

## 7. Risks & Mitigation

* **KPI complexity across departments** → solution: pre-defined templates with configurable fields.
* **Balancing qualitative vs. quantitative KPIs** → solution: automatic scoring plus manual override.
* **Change management and adoption** → solution: phased rollout, training for staff.
* **Integration needs (e.g., Jira, HR, LMS)** → addressed in later phases.
* **Scope creep with file storage** → explicitly excluded; system focuses on task and KPI management only.

---

## 8. Next Steps

1. Confirm MVP scope: Task Management (Kanban + Calendar), Assignment Engine (rule-based), KPI tracking (auto + manual), SLA dashboard, Priority Hint.
2. Build wireframes: Kanban, Calendar, KPI dashboard, SLA alerts, workload charts.
3. Develop prototype and conduct user testing with selected auditors and department heads.
4. Refine KPI engine and assignment logic based on feedback.
5. Full Phase 1 development (3–6 months).