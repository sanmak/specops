# Feature: Task Management SaaS MVP

## Overview
Build a task management SaaS product that lets users create task boards, organize tasks with drag-and-drop, and collaborate in real-time. The MVP targets freelancers and small teams who need a lightweight alternative to Jira and Asana. Ships as a web application with React frontend, REST API backend, PostgreSQL database, and Docker-based deployment.

## Product Requirements

### Requirement 1: Task Board Management
**As a** user
**I want** to create, rename, and delete task boards
**So that** I can organize work by project or team

**Acceptance Criteria:**
- [ ] User can create a new board with a name and optional description
- [ ] User can rename and delete boards they own
- [ ] Boards display as a Kanban view with configurable columns (default: To Do, In Progress, Done)
- [ ] Board list shows all boards the user has access to, sorted by last activity

### Requirement 2: Task CRUD with Drag-and-Drop
**As a** user
**I want** to create, edit, move, and delete tasks within a board
**So that** I can track work items and their progress

**Acceptance Criteria:**
- [ ] User can create a task with title, description, assignee, and due date
- [ ] Tasks can be dragged between columns to update status
- [ ] Drag-and-drop state persists immediately (optimistic UI with server sync)
- [ ] Tasks display a compact card view with title, assignee avatar, and due date indicator

### Requirement 3: User Authentication
**As a** visitor
**I want** to sign up and log in to access my boards
**So that** my data is private and persistent across sessions

**Acceptance Criteria:**
- [ ] User can register with email and password
- [ ] User can log in and receive a JWT token
- [ ] Protected routes redirect unauthenticated users to login
- [ ] Password is hashed with bcrypt before storage

### Requirement 4: Real-Time Updates
**As a** team member
**I want** to see changes from other users appear instantly
**So that** the board always reflects the current state without manual refresh

**Acceptance Criteria:**
- [ ] Board updates (task created, moved, edited, deleted) broadcast to all connected clients
- [ ] WebSocket connection established on board view, cleaned up on navigation
- [ ] Reconnection handled gracefully on network interruption

## Scope Boundary

**Ships in v1 (MVP):**
- Task boards with Kanban columns
- Task CRUD with drag-and-drop
- Email/password authentication
- Real-time board updates via WebSocket
- Single-user and shared boards (invite by email)
- Docker Compose deployment to a single VPS
- Basic CI pipeline (lint, test, build)

**Deferred (post-MVP):**
- OAuth providers (Google, GitHub)
- File attachments on tasks
- Activity log / audit trail
- Mobile-responsive layout optimization
- Custom fields on tasks
- Team management and roles (admin, member, viewer)
- Automated cloud deployment (Kubernetes, auto-scaling)
- Email notifications
- Search and filtering across boards

## Product Quality Attributes
- **Performance:** Board loads in < 2 seconds with up to 200 tasks; drag-and-drop responds in < 100ms
- **Reliability:** Server uptime target 99% (acceptable for MVP); data not lost on server restart (PostgreSQL persistence)
- **Security:** Passwords hashed, JWT tokens with expiry, SQL injection prevention via parameterized queries
- **Cost:** Infrastructure cost < $20/month on a single VPS for MVP traffic (< 100 concurrent users)

## Constraints & Assumptions
- Solo builder; no dedicated design, QA, or DevOps support
- Target deployment: single Docker Compose stack on a VPS (DigitalOcean, Hetzner, or similar)
- No mobile app in v1 — web-only, desktop-first
- PostgreSQL chosen for relational data and JSONB flexibility
- React chosen based on builder familiarity; no SSR needed for MVP

## Success Metrics
- Working product deployed and accessible via public URL within 2 weeks
- At least 5 beta users onboarded within first month
- Core flow (create board, add tasks, drag between columns) works end-to-end without errors
