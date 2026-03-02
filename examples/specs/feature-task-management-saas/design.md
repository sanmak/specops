# Design: Task Management SaaS MVP

## Architecture Overview

Monolithic architecture with clear module boundaries, deployed as a Docker Compose stack. The system consists of a React SPA served by Nginx, a Node.js/Express REST API with WebSocket support, and a PostgreSQL database. All three run as containers on a single VPS.

```
Browser → Nginx (static + reverse proxy) → Express API → PostgreSQL
                                         → WebSocket (ws)
```

No microservices, no message queues, no caching layer. The MVP targets < 100 concurrent users on a single server. Complexity is added only when traffic demands it.

## Technical Decisions

### Decision 1: Monolith vs Microservices
**Context:** Need to ship a working product fast as a solo builder.

**Options Considered:**
1. **Monolith (Express API)** — Single server handles REST, WebSocket, and auth
   - Pros: Simple deployment, single codebase, fast iteration, easy debugging
   - Cons: Scales vertically only, harder to isolate failures
2. **Microservices** — Separate services for auth, boards, real-time
   - Pros: Independent scaling, technology diversity
   - Cons: Deployment complexity, service discovery, network overhead, overkill for MVP

**Decision:** Monolith
**Rationale:** A solo builder shipping an MVP does not need service boundaries. One Express server handles everything. If the product gains traction, extract services later when there is a concrete reason.

### Decision 2: Real-Time Approach
**Context:** Board updates need to appear instantly for all connected users.

**Options Considered:**
1. **WebSocket (ws library)** — Full-duplex connection
   - Pros: Low latency, bidirectional, well-supported
   - Cons: Connection management, requires sticky sessions at scale
2. **Server-Sent Events** — Server push over HTTP
   - Pros: Simple, built on HTTP, auto-reconnect
   - Cons: Unidirectional, limited browser connections per domain
3. **Polling** — Client fetches updates every N seconds
   - Pros: Simplest implementation
   - Cons: Latency, wasted requests, not truly real-time

**Decision:** WebSocket (ws library)
**Rationale:** Real-time drag-and-drop requires low-latency bidirectional communication. The `ws` library is lightweight, has zero dependencies, and works with the Express server directly. At MVP scale (single server), sticky sessions are not a concern.

### Decision 3: Drag-and-Drop Library
**Context:** Need Kanban-style column drag-and-drop for tasks.

**Options Considered:**
1. **@hello-pangea/dnd (fork of react-beautiful-dnd)** — Maintained fork with accessible drag-and-drop
   - Pros: Battle-tested, keyboard accessible, smooth animations, Kanban-optimized
   - Cons: Heavier than alternatives, opinionated API
2. **dnd-kit** — Modern, modular drag-and-drop toolkit
   - Pros: Smaller bundle, composable, framework-agnostic sensors
   - Cons: More setup for Kanban pattern, less opinionated

**Decision:** @hello-pangea/dnd
**Rationale:** Purpose-built for the Kanban use case with accessibility out of the box. The slightly larger bundle is acceptable for an MVP.

## Product Module Design

### Module 1: Auth
**Responsibility:** User registration, login, JWT token issuance and verification.
**Interface:**
- `POST /api/auth/register` — Create account
- `POST /api/auth/login` — Authenticate, return JWT
- `GET /api/auth/me` — Return current user from token
**Dependencies:** PostgreSQL (users table), bcrypt, jsonwebtoken

### Module 2: Boards
**Responsibility:** Board CRUD and membership management.
**Interface:**
- `POST /api/boards` — Create board
- `GET /api/boards` — List user's boards
- `GET /api/boards/:id` — Get board with columns and tasks
- `PATCH /api/boards/:id` — Update board name/description
- `DELETE /api/boards/:id` — Delete board
- `POST /api/boards/:id/invite` — Invite user by email
**Dependencies:** PostgreSQL (boards, board_members tables), Auth module (JWT middleware)

### Module 3: Tasks
**Responsibility:** Task CRUD and column position management.
**Interface:**
- `POST /api/boards/:boardId/tasks` — Create task
- `PATCH /api/tasks/:id` — Update task fields
- `PATCH /api/tasks/:id/move` — Move task to column + position (drag-and-drop)
- `DELETE /api/tasks/:id` — Delete task
**Dependencies:** PostgreSQL (tasks, columns tables), Boards module (authorization)

### Module 4: Real-Time
**Responsibility:** Broadcast board changes to connected clients via WebSocket.
**Interface:** WebSocket endpoint at `/ws?boardId=<id>&token=<jwt>`
**Events emitted:** `task:created`, `task:updated`, `task:moved`, `task:deleted`
**Dependencies:** ws library, Auth module (token validation), Boards/Tasks modules (event source)

## System Flow

### Flow: User Drags Task to New Column
```
User drags task card → React DnD fires onDragEnd
→ Frontend optimistically reorders local state
→ Frontend sends PATCH /api/tasks/:id/move { columnId, position }
→ API validates ownership, updates tasks.column_id and tasks.position in DB
→ API publishes { event: "task:moved", taskId, columnId, position } to WebSocket room
→ Other connected clients receive event, update their local board state
→ If API call fails, frontend reverts optimistic update and shows error toast
```

## Integration Points
- **bcrypt** — Password hashing (registration, login)
- **jsonwebtoken** — JWT signing and verification
- **ws** — WebSocket server, attached to the Express HTTP server
- **@hello-pangea/dnd** — React drag-and-drop for Kanban boards
- **pg (node-postgres)** — PostgreSQL client for all database operations
- **Docker Compose** — Container orchestration for API, PostgreSQL, Nginx

## Data Architecture

### Tables
```sql
users:
  - id: uuid (PK)
  - email: varchar(255) UNIQUE
  - password_hash: varchar(255)
  - name: varchar(100)
  - created_at: timestamptz

boards:
  - id: uuid (PK)
  - name: varchar(200)
  - description: text (nullable)
  - owner_id: uuid (FK → users)
  - created_at: timestamptz

board_members:
  - board_id: uuid (FK → boards)
  - user_id: uuid (FK → users)
  - role: varchar(20) DEFAULT 'member'
  - PK: (board_id, user_id)

columns:
  - id: uuid (PK)
  - board_id: uuid (FK → boards)
  - name: varchar(100)
  - position: integer

tasks:
  - id: uuid (PK)
  - board_id: uuid (FK → boards)
  - column_id: uuid (FK → columns)
  - title: varchar(300)
  - description: text (nullable)
  - assignee_id: uuid (FK → users, nullable)
  - due_date: date (nullable)
  - position: integer
  - created_at: timestamptz
  - updated_at: timestamptz
```

## Ship Plan

**Phase 1: Core Backend (Days 1-3)**
Deploy API with auth, board CRUD, and task CRUD. Verify with Postman/curl. No frontend yet.

**Phase 2: Frontend Shell (Days 4-7)**
React app with routing, auth pages, board list, and Kanban board view with drag-and-drop. Connect to API.

**Phase 3: Real-Time + Polish (Days 8-10)**
Add WebSocket layer for live updates. Add board sharing (invite by email). Fix rough edges.

**Phase 4: Deploy (Days 11-12)**
Docker Compose on VPS. Nginx config. Domain + HTTPS via Let's Encrypt. Basic CI (GitHub Actions: lint + test + build).

**Rollback:** Each phase is independently deployable. If Phase 3 blocks, ship without real-time and add it post-launch.

## Testing Strategy
- **Unit tests:** Auth logic (token generation, password hashing), task position reordering
- **Integration tests:** API endpoint tests with test database (board CRUD, task move, auth flow)
- **No E2E tests in v1** — manual testing of drag-and-drop; E2E is a post-MVP investment
