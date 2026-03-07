# Implementation Journal: User Authentication System

## Summary
All 16 tasks completed. 3 key decisions diverged from the original design: used express-rate-limit instead of custom rate limiting, combined TokenGenerator into AuthService, and chose zod over express-validator. 2 blockers were encountered and resolved (SendGrid sandbox mode, GitHub OAuth callback URL). Test coverage at 84%.

## Decision Log
| # | Decision | Rationale | Task | Timestamp |
|---|----------|-----------|------|-----------|
| 1 | Used `express-rate-limit` instead of custom rate limiter | Well-maintained, configurable, and handles edge cases (distributed setups) out of the box | Task 7 | 2025-02-18 |
| 2 | Added `connect-redis` for session store | Provides Express-compatible session middleware with Redis backend, reducing custom code | Task 2 | 2025-02-15 |
| 3 | Chose `zod` for input validation over `express-validator` | Already used elsewhere in the project; keeps validation approach consistent | Task 12 | 2025-02-22 |

## Deviations from Design
| Planned | Actual | Reason | Task |
|---------|--------|--------|------|
| Database fallback for Redis sessions | Skipped — Redis Sentinel configured for HA | Ops team confirmed Redis Sentinel is available; DB fallback adds complexity with no benefit | Task 2 |
| Separate `TokenGenerator` class | Combined into `AuthService` as private methods | Only two token types needed; separate class was over-abstraction | Task 5 |

## Blockers Encountered
| Blocker | Resolution | Impact | Task |
|---------|------------|--------|------|
| SendGrid sandbox mode rejecting verification emails in dev | Used `nodemailer` with Ethereal for local dev, SendGrid for staging/prod | Task 6 delayed by 2 hours | Task 6 |
| GitHub OAuth callback URL mismatch in dev | Added `localhost:3000` to GitHub OAuth app's allowed redirect URIs | Task 9 delayed by 30 min | Task 9 |

## Session Log
- **2025-02-15**: Started implementation. Completed Tasks 1-3.
- **2025-02-16**: Resumed at Task 4. Completed Tasks 4-6. Blocker hit on Task 6 (SendGrid).
- **2025-02-18**: Resumed at Task 7. Completed Tasks 7-10. Blocker hit on Task 9 (OAuth callback).
- **2025-02-22**: Resumed at Task 11. Completed Tasks 11-16. All tasks done.
