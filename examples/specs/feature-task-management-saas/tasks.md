# Implementation Tasks: Task Management SaaS MVP

## Task Breakdown

### Task 1: Project Scaffolding and Database Schema
**Status:** Pending
**Estimated Effort:** S (2 hours)
**Dependencies:** None
**Priority:** High
**Domain:** backend, infra
**Ship Blocking:** Yes

**Description:**
Initialize the monorepo structure with backend (Express + TypeScript) and frontend (React + TypeScript) projects. Set up PostgreSQL schema with all tables from the design.

**Implementation Steps:**
1. Create `server/` directory with Express + TypeScript scaffold (tsconfig, package.json)
2. Create `client/` directory with Vite + React + TypeScript scaffold
3. Create `docker-compose.yml` with PostgreSQL service
4. Write SQL migration file with users, boards, board_members, columns, tasks tables
5. Add migration runner script

**Acceptance Criteria:**
- [ ] `docker compose up db` starts PostgreSQL with empty schema
- [ ] Migration script creates all tables with correct constraints
- [ ] TypeScript compiles in both server/ and client/

**Files to Create:**
- `docker-compose.yml`
- `server/package.json`, `server/tsconfig.json`, `server/src/index.ts`
- `client/package.json`, `client/tsconfig.json`, `client/src/main.tsx`
- `server/migrations/001-initial-schema.sql`
- `server/scripts/migrate.ts`

---

### Task 2: Auth Module (Register + Login + JWT Middleware)
**Status:** Pending
**Estimated Effort:** M (3 hours)
**Dependencies:** Task 1
**Priority:** High
**Domain:** backend
**Ship Blocking:** Yes

**Description:**
Implement user registration, login, and JWT middleware for protected routes.

**Implementation Steps:**
1. Create `server/src/modules/auth/routes.ts` with register and login endpoints
2. Implement password hashing with bcrypt (cost factor 12)
3. Implement JWT signing (HS256, 7-day expiry) and verification middleware
4. Create `GET /api/auth/me` endpoint to return current user from token
5. Add input validation (email format, password min length)
6. Write integration tests for register, login, and protected route access

**Acceptance Criteria:**
- [ ] `POST /api/auth/register` creates user with hashed password
- [ ] `POST /api/auth/login` returns JWT for valid credentials, 401 for invalid
- [ ] JWT middleware rejects requests without valid token
- [ ] `GET /api/auth/me` returns user profile from token
- [ ] Duplicate email registration returns 409

**Tests Required:**
- [ ] Register with valid credentials succeeds
- [ ] Register with duplicate email returns 409
- [ ] Login with correct password returns JWT
- [ ] Login with wrong password returns 401
- [ ] Protected route without token returns 401

---

### Task 3: Board and Task CRUD API
**Status:** Pending
**Estimated Effort:** M (4 hours)
**Dependencies:** Task 2
**Priority:** High
**Domain:** backend
**Ship Blocking:** Yes

**Description:**
Implement REST endpoints for board management (create, list, get, update, delete) and task management (create, update, move, delete). Board GET returns full board with columns and tasks.

**Implementation Steps:**
1. Create `server/src/modules/boards/routes.ts` with board CRUD
2. Create `server/src/modules/tasks/routes.ts` with task CRUD and move endpoint
3. Board creation auto-creates default columns (To Do, In Progress, Done)
4. Task move endpoint updates column_id and reorders positions atomically
5. Authorization: users can only access boards they own or are members of
6. Write integration tests

**Acceptance Criteria:**
- [ ] Board CRUD works end-to-end with auth
- [ ] `GET /api/boards/:id` returns board with nested columns and tasks
- [ ] `PATCH /api/tasks/:id/move` updates column and position atomically
- [ ] Users cannot access boards they are not members of (403)
- [ ] Default columns created on board creation

**Tests Required:**
- [ ] Board CRUD lifecycle (create, get, update, delete)
- [ ] Task CRUD lifecycle
- [ ] Task move between columns
- [ ] Authorization: non-member gets 403

---

### Task 4: React App Shell with Auth Pages
**Status:** Pending
**Estimated Effort:** M (3 hours)
**Dependencies:** Task 2
**Priority:** High
**Domain:** frontend
**Ship Blocking:** Yes

**Description:**
Build the React application shell with routing, login/register pages, and auth state management. Protected routes redirect to login.

**Implementation Steps:**
1. Set up React Router with public routes (/login, /register) and protected routes (/boards, /boards/:id)
2. Create auth context that stores JWT in localStorage and exposes login/logout/register functions
3. Build login and register form components with validation
4. Create a minimal layout component with navigation header and logout button
5. Add API client utility with automatic JWT header injection

**Acceptance Criteria:**
- [ ] Login and register pages render and submit to API
- [ ] Successful login stores JWT and redirects to /boards
- [ ] Protected routes redirect to /login when unauthenticated
- [ ] Logout clears JWT and redirects to /login

---

### Task 5: Kanban Board UI with Drag-and-Drop
**Status:** Pending
**Estimated Effort:** L (5 hours)
**Dependencies:** Task 3, Task 4
**Priority:** High
**Domain:** frontend
**Ship Blocking:** Yes

**Description:**
Build the Kanban board view with columns and task cards. Implement drag-and-drop using @hello-pangea/dnd with optimistic updates.

**Implementation Steps:**
1. Create BoardView component that fetches board data and renders columns
2. Create Column component with task card list
3. Create TaskCard component with title, assignee, and due date
4. Integrate @hello-pangea/dnd: DragDropContext wraps board, Droppable per column, Draggable per task
5. On drag end, optimistically reorder local state and call PATCH /api/tasks/:id/move
6. Revert local state if API call fails and show error toast
7. Add "Create Task" button per column with inline form

**Acceptance Criteria:**
- [ ] Board displays columns with task cards
- [ ] Tasks can be dragged between columns
- [ ] Drag-and-drop state persists via API
- [ ] Failed moves revert with error feedback
- [ ] New tasks can be created inline

---

### Task 6: WebSocket Real-Time Updates
**Status:** Pending
**Estimated Effort:** M (3 hours)
**Dependencies:** Task 3, Task 5
**Priority:** Medium
**Domain:** backend, frontend
**Ship Blocking:** No

**Description:**
Add WebSocket server to the Express app and client-side hook so board changes from other users appear instantly.

**Implementation Steps:**
1. Attach ws WebSocket server to the Express HTTP server
2. On connection, validate JWT from query parameter and join board room
3. When a board mutation occurs (task create/update/move/delete), broadcast event to room
4. Create `useWebSocket` React hook that connects on board view mount, listens for events, and updates local state
5. Handle reconnection on network interruption (exponential backoff)

**Acceptance Criteria:**
- [ ] WebSocket connection established with valid JWT
- [ ] Board mutations broadcast to other connected clients
- [ ] Client UI updates without page refresh
- [ ] Connection reconnects after network interruption

---

### Task 7: Board Sharing (Invite by Email)
**Status:** Pending
**Estimated Effort:** S (2 hours)
**Dependencies:** Task 3
**Priority:** Medium
**Domain:** backend, frontend
**Ship Blocking:** No

**Description:**
Allow board owners to invite other registered users by email. Invited users see the board in their board list.

**Implementation Steps:**
1. Add `POST /api/boards/:id/invite` endpoint that adds a board_members row
2. Validate that the invited email belongs to a registered user
3. Add "Invite" button to board header with email input
4. Show board members list in board settings

**Acceptance Criteria:**
- [ ] Board owner can invite registered users by email
- [ ] Invited user sees the board in their board list
- [ ] Non-owners cannot invite (403)
- [ ] Inviting a non-existent email returns 404 with message

---

### Task 8: Docker Compose Deployment
**Status:** Pending
**Estimated Effort:** M (3 hours)
**Dependencies:** Task 1, Task 5
**Priority:** High
**Domain:** infra
**Ship Blocking:** Yes

**Description:**
Create production Docker Compose configuration with Nginx reverse proxy, Express API, and PostgreSQL. Configure HTTPS with Let's Encrypt.

**Implementation Steps:**
1. Create `Dockerfile` for server (multi-stage: build TypeScript, run with node:20-slim)
2. Create `Dockerfile` for client (multi-stage: build with Vite, serve with Nginx)
3. Create `nginx.conf` for reverse proxy (static files + /api proxy + /ws proxy)
4. Update `docker-compose.yml` with production profile (API, client, db, nginx)
5. Add environment variable configuration (.env.example)
6. Add Let's Encrypt with certbot or Caddy as alternative

**Acceptance Criteria:**
- [ ] `docker compose --profile prod up` starts all services
- [ ] Nginx serves frontend static files and proxies /api and /ws to Express
- [ ] PostgreSQL data persists via Docker volume
- [ ] HTTPS works with valid certificate

---

### Task 9: CI Pipeline (GitHub Actions)
**Status:** Pending
**Estimated Effort:** S (1 hour)
**Dependencies:** Task 2, Task 4
**Priority:** Medium
**Domain:** infra
**Ship Blocking:** No

**Description:**
Set up GitHub Actions workflow that runs lint, type-check, and tests on push to main and on PRs.

**Implementation Steps:**
1. Create `.github/workflows/ci.yml`
2. Steps: checkout, install deps, lint (server + client), type-check, test (server integration tests)
3. Use PostgreSQL service container for integration tests

**Acceptance Criteria:**
- [ ] CI runs on push to main and on PRs
- [ ] Lint, type-check, and test steps all pass
- [ ] PostgreSQL service container used for integration tests

---

## Implementation Order

### Week 1: Backend + Frontend Core
1. Task 1: Project Scaffolding (foundation)
2. Task 2: Auth Module (backend foundation)
3. Task 3: Board + Task CRUD API (core backend)
4. Task 4: React App Shell (frontend foundation)
5. Task 5: Kanban Board with Drag-and-Drop (core frontend)

### Week 2: Integration + Deploy
6. Task 8: Docker Compose Deployment (ship-blocking)
7. Task 6: WebSocket Real-Time (enhancement)
8. Task 7: Board Sharing (enhancement)
9. Task 9: CI Pipeline (quality)

## Progress Tracking

**Total Tasks:** 9
**Ship Blocking:** 6 (Tasks 1-5, 8)
**Non-Ship-Blocking:** 3 (Tasks 6, 7, 9)
**Completed:** 0
**Remaining:** 9
