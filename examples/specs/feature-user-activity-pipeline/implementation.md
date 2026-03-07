# Implementation Journal: User Activity Aggregation Pipeline

## Summary
All 14 tasks completed. 3 key decisions (Delta Lake MERGE for idempotency, Great Expectations for validation, broadcast join for user dimension). 3 deviations from design (S3 snapshot over JDBC, scheduled COPY INTO over Snowpipe, shared EMR cluster). 3 blockers resolved (Delta Lake S3 upload, Kafka quota, GE Spark engine). Pipeline runs within SLA on 100% of test days. Average daily cost: $18 (under $25 budget).

## Decision Log
| # | Decision | Rationale | Task | Timestamp |
|---|----------|-----------|------|-----------|
| 1 | Used Delta Lake `MERGE` for idempotent upserts at every stage | Guarantees identical output on re-run without manual dedup logic; simplifies backfill and late-event reprocessing | Tasks 3, 4, 5 | 2025-02-12 |
| 2 | Chose Great Expectations over custom validation framework | Declarative expectation suites are easier to maintain and audit than ad-hoc Python checks; built-in HTML reports for stakeholder visibility | Task 8 | 2025-02-20 |
| 3 | Broadcast join for user dimension enrichment | User dimension table (~500 MB) fits in executor memory; eliminates shuffle join and reduces enrichment stage from 25 min to 8 min | Task 4 | 2025-02-14 |

## Deviations from Design
| Planned | Actual | Reason | Task |
|---------|--------|--------|------|
| JDBC connection to PostgreSQL replica for dimension export | Daily S3 snapshot of `users` table exported by a separate Airflow task | Avoids adding load to production replica during pipeline window; snapshot is reusable by other pipelines | Task 4 |
| Snowpipe for continuous Snowflake loading | Scheduled `COPY INTO` via Airflow SnowflakeOperator | Snowpipe auto-ingest added operational complexity (SQS queue, troubleshooting lag); scheduled COPY INTO is simpler to monitor and debug | Task 6 |
| Separate EMR cluster per pipeline run | Shared long-running EMR cluster with auto-scaling | Cost savings of ~40%; spot instance interruptions handled by EMR managed scaling with instance fleet fallback | Task 1 |

## Blockers Encountered
| Blocker | Resolution | Impact | Task |
|---------|------------|--------|------|
| EMR 6.10 (Spark 3.3) had Delta Lake S3 multi-part upload compatibility issue causing intermittent write failures | Upgraded to EMR 6.12 (Spark 3.4) which includes the fix; verified with 50M event load test | Task 5 delayed by 1 day | Task 5 |
| Kafka consumer group quota on shared cluster too low (10 MB/s) causing ingestion lag during peak hours | Platform team increased quota to 50 MB/s for `user-activity-pipeline` consumer group | Task 2 delayed by 1 day (waiting on platform team) | Task 2 |
| Great Expectations Spark engine incompatible with Delta Lake table format for certain expectations | Used `RuntimeDataConnector` with explicit DataFrame pass-through instead of `InferredAssetFilesystemDataConnector` | Task 8 required 3 hours of additional debugging | Task 8 |

## Session Log
- **2025-02-10**: Started implementation. Completed Tasks 1-2. Blocker hit on Task 2 (Kafka quota).
- **2025-02-12**: Resumed at Task 3. Completed Tasks 3-5. Blocker hit on Task 5 (Delta Lake S3).
- **2025-02-14**: Resumed at Task 4 enrichment. Completed Tasks 4-7.
- **2025-02-20**: Resumed at Task 8. Completed Tasks 8-14. Blocker hit on Task 8 (GE Spark). All tasks done.
