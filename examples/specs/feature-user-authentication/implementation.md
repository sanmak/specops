# Implementation Notes: User Authentication System

## Decisions Made During Implementation
| Decision | Rationale | Task |
|----------|-----------|------|
| Used `express-rate-limit` instead of custom rate limiter | Well-maintained, configurable, and handles edge cases (distributed setups) out of the box | Task 7 |
| Added `connect-redis` for session store | Provides Express-compatible session middleware with Redis backend, reducing custom code | Task 2 |
| Chose `zod` for input validation over `express-validator` | Already used elsewhere in the project; keeps validation approach consistent | Task 12 |

## Deviations from Design
| Planned | Actual | Reason |
|---------|--------|--------|
| Database fallback for Redis sessions | Skipped — Redis Sentinel configured for HA | Ops team confirmed Redis Sentinel is available; DB fallback adds complexity with no benefit |
| Separate `TokenGenerator` class | Combined into `AuthService` as private methods | Only two token types needed; separate class was over-abstraction |

## Blockers Encountered
| Blocker | Resolution | Impact |
|---------|------------|--------|
| SendGrid sandbox mode rejecting verification emails in dev | Used `nodemailer` with Ethereal for local dev, SendGrid for staging/prod | Task 6 delayed by 2 hours |
| GitHub OAuth callback URL mismatch in dev | Added `localhost:3000` to GitHub OAuth app's allowed redirect URIs | Task 9 delayed by 30 min |

## Notes
- Password hashing with bcrypt cost 12 takes ~250ms on the dev machine — acceptable for auth endpoints but monitor in production
- OAuth token encryption at rest deferred to a follow-up task (tracked as future enhancement in design.md)
- All 16 tasks completed; test coverage at 84%
