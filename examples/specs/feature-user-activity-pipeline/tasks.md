# Implementation Tasks: User Activity Aggregation Pipeline

## Task Breakdown

### Task 1: Set Up S3 Bucket Structure and Delta Lake
**Status:** Pending
**Estimated Effort:** S (1-2 hours)
**Dependencies:** None
**Priority:** High

**Description:**
Create the S3 directory structure for all pipeline zones (raw, staging, enriched, aggregated, checkpoints, snowflake-staging) and initialize Delta Lake tables with correct schemas and partition strategies.

**Implementation Steps:**
1. Create S3 prefix structure under `s3://data-lake/`:
   - `raw/user_events/`
   - `staging/user_events_cleaned/`
   - `enriched/user_events_enriched/`
   - `aggregated/user_activity_daily/`
   - `checkpoints/ingestion/`
   - `snowflake-staging/user_activity_daily/`
   - `dimensions/users/`
2. Initialize Delta Lake tables with schema definitions for staging, enriched, and aggregated zones
3. Configure Delta Lake table properties (auto-optimize, retention, Z-ORDER)
4. Set up S3 lifecycle policies (raw: 90 days, staging: 30 days, checkpoints: 7 days)
5. Verify IAM role `data-pipeline-role` has read/write access to all prefixes
6. Tag all resources with `project:user-activity-pipeline`

**Acceptance Criteria:**
- [ ] All S3 prefixes created and accessible by EMR and MWAA roles
- [ ] Delta Lake tables initialized with correct schemas (verified via `DESCRIBE TABLE`)
- [ ] Lifecycle policies applied (raw 90-day, staging 30-day retention)
- [ ] IAM permissions validated (write test file, read back, delete)
- [ ] **Data Validation:** Write a small test Parquet file to each zone and read it back to verify schema compatibility

**Files to Modify:**
- `infrastructure/s3_setup.py`
- `infrastructure/delta_lake_init.py`
- `infrastructure/iam_policy.json`
- `config/delta_table_properties.json`

**Validation Required:**
- [ ] Delta Lake table schemas match design spec
- [ ] Write + read round-trip succeeds for each zone
- [ ] Lifecycle rules verified via `aws s3api get-bucket-lifecycle-configuration`

---

### Task 2: Create Kafka Consumer with Spark Structured Streaming
**Status:** Pending
**Estimated Effort:** M (3 hours)
**Dependencies:** Task 1
**Priority:** High

**Description:**
Implement Spark Structured Streaming job that consumes events from the Kafka `user-events` topic, validates against Avro schema, deduplicates by `event_id`, and writes Parquet files to the S3 raw zone partitioned by `event_date` and `hour`.

**Implementation Steps:**
1. Create PySpark application `ingestion/kafka_consumer.py`
2. Configure Kafka source with `subscribe`, `startingOffsets`, `maxOffsetsPerTrigger`
3. Implement Avro deserialization using Schema Registry client (`confluent_kafka.avroserializer`)
4. Add schema validation: check required fields (`event_id`, `user_id`, `event_type`, `timestamp`)
5. Route invalid events to dead-letter topic `user-events-dlq` with error reason
6. Implement deduplication using `dropDuplicates("event_id")` with 24-hour watermark on `timestamp`
7. Normalize timestamps to UTC
8. Add processing metadata columns: `_ingested_at`, `_batch_id`, `_source_partition`
9. Write to S3 raw zone as Parquet, partitioned by `event_date=YYYY-MM-DD/hour=HH`
10. Configure checkpointing to `s3://data-lake/checkpoints/ingestion/`
11. Set trigger interval to 15 minutes

**Acceptance Criteria:**
- [ ] Structured Streaming job starts and consumes from Kafka topic
- [ ] Avro deserialization works with Schema Registry
- [ ] Invalid events routed to DLQ with error reason in message headers
- [ ] Duplicate `event_id` values within 24-hour window are eliminated
- [ ] Output Parquet files partitioned correctly by `event_date` and `hour`
- [ ] Checkpointing enables exactly-once processing across restarts
- [ ] Job processes 5,000 events/sec without lag accumulation
- [ ] **Data Validation:** Ingested record count matches Kafka offset range (within 0.1% tolerance after dedup)

**Files to Modify:**
- `ingestion/kafka_consumer.py`
- `ingestion/schema_validator.py`
- `ingestion/dlq_handler.py`
- `config/ingestion_config.py`

**Validation Required:**
- [ ] Publish 10,000 test events to Kafka; verify 10,000 appear in raw zone (minus known duplicates)
- [ ] Publish 100 malformed events; verify all appear in DLQ
- [ ] Publish 500 duplicate `event_id` values; verify dedup produces unique records
- [ ] Restart consumer; verify no duplicates or gaps from checkpoint recovery

---

### Task 3: Build Staging Transformation
**Status:** Pending
**Estimated Effort:** M (2-3 hours)
**Dependencies:** Task 2
**Priority:** High

**Description:**
Create PySpark batch job that reads raw Parquet files, applies type coercion and normalization, filters internal/test events, and writes cleaned data to Delta Lake staging table using MERGE for idempotent upserts.

**Implementation Steps:**
1. Create PySpark application `transformations/staging.py`
2. Read raw Parquet files for target date range (T-2 to T for late arrivals)
3. Apply strict type coercion:
   - `event_id`: STRING, UUID format regex validation
   - `event_type`: STRING, lowercase + trim, validate against allowlist
   - `timestamp`: TIMESTAMP, UTC normalization
   - `duration_seconds`: INT, range check (>= 0)
   - `metadata`: parse JSON string to MAP<STRING, STRING>
4. Flag rows with type coercion issues: `_has_quality_issue = true`
5. Filter out test/internal events (configurable user_id exclusion list)
6. Write to Delta Lake staging table using `MERGE` on `event_id`
7. Run Delta Lake `OPTIMIZE` with file compaction (target 128 MB per file)
8. Parameterize date range for backfill support

**Acceptance Criteria:**
- [ ] All columns correctly typed per staging schema specification
- [ ] Invalid `event_type` values flagged (not dropped) with `_has_quality_issue = true`
- [ ] Internal/test events filtered out based on configurable exclusion list
- [ ] Delta Lake MERGE produces identical output on re-run (idempotent)
- [ ] File compaction reduces small file count (no files < 64 MB after OPTIMIZE)
- [ ] Handles empty date partitions gracefully (no failures)
- [ ] **Data Validation:** Staged record count within 1% of raw record count (after filtering)

**Files to Modify:**
- `transformations/staging.py`
- `transformations/type_coercion.py`
- `config/staging_config.py`
- `config/event_type_allowlist.json`

**Validation Required:**
- [ ] Run with 1M synthetic events; verify all valid events present in staging
- [ ] Run twice for same date; verify Delta Lake table has no duplicates
- [ ] Inject 1,000 events with invalid types; verify `_has_quality_issue` flag set
- [ ] Verify OPTIMIZE produces files between 64 MB and 256 MB

---

### Task 4: Implement Dimension Enrichment
**Status:** Pending
**Estimated Effort:** M (2-3 hours)
**Dependencies:** Task 3
**Priority:** High

**Description:**
Build the user dimension export from PostgreSQL replica to S3 and the PySpark enrichment job that LEFT JOINs staged events with user dimension data to add user profile attributes.

**Implementation Steps:**
1. Create dimension export script `dimensions/export_users.py`:
   - Connect to PostgreSQL read replica
   - Execute dimension query (active users + deactivated within 90 days)
   - Write to `s3://data-lake/dimensions/users/snapshot_date={date}/` as Parquet
2. Create PySpark enrichment job `transformations/enrichment.py`:
   - Read staged events from Delta Lake
   - Read user dimension snapshot from S3
   - LEFT JOIN on `user_id` (broadcast join — dimension table ~500 MB)
   - Add enrichment columns: `user_tier`, `signup_date`, `region`, `account_status`, `company_size`
   - Compute derived columns: `days_since_signup`, `user_cohort_week`, `is_new_user`
   - Set `_enrichment_status` = 'matched' or 'unmatched'
   - Write to Delta Lake enriched table using MERGE on `event_id`
3. Parameterize for backfill (use snapshot closest to target date)

**Acceptance Criteria:**
- [ ] Dimension export completes in < 10 minutes
- [ ] No direct PostgreSQL queries during enrichment job (uses S3 snapshot only)
- [ ] LEFT JOIN preserves all events (unmatched users get NULL enrichment columns)
- [ ] `days_since_signup` and `user_cohort_week` correctly computed
- [ ] `is_new_user` = true when `days_since_signup` < 7
- [ ] Enrichment is idempotent (re-run produces identical results)
- [ ] **Data Validation:** Enriched record count equals staged record count (zero records lost in join)

**Files to Modify:**
- `dimensions/export_users.py`
- `transformations/enrichment.py`
- `sql/extract_user_dimension.sql`
- `config/enrichment_config.py`

**Validation Required:**
- [ ] Export 100K user dimension rows; verify Parquet schema matches expectation
- [ ] Enrich 1M events with 100K users; verify matched count > 95%
- [ ] Inject 1,000 events with unknown `user_id`; verify preserved with NULL enrichment
- [ ] Run enrichment twice; verify no duplicate rows in enriched table

---

### Task 5: Build Aggregation Logic
**Status:** Pending
**Estimated Effort:** L (4-5 hours)
**Dependencies:** Task 4
**Priority:** High

**Description:**
Implement the core aggregation PySpark job that computes daily user activity metrics including session computation (30-minute inactivity gap), event counts by type, and duration aggregates, and writes results to the aggregated Delta Lake table using MERGE.

**Implementation Steps:**
1. Create PySpark application `transformations/aggregation.py`
2. Read enriched events from Delta Lake for target date range (T-2 to T)
3. Implement session computation:
   - Window function: partition by `user_id`, order by `timestamp`
   - Compute time gap between consecutive events using `LAG`
   - Assign new `session_id` when gap > 30 minutes
   - Calculate per-session duration (last event timestamp - first event timestamp)
4. Aggregate by (`user_id`, `event_date`):
   - `session_count`: COUNT DISTINCT computed session IDs
   - `total_duration_seconds`: SUM of session durations
   - `page_views`: COUNT where event_type = 'page_view'
   - `unique_pages`: COUNT DISTINCT page_url
   - `total_events`: COUNT all events
   - `actions_by_type`: MAP from event_type to count (JSON-serializable)
   - `first_event_at`, `last_event_at`: MIN/MAX timestamp
   - `avg_session_duration_seconds`: AVG of session durations
5. Carry forward enrichment columns (FIRST non-null)
6. Write to Delta Lake aggregated table using MERGE on (`user_id`, `event_date`)
7. Run OPTIMIZE with Z-ORDER on `user_id`
8. Parameterize date range for backfill support

**Acceptance Criteria:**
- [ ] One row per (`user_id`, `event_date`) in output
- [ ] Session boundaries correct: new session after 30-minute gap
- [ ] `actions_by_type` is a valid JSON map with correct counts per event type
- [ ] Late-arriving events (T-1, T-2) re-aggregated correctly via MERGE upsert
- [ ] MERGE is idempotent: re-running for same date produces identical results
- [ ] Z-ORDER optimization applied after each run
- [ ] Handles edge cases: single-event sessions, users with 1,000+ events/day
- [ ] **Data Validation:** SUM of `total_events` across all users for a date matches enriched event count (within 0.5%)

**Files to Modify:**
- `transformations/aggregation.py`
- `transformations/session_computation.py`
- `config/aggregation_config.py`

**Validation Required:**
- [ ] Process 1M events for 10K users; verify row count = unique (user_id, event_date) combinations
- [ ] Create events with known session gaps; verify `session_count` is correct
- [ ] Verify `actions_by_type` JSON is valid and sums equal `total_events`
- [ ] Run for same date twice; verify no duplicates and values unchanged
- [ ] Reconcile: SUM(total_events) = COUNT of enriched events for same date

---

### Task 6: Configure Snowflake Loading
**Status:** Pending
**Estimated Effort:** M (2-3 hours)
**Dependencies:** Task 5
**Priority:** High

**Description:**
Implement the Snowflake loading stage that creates the target table and DDL, exports aggregated Delta Lake data to a Snowflake-compatible staging area on S3, and executes COPY INTO with idempotent DELETE + LOAD pattern.

**Implementation Steps:**
1. Create Snowflake DDL scripts:
   - `sql/create_user_activity_daily.sql` — target table with primary key and clustering
   - `sql/create_quality_results.sql` — quality metrics table
   - `sql/create_pipeline_runs.sql` — pipeline metadata table
   - `sql/grant_permissions.sql` — role-based access grants
2. Create external stage in Snowflake pointing to S3 staging path
3. Implement loading script `loading/snowflake_loader.py`:
   - Export aggregated Delta Lake partition to Parquet in S3 staging area
   - Execute DELETE for target date range (idempotent reload)
   - Execute COPY INTO from S3 staging with `MATCH_BY_COLUMN_NAME`
   - Update `pipeline_runs` metadata table
4. Configure Snowflake connection using key-pair authentication (no password)
5. Set warehouse to auto-resume and auto-suspend (5 minutes)

**Acceptance Criteria:**
- [ ] Target table `analytics.user_activity_daily` created with correct schema and primary key
- [ ] External stage `@data_lake_stage` reads from S3 with correct IAM role
- [ ] DELETE + COPY INTO pattern produces identical results on re-run (idempotent)
- [ ] COPY INTO completes within 30 minutes for 2M rows
- [ ] Pipeline metadata recorded in `analytics.pipeline_runs`
- [ ] Warehouse auto-suspends after 5 minutes of inactivity
- [ ] **Data Validation:** Row count in Snowflake matches aggregated Delta Lake table for loaded dates

**Files to Modify:**
- `sql/create_user_activity_daily.sql`
- `sql/create_quality_results.sql`
- `sql/create_pipeline_runs.sql`
- `sql/grant_permissions.sql`
- `loading/snowflake_loader.py`
- `config/snowflake_config.py`

**Validation Required:**
- [ ] Load 100K rows; verify all rows present in Snowflake with correct column values
- [ ] Load same date twice; verify no duplicate rows (DELETE + COPY is idempotent)
- [ ] Verify primary key constraint on (`user_id`, `event_date`)
- [ ] Query `pipeline_runs` table and verify metadata is recorded
- [ ] Verify warehouse auto-suspends after idle period

---

### Task 7: Create Airflow DAG
**Status:** Pending
**Estimated Effort:** M (3 hours)
**Dependencies:** Task 2, Task 3, Task 4, Task 5, Task 6
**Priority:** High

**Description:**
Build the main Airflow DAG that orchestrates the entire daily pipeline: dimension export, ingestion check, staging, enrichment, aggregation, quality checks, Snowflake loading, materialized view refresh, and completion notification.

**Implementation Steps:**
1. Create DAG file `dags/dag_analytics_user_activity_v1.py`
2. Define DAG configuration:
   - Schedule: `0 2 * * *` (daily at 02:00 UTC)
   - Start date: configured via Airflow Variable
   - Catchup: False (backfill handled by separate DAG)
   - Max active runs: 1
   - Default retries: 3, retry delay: 10 minutes
3. Define tasks:
   - `dimension_export`: PythonOperator — run dimension export script
   - `check_ingestion`: S3KeySensor — verify raw data exists for target date
   - `staging`: EmrAddStepsOperator — submit staging Spark job
   - `quality_check_staging`: PythonOperator — run Great Expectations on staging
   - `enrichment`: EmrAddStepsOperator — submit enrichment Spark job
   - `aggregation`: EmrAddStepsOperator — submit aggregation Spark job
   - `quality_check_aggregation`: PythonOperator — run Great Expectations on aggregation
   - `snowflake_load`: SnowflakeOperator — execute loading SQL
   - `mv_refresh`: SnowflakeOperator — refresh materialized views
   - `notify_completion`: SlackWebhookOperator — send completion notification
4. Define task dependencies (linear chain with quality gates)
5. Configure SLA monitoring (4-hour SLA miss notification)
6. Add failure callbacks (PagerDuty for critical tasks, Slack for warnings)

**Acceptance Criteria:**
- [ ] DAG parses without errors (`python -c "from dags import dag_analytics_user_activity_v1"`)
- [ ] Task dependencies match the design data flow diagram
- [ ] SLA monitoring triggers alert if pipeline exceeds 4 hours
- [ ] Failed tasks retry 3 times with 10-minute delay
- [ ] Critical task failures trigger PagerDuty alert
- [ ] Completion notification sent to Slack with run summary
- [ ] DAG file size < 1 MB (MWAA limit)
- [ ] **Data Validation:** DAG end-to-end test with synthetic data produces correct output in Snowflake

**Files to Modify:**
- `dags/dag_analytics_user_activity_v1.py`
- `dags/callbacks/alerting.py`
- `config/airflow_variables.json`

**Validation Required:**
- [ ] DAG parsing test passes
- [ ] Trigger DAG manually with test date; verify all tasks execute in correct order
- [ ] Simulate task failure; verify retry and alerting behavior
- [ ] Verify SLA monitoring fires notification for slow runs

---

### Task 8: Set Up Great Expectations Quality Checks
**Status:** Pending
**Estimated Effort:** M (3 hours)
**Dependencies:** Task 3, Task 4, Task 5, Task 6
**Priority:** High

**Description:**
Configure Great Expectations validation suites for each pipeline stage (ingestion, staging, aggregation) including null checks, range validation, uniqueness checks, and cross-stage reconciliation.

**Implementation Steps:**
1. Initialize Great Expectations project: `great_expectations init`
2. Create data sources for S3/Delta Lake (Spark engine)
3. Create expectation suite `ingestion_validation`:
   - Column existence checks
   - Not-null checks on required columns
   - `event_type` allowlist validation
   - Row count thresholds (1M-200M per day)
   - `event_id` uniqueness
4. Create expectation suite `staging_validation`:
   - UUID format regex for `event_id`
   - `duration_seconds` range check (0-86400)
   - `session_id` not null
   - Event_id near-unique proportion (> 99.9%)
5. Create expectation suite `aggregation_validation`:
   - Compound uniqueness on (`user_id`, `event_date`)
   - `session_count` range (1-1000)
   - `total_duration_seconds` range (0-86400)
   - Row count thresholds (500K-10M)
6. Create cross-stage reconciliation checks:
   - Raw event count vs. aggregated `SUM(total_events)` (tolerance 0.5%)
   - Raw user count vs. aggregated row count (tolerance 0.1%)
7. Configure alert routing: critical failures -> PagerDuty, warnings -> Slack
8. Write quality results to `analytics.data_quality_results` in Snowflake

**Acceptance Criteria:**
- [ ] Three expectation suites configured and parseable
- [ ] Each suite runs in < 10 minutes on production-scale data
- [ ] Critical failures (completeness < 95%) halt pipeline via Airflow callback
- [ ] Warning-level issues (95-99.5%) logged but pipeline continues
- [ ] Quality results persisted to Snowflake with `run_id` for traceability
- [ ] Cross-stage reconciliation catches event count discrepancies > 0.5%
- [ ] **Data Validation:** Inject known bad data and verify expectations fail correctly

**Files to Modify:**
- `great_expectations/great_expectations.yml`
- `great_expectations/expectations/ingestion_validation.json`
- `great_expectations/expectations/staging_validation.json`
- `great_expectations/expectations/aggregation_validation.json`
- `great_expectations/checkpoints/pipeline_checkpoint.yml`
- `quality/reconciliation.py`
- `quality/alert_router.py`

**Validation Required:**
- [ ] Run suite on valid synthetic data; verify all expectations pass
- [ ] Inject 5% null values; verify completeness check fails at critical level
- [ ] Inject 1,000 duplicate (`user_id`, `event_date`) pairs; verify uniqueness check fails
- [ ] Run reconciliation with 2% event count variance; verify warning triggered
- [ ] Verify results appear in `analytics.data_quality_results` table

---

### Task 9: Create Snowflake Materialized Views
**Status:** Pending
**Estimated Effort:** S (1-2 hours)
**Dependencies:** Task 6
**Priority:** Medium

**Description:**
Create the four materialized views in Snowflake for pre-computed engagement metrics: daily active users, weekly active users, monthly active users, and retention cohorts.

**Implementation Steps:**
1. Create `analytics.mv_daily_active_users` — DAU by date, region, user tier
2. Create `analytics.mv_weekly_active_users` — WAU by week, region, user tier
3. Create `analytics.mv_monthly_active_users` — MAU by month, region, user tier
4. Create `analytics.mv_retention_cohorts` — retention by signup cohort week, region, user tier
5. Add clustering on `event_date` (or equivalent date column) for each view
6. Grant SELECT to `ANALYTICS_READER` and `DASHBOARD_SERVICE` roles
7. Add refresh commands to the loading DAG task
8. Verify query performance (< 5 seconds p95)

**Acceptance Criteria:**
- [ ] All four materialized views created with correct SQL logic
- [ ] DAU, WAU, MAU calculations verified against manual queries
- [ ] Retention cohort percentages match manual calculation for sample data
- [ ] Views refresh within 15 minutes total (all four)
- [ ] Query performance < 5 seconds (p95) on 90 days of data
- [ ] Correct role-based access grants in place
- [ ] **Data Validation:** DAU for a test date matches `COUNT(DISTINCT user_id)` from base table

**Files to Modify:**
- `sql/create_mv_daily_active_users.sql`
- `sql/create_mv_weekly_active_users.sql`
- `sql/create_mv_monthly_active_users.sql`
- `sql/create_mv_retention_cohorts.sql`
- `sql/grant_mv_permissions.sql`

**Validation Required:**
- [ ] Load 30 days of synthetic data; verify DAU/WAU/MAU numbers are mathematically correct
- [ ] Verify retention cohort: 100% of users active in week 0 (by definition)
- [ ] Time the refresh of all 4 views; confirm < 15 minutes total
- [ ] Run dashboard-style queries; verify < 5 second response time

---

### Task 10: Set Up Avro Schema Registry
**Status:** Pending
**Estimated Effort:** S (1-2 hours)
**Dependencies:** Task 2
**Priority:** Medium

**Description:**
Register the `UserEvent` Avro schema with the Confluent Schema Registry, configure compatibility settings, and integrate schema validation into the ingestion consumer.

**Implementation Steps:**
1. Define `UserEvent` Avro schema (JSON format) per design spec
2. Register schema under subject `user-events-value` via Schema Registry REST API
3. Set compatibility mode to BACKWARD for the subject
4. Update ingestion consumer to use Schema Registry for deserialization
5. Create schema evolution test: add an optional field, verify backward compatibility
6. Document schema registration and evolution process in runbook

**Acceptance Criteria:**
- [ ] Schema registered under `user-events-value` with schema ID assigned
- [ ] Compatibility mode set to BACKWARD
- [ ] Ingestion consumer deserializes events using Schema Registry (not hardcoded schema)
- [ ] Adding a new optional field passes compatibility check
- [ ] Removing a required field fails compatibility check (as expected)
- [ ] **Data Validation:** Produce Avro-encoded events via Schema Registry; verify ingestion consumer deserializes correctly

**Files to Modify:**
- `schemas/user_event.avsc`
- `schemas/register_schema.py`
- `ingestion/kafka_consumer.py` (update to use registry)
- `docs/schema_evolution_runbook.md`

**Validation Required:**
- [ ] Register schema via REST API; verify response contains schema ID
- [ ] Produce 1,000 events with registered schema; verify all deserialize in consumer
- [ ] Test backward compatibility: add optional field, register v2, verify both v1 and v2 events deserialize
- [ ] Test incompatible change: remove required field, verify registration rejected

---

### Task 11: Implement Monitoring and Alerting
**Status:** Pending
**Estimated Effort:** M (2-3 hours)
**Dependencies:** Task 7
**Priority:** Medium

**Description:**
Set up comprehensive monitoring for the pipeline including CloudWatch metrics, dashboards, PagerDuty integration for critical alerts, and Slack notifications for operational events.

**Implementation Steps:**
1. Create CloudWatch custom metrics:
   - `pipeline/ingestion_lag_seconds` — Kafka consumer lag
   - `pipeline/events_processed_count` — events per batch
   - `pipeline/events_rejected_count` — DLQ events per batch
   - `pipeline/stage_duration_seconds` — per-stage processing time
   - `pipeline/quality_check_pass_rate` — percentage of checks passing
2. Create CloudWatch dashboard `UserActivityPipeline`:
   - Ingestion lag over time
   - Events processed per batch
   - DLQ rate
   - Stage durations
   - EMR cluster utilization
3. Configure CloudWatch alarms:
   - Ingestion lag > 1M offsets -> PagerDuty
   - DLQ rate > 1% -> PagerDuty
   - Pipeline not completed by 04:00 UTC -> PagerDuty
   - EMR cluster cost > $50/day -> Slack warning
4. Integrate Airflow alerting:
   - Task failure -> PagerDuty (critical tasks) or Slack (non-critical)
   - SLA miss -> PagerDuty
   - Pipeline completion -> Slack summary with metrics
5. Create Snowflake query for daily pipeline health report

**Acceptance Criteria:**
- [ ] Custom CloudWatch metrics published from pipeline code
- [ ] Dashboard displays all key metrics with 1-minute granularity
- [ ] PagerDuty alert fires for ingestion lag > 1M offsets
- [ ] PagerDuty alert fires for pipeline SLA miss (not done by 04:00 UTC)
- [ ] Slack notification on pipeline completion includes: duration, row count, quality pass rate
- [ ] All alerts have runbook links in the notification body
- [ ] **Data Validation:** Trigger each alarm condition manually and verify notification delivery

**Files to Modify:**
- `monitoring/cloudwatch_metrics.py`
- `monitoring/cloudwatch_dashboard.json`
- `monitoring/cloudwatch_alarms.json`
- `dags/callbacks/alerting.py` (update with PagerDuty integration)
- `monitoring/pagerduty_config.py`
- `sql/pipeline_health_report.sql`

**Validation Required:**
- [ ] Publish test metric; verify it appears in CloudWatch within 2 minutes
- [ ] Trigger each alarm condition; verify PagerDuty or Slack notification received
- [ ] Verify dashboard renders correctly with live data
- [ ] Run pipeline health report query; verify output is accurate

---

### Task 12: Load Testing with Production-Scale Data
**Status:** Pending
**Estimated Effort:** L (4 hours)
**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8
**Priority:** High

**Description:**
Generate production-scale synthetic data (50M events), run the full pipeline end-to-end, and verify SLA compliance, data quality, and resource utilization.

**Implementation Steps:**
1. Create data generator `testing/generate_synthetic_data.py`:
   - Generate 50M realistic user events (2M unique users)
   - Distribute events across 24 hours with realistic patterns (peak at 14:00-18:00 UTC)
   - Include realistic session patterns (3-15 events per session, 1-5 sessions per user)
   - Include 0.1% malformed events (missing fields, invalid types)
   - Include 0.5% duplicate `event_id` values
2. Publish synthetic events to Kafka test topic
3. Run full Airflow DAG with production EMR cluster sizing (10 nodes)
4. Measure and record:
   - Ingestion time per micro-batch
   - Staging transformation duration
   - Enrichment duration
   - Aggregation duration
   - Snowflake loading duration
   - Total end-to-end duration
   - EMR cluster utilization (CPU, memory, shuffle)
   - Snowflake credits consumed
5. Verify data quality checks pass
6. Compare output row count against expected values
7. Run reconciliation checks

**Acceptance Criteria:**
- [ ] Full pipeline completes within 2-hour SLA
- [ ] All Great Expectations checks pass on production-scale data
- [ ] Cross-stage reconciliation within 0.5% tolerance
- [ ] No out-of-memory errors on EMR (memory utilization < 85%)
- [ ] No Spark executor failures or task retries > 3
- [ ] Snowflake loading completes within 30 minutes
- [ ] Total cost per run < $25 (EMR + Snowflake)
- [ ] **Data Validation:** Final Snowflake row count matches expected unique (user_id, event_date) combinations from generated data

**Files to Modify:**
- `testing/generate_synthetic_data.py`
- `testing/load_test_runner.py`
- `testing/performance_report.py`

**Validation Required:**
- [ ] 50M events fully processed end-to-end without failures
- [ ] Timing report shows each stage within SLA targets
- [ ] Quality checks pass (all expectations green)
- [ ] Reconciliation: raw events vs. aggregated totals within 0.5%
- [ ] Resource utilization report shows no bottlenecks

---

### Task 13: Build Backfill DAG
**Status:** Pending
**Estimated Effort:** M (2 hours)
**Dependencies:** Task 7
**Priority:** Medium

**Description:**
Create a separate Airflow DAG for historical backfill that accepts date range parameters and reprocesses all pipeline stages with configurable parallelism, using a dedicated Airflow pool to avoid contending with the daily DAG.

**Implementation Steps:**
1. Create DAG file `dags/dag_analytics_user_activity_backfill_v1.py`
2. Configure as manually triggered (no schedule, `schedule_interval=None`)
3. Accept parameters via `dag_run.conf`: `start_date`, `end_date`, `parallelism`
4. Generate date list from range, create dynamic task group per date
5. Each date runs: staging -> enrichment -> aggregation -> quality check -> snowflake load
6. Limit concurrency using Airflow pool `backfill_pool` (default: 5 parallel dates)
7. Use lower priority weight than daily DAG (1 vs 10)
8. Scale EMR cluster up for backfill (15 task nodes vs 5)
9. Use Snowflake `COMPUTE_WH_LARGE` for bulk loading
10. Send Slack notification on completion with summary

**Acceptance Criteria:**
- [ ] DAG accepts `start_date` and `end_date` via `dag_run.conf`
- [ ] Creates correct number of parallel task groups for date range
- [ ] Respects `backfill_pool` concurrency limit
- [ ] Does not interfere with daily DAG execution (separate pool, lower priority)
- [ ] 7-day backfill completes within 3 hours
- [ ] 90-day backfill completes within 12 hours (dedicated cluster)
- [ ] Completion notification includes date range, row counts, and duration
- [ ] **Data Validation:** Backfilled data matches fresh-run data for overlapping dates

**Files to Modify:**
- `dags/dag_analytics_user_activity_backfill_v1.py`
- `config/backfill_config.py`
- `config/airflow_pools.json`

**Validation Required:**
- [ ] Trigger backfill for 3 dates; verify all 3 processed successfully
- [ ] Verify pool limits respected (no more than configured parallel dates)
- [ ] Compare backfilled data against daily DAG output for same date; verify identical
- [ ] Run backfill while daily DAG is running; verify no resource contention

---

### Task 14: Documentation and Runbooks
**Status:** Pending
**Estimated Effort:** M (2 hours)
**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13
**Priority:** Medium

**Description:**
Create comprehensive documentation including architecture overview, operational runbooks for common scenarios (backfill, schema evolution, incident response), configuration reference, and onboarding guide for new team members.

**Implementation Steps:**
1. Create architecture documentation:
   - Pipeline overview diagram
   - Data flow description per stage
   - Technology stack and version matrix
2. Create operational runbooks:
   - Daily pipeline monitoring checklist
   - Backfill procedure (step-by-step with Airflow commands)
   - Schema evolution procedure (add field, deprecate field)
   - Incident response: pipeline failure (diagnosis, recovery steps)
   - Incident response: data quality alert (investigation, remediation)
   - EMR cluster scaling guide
   - Snowflake warehouse scaling guide
3. Create configuration reference:
   - All environment variables with descriptions and defaults
   - Airflow Variables and Connections setup
   - Snowflake roles and permissions matrix
4. Create onboarding guide:
   - Local development setup (Docker Compose for Kafka, Spark, Delta Lake)
   - How to run unit tests
   - How to trigger a test pipeline run
   - Code review checklist for pipeline changes

**Acceptance Criteria:**
- [ ] Architecture document accurately reflects implemented pipeline
- [ ] Runbooks contain specific commands (not just descriptions)
- [ ] A new team member can set up local development environment using onboarding guide
- [ ] Incident response runbook covers top 5 failure scenarios
- [ ] Configuration reference lists all 20+ config parameters with valid values
- [ ] Documentation reviewed by at least one other team member
- [ ] **Data Validation:** Walk through backfill runbook end-to-end; verify it works as documented

**Files to Modify:**
- `docs/architecture.md`
- `docs/runbooks/daily_monitoring.md`
- `docs/runbooks/backfill_procedure.md`
- `docs/runbooks/schema_evolution.md`
- `docs/runbooks/incident_response.md`
- `docs/configuration_reference.md`
- `docs/onboarding.md`
- `docs/code_review_checklist.md`

**Validation Required:**
- [ ] Have a team member follow the onboarding guide from scratch
- [ ] Execute each runbook procedure on staging environment
- [ ] Verify all configuration parameters documented match actual code

---

## Implementation Order

### Week 1: Infrastructure, Ingestion, and Core Transformations

**Day 1:**
1. Task 1: S3 bucket structure and Delta Lake setup (foundation, no dependencies)
2. Task 10: Avro Schema Registry setup (can be done in parallel with Task 1)

**Day 2:**
3. Task 2: Kafka consumer with Spark Structured Streaming (depends on Task 1)

**Day 3:**
4. Task 3: Staging transformation (depends on Task 2)
5. Task 4: Dimension enrichment (depends on Task 3, start dimension export in parallel)

**Day 4-5:**
6. Task 5: Aggregation logic (depends on Task 4 — largest task, 4-5 hours)
7. Task 6: Snowflake loading (depends on Task 5)

### Week 2: Orchestration, Quality, Testing, and Documentation

**Day 1:**
8. Task 7: Airflow DAG (depends on Tasks 2-6)
9. Task 8: Great Expectations quality checks (depends on Tasks 3-6, parallel with Task 7)

**Day 2:**
10. Task 9: Snowflake materialized views (depends on Task 6)
11. Task 11: Monitoring and alerting (depends on Task 7)

**Day 3:**
12. Task 12: Load testing with production-scale data (depends on Tasks 1-8)

**Day 4:**
13. Task 13: Backfill DAG (depends on Task 7)
14. Task 14: Documentation and runbooks (depends on all tasks)

## Progress Tracking

**Total Tasks:** 14
**Completed:** 0
**In Progress:** 0
**Remaining:** 14

**Estimated Total Effort:** ~36-45 hours (~2 weeks for 1 developer)

### Status Legend
- **Pending**: Not started
- **In Progress**: Currently being worked on
- **Completed**: Done and validated
- **Blocked**: Waiting on dependencies or external factors

### Progress by Category
- **Infrastructure**: 0/2 (Tasks 1, 10)
- **Ingestion**: 0/1 (Task 2)
- **Transformations**: 0/3 (Tasks 3, 4, 5)
- **Loading**: 0/2 (Tasks 6, 9)
- **Orchestration**: 0/2 (Tasks 7, 13)
- **Quality**: 0/1 (Task 8)
- **Monitoring**: 0/1 (Task 11)
- **Testing**: 0/1 (Task 12)
- **Documentation**: 0/1 (Task 14)

## Notes

- Tasks 1 and 10 are foundational and can be done in parallel on Day 1
- Task 2 (Kafka consumer) gates all downstream transformation tasks
- Tasks 3-6 form the core transformation chain and must be done sequentially
- Task 7 (Airflow DAG) and Task 8 (Great Expectations) can be done in parallel once transformations are complete
- Task 12 (load testing) should be done before production deployment — it validates all SLAs
- Task 13 (backfill DAG) can reuse most logic from Task 7 — lower effort
- Task 14 (documentation) should be done incrementally but final review is last

## Risk Items

- **Kafka consumer group quota**: Shared cluster may have quota limits — confirm with platform team before Task 2
- **EMR spot availability**: r5.2xlarge spot instances in target AZ may have limited capacity — configure instance fleet with fallback types (r5.xlarge, r5a.2xlarge)
- **Schema Registry access**: Verify pipeline service account has read access to Schema Registry before Task 10
- **Snowflake service account**: Confirm key-pair authentication is set up and `DATA_PIPELINE_ROLE` has required grants before Task 6
- **PostgreSQL replica**: Confirm replica is available during dimension export window (01:00-02:00 UTC) — coordinate with DBA team
