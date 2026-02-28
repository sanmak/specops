# Implementation Notes: User Activity Aggregation Pipeline

## Decisions Made During Implementation
| Decision | Rationale | Task |
|----------|-----------|------|
| Used Delta Lake `MERGE` for idempotent upserts at every stage | Guarantees identical output on re-run without manual dedup logic; simplifies backfill and late-event reprocessing | Tasks 3, 4, 5 |
| Chose Great Expectations over custom validation framework | Declarative expectation suites are easier to maintain and audit than ad-hoc Python checks; built-in HTML reports for stakeholder visibility | Task 8 |
| Broadcast join for user dimension enrichment | User dimension table (~500 MB) fits in executor memory; eliminates shuffle join and reduces enrichment stage from 25 min to 8 min | Task 4 |

## Deviations from Design
| Planned | Actual | Reason |
|---------|--------|--------|
| JDBC connection to PostgreSQL replica for dimension export | Daily S3 snapshot of `users` table exported by a separate Airflow task | Avoids adding load to production replica during pipeline window; snapshot is reusable by other pipelines |
| Snowpipe for continuous Snowflake loading | Scheduled `COPY INTO` via Airflow SnowflakeOperator | Snowpipe auto-ingest added operational complexity (SQS queue, troubleshooting lag); scheduled COPY INTO is simpler to monitor and debug |
| Separate EMR cluster per pipeline run | Shared long-running EMR cluster with auto-scaling | Cost savings of ~40%; spot instance interruptions handled by EMR managed scaling with instance fleet fallback |

## Blockers Encountered
| Blocker | Resolution | Impact |
|---------|------------|--------|
| EMR 6.10 (Spark 3.3) had Delta Lake S3 multi-part upload compatibility issue causing intermittent write failures | Upgraded to EMR 6.12 (Spark 3.4) which includes the fix; verified with 50M event load test | Task 5 delayed by 1 day |
| Kafka consumer group quota on shared cluster too low (10 MB/s) causing ingestion lag during peak hours | Platform team increased quota to 50 MB/s for `user-activity-pipeline` consumer group | Task 2 delayed by 1 day (waiting on platform team) |
| Great Expectations Spark engine incompatible with Delta Lake table format for certain expectations | Used `RuntimeDataConnector` with explicit DataFrame pass-through instead of `InferredAssetFilesystemDataConnector` | Task 8 required 3 hours of additional debugging |

## Notes
- All 14 tasks completed; pipeline runs within SLA on 100% of test days (7-day burn-in period)
- Data quality checks pass consistently; cross-stage reconciliation variance < 0.05% (well within 0.5% tolerance)
- Average daily pipeline cost: $18 (EMR spot: $12, Snowflake: $6) — under $25 budget
- Backfill DAG validated with 30-day reprocessing; completed in 5.5 hours on dedicated cluster
