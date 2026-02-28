# Design: User Authentication System

## Architecture Overview

The authentication system will be built as a modular service with clear separation of concerns:

- **Authentication Service**: Core business logic for auth operations
- **Session Management**: Handles session creation, validation, destruction
- **OAuth Integration**: Manages OAuth provider flows
- **Email Service**: Sends verification and reset emails
- **Middleware**: Request authentication and authorization
- **API Routes**: HTTP endpoints for auth operations

## Technical Decisions

### Decision 1: Session Storage - Redis vs Database
**Context:** Need fast session lookup and automatic expiration

**Options Considered:**
1. **PostgreSQL** - Store sessions in database
   - Pros: Simple, already have DB
   - Cons: Slower, no auto-expiration, more DB load
2. **Redis** - Store sessions in memory cache
   - Pros: Fast, TTL support, scales well
   - Cons: Additional infrastructure, needs replication
3. **JWT only** - Stateless tokens
   - Pros: No server-side storage
   - Cons: Cannot invalidate, larger payload, security concerns

**Decision:** Redis with PostgreSQL backup
**Rationale:**
- Redis provides fast session lookup (<1ms)
- Built-in TTL handles expiration automatically
- Can fall back to DB if Redis unavailable
- Supports session invalidation for security

### Decision 2: Password Hashing - bcrypt vs argon2
**Context:** Need secure, performant password hashing

**Options Considered:**
1. **bcrypt** - Industry standard
   - Pros: Well-tested, widely supported, good security
   - Cons: Limited by single thread performance
2. **argon2** - Modern alternative
   - Pros: Better security, configurable memory cost
   - Cons: Newer, less battle-tested, complex configuration
3. **scrypt** - Memory-hard function
   - Pros: Resistant to ASIC attacks
   - Cons: Complex tuning, performance issues

**Decision:** bcrypt with cost factor 12
**Rationale:**
- Proven security track record
- Well-supported in Node.js ecosystem
- Cost factor 12 balances security and performance (~200ms hash time)
- Easy to upgrade cost factor in future

### Decision 3: OAuth Strategy - Passport vs Manual
**Context:** Need to implement Google and GitHub OAuth

**Options Considered:**
1. **Passport.js** - Authentication middleware
   - Pros: Many strategies, battle-tested, simple integration
   - Cons: Additional dependency, less control
2. **Manual implementation** - Direct OAuth 2.0 flow
   - Pros: Full control, no dependencies
   - Cons: More code, potential security issues, maintenance burden
3. **NextAuth.js** - Full-featured auth library
   - Pros: Complete solution, great DX
   - Cons: Heavy, opinionated, may not fit architecture

**Decision:** Passport.js with custom strategies
**Rationale:**
- Reduces implementation time significantly
- Well-maintained and secure
- Flexible enough for our needs
- Industry standard approach

## Component Design

### Component 1: AuthService
**Responsibility:** Core authentication business logic

**Interface:**
```typescript
class AuthService {
  async register(email: string, password: string): Promise<User>
  async login(email: string, password: string): Promise<Session>
  async logout(sessionId: string): Promise<void>
  async verifyEmail(token: string): Promise<User>
  async requestPasswordReset(email: string): Promise<void>
  async resetPassword(token: string, newPassword: string): Promise<void>
  async validateSession(sessionId: string): Promise<Session | null>
}
```

**Dependencies:**
- UserRepository (database access)
- PasswordHasher (bcrypt wrapper)
- EmailService (sending emails)
- SessionStore (Redis/DB)
- TokenGenerator (secure random tokens)

### Component 2: OAuthService
**Responsibility:** Handle OAuth provider flows

**Interface:**
```typescript
class OAuthService {
  async initiateOAuth(provider: 'google' | 'github', redirectUrl: string): Promise<string>
  async handleOAuthCallback(provider: string, code: string): Promise<Session>
  async linkOAuthAccount(userId: string, provider: string, oauthId: string): Promise<void>
}
```

**Dependencies:**
- Passport strategies
- UserRepository
- SessionStore
- AuthService (for session creation)

### Component 3: SessionStore
**Responsibility:** Manage session storage and retrieval

**Interface:**
```typescript
class SessionStore {
  async create(session: Session, ttl: number): Promise<string>
  async get(sessionId: string): Promise<Session | null>
  async delete(sessionId: string): Promise<void>
  async extend(sessionId: string, ttl: number): Promise<void>
  async deleteAllForUser(userId: string): Promise<void>
}
```

**Dependencies:**
- Redis client
- Database fallback (optional)

### Component 4: AuthMiddleware
**Responsibility:** Validate requests and inject user context

**Interface:**
```typescript
function requireAuth(req: Request, res: Response, next: NextFunction): void
function optionalAuth(req: Request, res: Response, next: NextFunction): void
function requireRole(role: string): Middleware
```

**Dependencies:**
- SessionStore
- AuthService

## Sequence Diagrams

### Flow 1: User Registration
```
User -> Frontend: Submit registration form (email, password)
Frontend -> API: POST /api/auth/register
API -> AuthService: register(email, password)
AuthService -> PasswordHasher: hash(password)
PasswordHasher -> AuthService: hashedPassword
AuthService -> UserRepository: createUser(email, hashedPassword)
UserRepository -> Database: INSERT user
Database -> UserRepository: user
UserRepository -> AuthService: user
AuthService -> TokenGenerator: generateEmailToken()
TokenGenerator -> AuthService: token
AuthService -> EmailService: sendVerificationEmail(email, token)
EmailService -> External: Send email via SendGrid
AuthService -> API: user
API -> Frontend: { success: true, message: "Check email" }
Frontend -> User: Show success message
```

### Flow 2: User Login
```
User -> Frontend: Submit login form (email, password)
Frontend -> API: POST /api/auth/login
API -> RateLimiter: checkLimit(email)
RateLimiter -> API: allowed
API -> AuthService: login(email, password)
AuthService -> UserRepository: findByEmail(email)
UserRepository -> Database: SELECT user
Database -> UserRepository: user
UserRepository -> AuthService: user
AuthService -> PasswordHasher: compare(password, user.hash)
PasswordHasher -> AuthService: isValid
AuthService -> SessionStore: create(session, 24h)
SessionStore -> Redis: SET session:id { userId, ... }
Redis -> SessionStore: OK
SessionStore -> AuthService: sessionId
AuthService -> API: { user, sessionId }
API -> Frontend: Set cookie, return user
Frontend -> User: Redirect to dashboard
```

### Flow 3: OAuth Login (Google)
```
User -> Frontend: Click "Login with Google"
Frontend -> API: GET /api/auth/oauth/google
API -> OAuthService: initiateOAuth('google', callbackUrl)
OAuthService -> API: authorizationUrl
API -> Frontend: Redirect to Google
Frontend -> Google: Authorization request
Google -> User: Login and consent
User -> Google: Approve
Google -> Frontend: Redirect to callback with code
Frontend -> API: GET /api/auth/oauth/google/callback?code=xxx
API -> OAuthService: handleOAuthCallback('google', code)
OAuthService -> Google: Exchange code for token
Google -> OAuthService: { accessToken, profile }
OAuthService -> UserRepository: findByOAuthId('google', profile.id)
UserRepository -> Database: SELECT user
Database -> UserRepository: user or null
Alt: User exists
  OAuthService -> SessionStore: create(session)
  SessionStore -> OAuthService: sessionId
Else: New user
  OAuthService -> UserRepository: createUser(profile)
  UserRepository -> Database: INSERT user
  Database -> UserRepository: user
  OAuthService -> SessionStore: create(session)
  SessionStore -> OAuthService: sessionId
End
OAuthService -> API: { user, sessionId }
API -> Frontend: Set cookie, return user
Frontend -> User: Redirect to dashboard
```

### Flow 4: Password Reset
```
User -> Frontend: Click "Forgot password"
Frontend -> API: POST /api/auth/reset-request { email }
API -> AuthService: requestPasswordReset(email)
AuthService -> UserRepository: findByEmail(email)
UserRepository -> AuthService: user or null
Note: Continue even if user not found (no enumeration)
AuthService -> TokenGenerator: generateResetToken()
TokenGenerator -> AuthService: token
AuthService -> Database: storeResetToken(email, token, 1h expiry)
Database -> AuthService: OK
AuthService -> EmailService: sendResetEmail(email, token)
EmailService -> AuthService: sent
AuthService -> API: success
API -> Frontend: "Check email for reset link"
Frontend -> User: Show message

--- User clicks reset link ---

User -> Frontend: Click reset link with token
Frontend -> ResetPage: Load form
User -> Frontend: Enter new password
Frontend -> API: POST /api/auth/reset-password { token, password }
API -> AuthService: resetPassword(token, password)
AuthService -> Database: validateToken(token)
Database -> AuthService: { valid, email }
AuthService -> PasswordHasher: hash(newPassword)
PasswordHasher -> AuthService: hashedPassword
AuthService -> UserRepository: updatePassword(email, hashedPassword)
UserRepository -> Database: UPDATE user
Database -> UserRepository: OK
UserRepository -> AuthService: success
AuthService -> SessionStore: deleteAllForUser(userId)
SessionStore -> Redis: DEL session:userId:*
Redis -> SessionStore: OK
AuthService -> Database: deleteResetToken(token)
Database -> AuthService: OK
AuthService -> API: success
API -> Frontend: "Password reset successfully"
Frontend -> User: Redirect to login
```

## Data Model Changes

### New Tables

#### users
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255),  -- null for OAuth-only accounts
  email_verified BOOLEAN DEFAULT FALSE,
  email_verified_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_login_at TIMESTAMP,
  failed_login_attempts INT DEFAULT 0,
  locked_until TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_email_verified ON users(email_verified);
```

#### oauth_accounts
```sql
CREATE TABLE oauth_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  provider VARCHAR(50) NOT NULL,  -- 'google', 'github'
  provider_user_id VARCHAR(255) NOT NULL,
  access_token TEXT,
  refresh_token TEXT,
  token_expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(provider, provider_user_id)
);

CREATE INDEX idx_oauth_accounts_user_id ON oauth_accounts(user_id);
CREATE INDEX idx_oauth_accounts_provider ON oauth_accounts(provider, provider_user_id);
```

#### email_verification_tokens
```sql
CREATE TABLE email_verification_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token VARCHAR(255) UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  used_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_email_tokens_token ON email_verification_tokens(token);
CREATE INDEX idx_email_tokens_expires ON email_verification_tokens(expires_at);
```

#### password_reset_tokens
```sql
CREATE TABLE password_reset_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token VARCHAR(255) UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  used_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_reset_tokens_expires ON password_reset_tokens(expires_at);
```

#### login_history
```sql
CREATE TABLE login_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  success BOOLEAN NOT NULL,
  ip_address INET,
  user_agent TEXT,
  location VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_login_history_user_id ON login_history(user_id, created_at DESC);
CREATE INDEX idx_login_history_created ON login_history(created_at);
```

### Redis Data Structures

#### Session
```
Key: session:{sessionId}
Value: {
  userId: string,
  email: string,
  createdAt: number,
  lastAccessedAt: number,
  expiresAt: number,
  ipAddress: string,
  userAgent: string
}
TTL: 24 hours (extended on access)
```

#### Rate Limiting
```
Key: ratelimit:login:{email}
Value: {
  attempts: number,
  resetAt: number
}
TTL: 1 hour
```

## API Changes

### New Endpoints

#### POST /api/auth/register
Register a new user account
```typescript
Request: {
  email: string,
  password: string
}
Response: {
  success: true,
  message: "Verification email sent"
}
Errors: 400 (invalid input), 409 (email exists)
```

#### POST /api/auth/login
Authenticate user and create session
```typescript
Request: {
  email: string,
  password: string,
  rememberMe?: boolean
}
Response: {
  user: { id, email, emailVerified },
  session: { id, expiresAt }
}
Sets cookie: sessionId (httpOnly, secure, sameSite)
Errors: 401 (invalid credentials), 423 (account locked), 429 (rate limit)
```

#### POST /api/auth/logout
End user session
```typescript
Request: {} (uses session cookie)
Response: { success: true }
Errors: 401 (not authenticated)
```

#### GET /api/auth/verify-email
Verify email address with token
```typescript
Query: { token: string }
Response: {
  success: true,
  message: "Email verified"
}
Errors: 400 (invalid token), 410 (expired token)
```

#### POST /api/auth/reset-request
Request password reset
```typescript
Request: { email: string }
Response: {
  success: true,
  message: "Reset email sent if account exists"
}
Errors: 429 (rate limit)
```

#### POST /api/auth/reset-password
Reset password with token
```typescript
Request: {
  token: string,
  password: string
}
Response: {
  success: true,
  message: "Password reset successfully"
}
Errors: 400 (invalid token), 410 (expired token)
```

#### GET /api/auth/oauth/:provider
Initiate OAuth flow
```typescript
Params: { provider: 'google' | 'github' }
Query: { redirect?: string }
Response: Redirect to OAuth provider
Errors: 400 (unsupported provider)
```

#### GET /api/auth/oauth/:provider/callback
Handle OAuth callback
```typescript
Params: { provider: 'google' | 'github' }
Query: { code: string, state: string }
Response: Redirect to app with session cookie
Errors: 400 (invalid code), 500 (OAuth error)
```

#### GET /api/auth/me
Get current user info
```typescript
Request: {} (uses session cookie)
Response: {
  user: { id, email, emailVerified, createdAt, lastLoginAt }
}
Errors: 401 (not authenticated)
```

#### GET /api/auth/sessions
List active sessions
```typescript
Request: {} (uses session cookie)
Response: {
  sessions: [
    { id, createdAt, lastAccessedAt, ipAddress, userAgent, current }
  ]
}
Errors: 401 (not authenticated)
```

#### DELETE /api/auth/sessions/:id
Revoke specific session
```typescript
Params: { id: string }
Request: {} (uses session cookie)
Response: { success: true }
Errors: 401 (not authenticated), 403 (not your session), 404 (session not found)
```

## Security Considerations

### Authentication
- All auth endpoints require HTTPS in production
- Passwords hashed with bcrypt (cost 12)
- Sessions use cryptographically secure random IDs (32 bytes)
- OAuth state parameter prevents CSRF attacks

### Authorization
- Session validation on every protected request
- Session cookies are httpOnly, secure, sameSite=Lax
- CSRF tokens for state-changing operations
- Rate limiting on sensitive endpoints

### Data Protection
- Never log passwords or tokens
- Mask email in error messages (no user enumeration)
- Sanitize user input to prevent injection
- Use parameterized queries for database access
- Encrypt OAuth tokens at rest

### Input Validation
- Validate email format (RFC 5322)
- Enforce password complexity requirements
- Sanitize all user input
- Limit request payload sizes
- Validate token formats

## Performance Considerations

### Caching Strategy
- Session data cached in Redis (O(1) lookup)
- User data cached after authentication (5 min TTL)
- OAuth tokens cached during flow
- Rate limit counters in Redis

### Database Indexes
- Index on users.email for fast lookups
- Index on oauth_accounts(provider, provider_user_id)
- Index on login_history(user_id, created_at)
- Composite index on token tables

### Optimization Approach
- Connection pooling for database and Redis
- Lazy loading of user profile data
- Batch cleanup of expired tokens (cron job)
- Monitor slow queries and add indexes as needed

## Testing Strategy

### Unit Tests
- AuthService: All authentication methods
- PasswordHasher: Hashing and comparison
- TokenGenerator: Token generation and validation
- SessionStore: CRUD operations
- Rate limiting logic

### Integration Tests
- Full authentication flows (register, login, logout)
- OAuth flows with mock providers
- Password reset flow
- Session management
- Rate limiting enforcement
- Database transactions

### E2E Tests
- User registration journey
- Login with email/password
- Login with OAuth (Google, GitHub)
- Password reset flow
- Session expiration
- Concurrent session management

### Security Tests
- Password hashing strength
- Session hijacking prevention
- CSRF protection
- SQL injection prevention
- XSS prevention
- Rate limiting effectiveness
- OAuth token security

## Rollout Plan

### Phase 1: Core Authentication (Week 1)
- Database schema
- User registration and email verification
- Login/logout with password
- Session management
- Basic security measures

### Phase 2: OAuth Integration (Week 1)
- OAuth service implementation
- Google provider integration
- GitHub provider integration
- Account linking

### Phase 3: Password Management (Week 2)
- Password reset flow
- Email integration
- Token management

### Phase 4: Security Enhancements (Week 2)
- Rate limiting
- Account lockout
- Login history
- Security notifications

### Phase 5: Testing & Deployment
- Comprehensive test suite
- Security audit
- Performance testing
- Staged rollout (10% → 50% → 100%)

## Risks & Mitigations

### Risk 1: Redis Failure
**Impact:** Sessions unavailable, users logged out
**Mitigation:**
- Implement database fallback for session storage
- Set up Redis replication
- Monitor Redis health closely
- Graceful degradation (temporary JWT tokens)

### Risk 2: OAuth Provider Downtime
**Impact:** Users cannot log in with OAuth
**Mitigation:**
- Support multiple authentication methods
- Clear error messages for users
- Fallback to email/password if available
- Cache OAuth user data for short period

### Risk 3: Email Delivery Issues
**Impact:** Users cannot verify email or reset password
**Mitigation:**
- Use reliable email service (SendGrid)
- Implement retry logic for failures
- Provide admin interface to manually verify
- Log email failures for monitoring

### Risk 4: Security Vulnerabilities
**Impact:** Account compromise, data breach
**Mitigation:**
- Security code review before launch
- Use established libraries (Passport, bcrypt)
- Regular security audits
- Implement comprehensive logging
- Set up intrusion detection

### Risk 5: Performance Issues at Scale
**Impact:** Slow authentication, poor UX
**Mitigation:**
- Load testing before launch
- Use caching extensively (Redis)
- Optimize database queries with indexes
- Monitor performance metrics
- Plan for horizontal scaling

## Future Enhancements

- Two-factor authentication (TOTP, SMS)
- Biometric authentication (WebAuthn)
- Passwordless login (magic links)
- Additional OAuth providers
- SSO for enterprise (SAML, LDAP)
- Account activity notifications
- Device management
- Session analytics
