# Data Pipeline: User Activity Aggregation Pipeline

## Overview

Build a daily user activity aggregation pipeline that ingests raw user interaction events from Apache Kafka, applies schema validation and deduplication, enriches with user dimension data, computes daily activity aggregates, and loads results into Snowflake for analytics and reporting. The pipeline is orchestrated by Apache Airflow (MWAA) and uses PySpark on AWS EMR for all transformation stages, Delta Lake on S3 for intermediate storage, and Great Expectations for data quality validation.

## Data Requirements

### Requirement 1: Event Ingestion
**As a** data platform
**I need** to consume raw user interaction events from the Kafka `user-events` topic and persist them to the raw data zone
**So that** all downstream transformations operate on a complete, deduplicated event stream

- **Source:** Kafka `user-events` topic (JSON, Avro-encoded via Schema Registry)
- **Destination:** S3 raw zone (`s3://data-lake/raw/user_events/`) in Parquet format, partitioned by `event_date` and `hour`
- **Transformation:** Schema validation against Avro registry, deduplication by `event_id` (exactly-once semantics), timestamp normalization to UTC
- **Frequency:** Micro-batch every 15 minutes via Spark Structured Streaming

**Acceptance Criteria:**
- [ ] Events consumed from Kafka with consumer group `user-activity-pipeline`
- [ ] Each event validated against registered Avro schema; malformed events routed to dead-letter topic
- [ ] Duplicate events (same `event_id`) eliminated within a 24-hour window
- [ ] Output Parquet files partitioned by `event_date=YYYY-MM-DD/hour=HH`
- [ ] Ingestion lag does not exceed 30 minutes under normal load
- [ ] Dead-letter topic receives < 0.1% of total events

### Requirement 2: Activity Aggregation
**As a** data analyst
**I need** daily user activity summaries aggregated by user and date
**So that** I can analyze engagement patterns, session behavior, and feature adoption

- **Source:** S3 raw zone (validated Parquet files)
- **Destination:** Snowflake `analytics.user_activity_daily` table
- **Transformation:** GROUP BY `user_id` + `event_date`; compute `session_count`, `total_duration_seconds`, `page_views`, `unique_pages`, `actions_by_type` (JSON map), `first_event_at`, `last_event_at`
- **Frequency:** Daily batch at 02:00 UTC

**Acceptance Criteria:**
- [ ] One row per `user_id` per `event_date` in the target table
- [ ] Session boundaries determined by 30-minute inactivity gap
- [ ] `actions_by_type` contains counts for each distinct `event_type`
- [ ] Aggregation handles late-arriving events (reprocesses T-1 and T-2)
- [ ] Results available in Snowflake by 04:00 UTC
- [ ] Idempotent: re-running for the same date produces identical results

### Requirement 3: Dimension Enrichment
**As a** data analyst
**I need** user activity records enriched with user profile attributes
**So that** I can segment activity by user tier, region, and cohort

- **Source:** PostgreSQL `users` table (production replica)
- **Destination:** Joined into aggregation output as denormalized columns
- **Transformation:** LEFT JOIN on `user_id`; add `user_tier`, `signup_date`, `region`, `account_status`
- **Frequency:** Daily snapshot of dimension table before aggregation run

**Acceptance Criteria:**
- [ ] User dimension snapshot exported to S3 daily before aggregation starts
- [ ] LEFT JOIN ensures activity records for deleted/unknown users are preserved (with NULLs)
- [ ] Dimension data is point-in-time (snapshot reflects state at start of pipeline run)
- [ ] No direct queries against production PostgreSQL during pipeline execution
- [ ] Dimension snapshot contains all active and recently-deactivated users (last 90 days)

### Requirement 4: Data Quality Checks
**As a** data engineer
**I need** automated data quality validation after each pipeline stage
**So that** data issues are detected before they propagate to downstream consumers

- **Source:** Pipeline stage outputs (raw, staging, aggregated)
- **Destination:** Quality metrics table (`analytics.data_quality_results`) + PagerDuty/Slack alerts
- **Transformation:** Null checks, range validation, row count thresholds, cross-stage reconciliation, uniqueness checks
- **Frequency:** After each pipeline stage completes

**Acceptance Criteria:**
- [ ] Great Expectations suite runs after ingestion, staging, and aggregation stages
- [ ] Critical failures (completeness < 95%) halt the pipeline and trigger PagerDuty alert
- [ ] Warning-level issues (completeness 95-99.5%) log to Slack and continue
- [ ] Quality results persisted to `analytics.data_quality_results` with run_id and timestamp
- [ ] Reconciliation check compares raw event count vs. aggregated record count (variance < 0.5%)
- [ ] Quality dashboard available in Snowflake for historical trend analysis

### Requirement 5: Reporting Materialization
**As a** business stakeholder
**I need** pre-computed engagement metrics and retention cohorts
**So that** dashboards load quickly and show consistent numbers

- **Source:** `analytics.user_activity_daily` (aggregated table)
- **Destination:** Snowflake materialized views (`analytics.mv_daily_active_users`, `analytics.mv_weekly_active_users`, `analytics.mv_monthly_active_users`, `analytics.mv_retention_cohorts`)
- **Transformation:** DAU/WAU/MAU calculations, retention cohort analysis (Week 1, Week 2, Week 4, Week 8, Week 12)
- **Frequency:** Daily refresh after aggregation completes

**Acceptance Criteria:**
- [ ] DAU = distinct `user_id` count per `event_date`
- [ ] WAU = distinct `user_id` count in trailing 7-day window
- [ ] MAU = distinct `user_id` count in trailing 30-day window
- [ ] Retention cohorts grouped by `signup_week` with activity flags per retention period
- [ ] Materialized views refresh completes within 15 minutes
- [ ] Views are query-optimized with clustering on `event_date`

## Data Quality Requirements

| Dimension | Target | Measurement Method |
|-----------|--------|-------------------|
| **Completeness** | >= 99.5% of Kafka events land in Snowflake | Compare Kafka topic offset range vs. raw zone record count |
| **Freshness** | Data available by 04:00 UTC for previous day | Monitor `last_loaded_at` timestamp in Snowflake metadata |
| **Accuracy** | Within 0.1% of source reconciliation | Cross-check aggregated totals against raw event counts |
| **Consistency** | Zero duplicate rows in target table | Uniqueness constraint on (`user_id`, `event_date`) |
| **Validity** | All `event_type` values in allowed set | Great Expectations allowlist check |
| **Timeliness** | Late events within 48h reprocessed automatically | T-1 and T-2 reprocessing in daily DAG |

## Volume & Velocity

| Metric | Current | Projected (12 months) |
|--------|---------|----------------------|
| Daily event volume | 50M events (~20 GB raw) | 100M events (~40 GB raw) |
| Peak throughput | 5,000 events/second | 10,000 events/second |
| Unique users/day | ~2M | ~4M |
| Aggregated rows/day | ~2M | ~4M |
| Raw storage growth | ~600 GB/month | ~1.2 TB/month |
| End-to-end latency | < 4 hours (T+4h) | < 4 hours (T+4h) |

## Pipeline SLAs

### Availability
- Pipeline execution success rate >= 99.5% (measured monthly)
- Automated retry on transient failures (max 3 retries per task)
- Manual intervention required only for schema-breaking changes

### Processing Time
- Ingestion micro-batch: < 5 minutes per batch
- Daily aggregation job: < 2 hours end-to-end
- Snowflake loading: < 30 minutes
- Materialized view refresh: < 15 minutes

### Data Freshness
- Previous day's data available in Snowflake by 04:00 UTC (T+4h)
- Late-arriving events reprocessed within 24 hours
- Quality check results available within 30 minutes of pipeline completion

### Error Budget
- < 0.5% event loss rate (Kafka to Snowflake)
- < 0.01% data accuracy variance vs. source
- Max 2 unplanned pipeline failures per month

## Constraints & Assumptions

### Constraints
- Shared Kafka cluster managed by platform team (no admin access; consumer group quotas apply)
- Snowflake Medium warehouse (`COMPUTE_WH`) — limited to 4 concurrent queries during pipeline window
- EMR clusters use spot instances (r5.2xlarge) for cost efficiency — must handle interruptions
- Airflow 2.x on AWS MWAA — DAG file size limit 1 MB, max 25 concurrent tasks
- S3 bucket `data-lake` already exists with lifecycle policies (raw: 90-day retention, staging: 30-day retention)

### Assumptions
- Kafka `user-events` topic exists with 12 partitions and 7-day retention
- Avro Schema Registry is operational and schema v1 is registered
- PostgreSQL production replica is available for read-only access during off-peak hours
- Snowflake `analytics` database and schema exist; service account has WRITE privileges
- AWS IAM roles for EMR and MWAA are pre-configured by infrastructure team
- PagerDuty and Slack webhook integrations are available for alerting

## Team Conventions

- Use PySpark for all transformation logic (no pandas in production pipelines)
- Write idempotent jobs — every stage must produce identical output on re-run
- Store all SQL as version-controlled `.sql` files (no inline SQL in DAG definitions)
- Use Delta Lake for all intermediate storage (ACID guarantees, schema enforcement)
- Tag all AWS resources with `project:user-activity-pipeline` and `env:{environment}`
- Configuration via environment variables and Airflow Variables (no hardcoded values)
- Follow team naming convention: `dag_<domain>_<pipeline>_<version>` for Airflow DAGs
- Log structured JSON to CloudWatch for observability

## Success Metrics

- Pipeline runs within SLA (< 2h processing, data available by 04:00 UTC) on 99%+ of days
- Data completeness >= 99.5% measured over rolling 30-day window
- Zero duplicate rows in `user_activity_daily` table
- Quality check pass rate > 99% (no critical failures)
- Snowflake query performance on materialized views < 5 seconds (p95)
- Cost per run < $25 (EMR spot + Snowflake credits)

## Out of Scope (Future Considerations)

- Real-time streaming aggregations (sub-minute latency)
- ML feature store integration (feature engineering pipelines)
- Cross-service event correlation (joining with payment or notification events)
- Backfill beyond 90 days of historical data
- Self-serve schema evolution (producer-driven schema changes)
- Multi-region data replication
- PII tokenization or anonymization (handled by upstream service)
