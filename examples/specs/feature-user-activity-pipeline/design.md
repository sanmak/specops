# Data Pipeline Design: User Activity Aggregation Pipeline

## Architecture Overview

The User Activity Aggregation Pipeline is a multi-stage batch and micro-batch data pipeline that processes raw user interaction events from Apache Kafka, transforms and enriches them through a series of PySpark jobs on AWS EMR, and loads the final aggregated results into Snowflake for analytics consumption.

**High-level architecture:**

- **Ingestion Layer:** Spark Structured Streaming consumes events from Kafka `user-events` topic in 15-minute micro-batches. Events are validated against the Avro Schema Registry, deduplicated by `event_id`, and written as Parquet files to the S3 raw zone.
- **Transformation Layer:** PySpark batch jobs on EMR read from the raw zone, apply type coercion and normalization (staging), join with user dimension data (enrichment), and compute daily aggregates (aggregation). All intermediate data is stored in Delta Lake format on S3 for ACID guarantees and schema enforcement.
- **Loading Layer:** Aggregated Delta Lake tables are exported to Snowflake via `COPY INTO` from staged S3 files. Materialized views in Snowflake pre-compute DAU, WAU, MAU, and retention cohorts.
- **Orchestration:** Apache Airflow 2.x on AWS MWAA manages the entire DAG, including the ingestion trigger, batch transformation chain, Snowflake loading, quality checks, and alerting.
- **Quality Layer:** Great Expectations validation suites run after each major pipeline stage. Critical failures halt the pipeline and trigger PagerDuty alerts; warnings are sent to Slack.

## Technical Decisions

### Decision 1: Processing Engine — PySpark vs Flink vs dbt

**Context:** Need a processing engine capable of handling 50M+ events/day with both micro-batch ingestion and daily batch aggregation workloads.

**Options Considered:**

1. **Apache Flink** — True streaming engine
   - Pros: Low-latency streaming, exactly-once semantics, mature Kafka connector
   - Cons: Operational complexity, team lacks Flink expertise, over-engineered for daily batch aggregation
2. **PySpark on EMR** — Unified batch and micro-batch engine
   - Pros: Team has deep Spark expertise, Structured Streaming for micro-batch, excellent S3/Delta Lake integration, cost-effective with spot instances
   - Cons: Higher latency than Flink for streaming, JVM overhead
3. **dbt + Snowflake** — SQL-based transformations
   - Pros: Simple, SQL-native, no cluster management
   - Cons: Cannot consume from Kafka directly, Snowflake compute costs for raw processing, limited for complex transformations (sessionization)

**Decision:** PySpark on AWS EMR

**Rationale:**
- The workload is fundamentally batch with a micro-batch ingestion component — Flink's streaming capabilities are unnecessary
- Team has 2+ years of PySpark production experience; Flink would require significant ramp-up
- EMR spot instances (r5.2xlarge) reduce compute costs by 60-70% compared to on-demand
- Spark Structured Streaming provides adequate micro-batch ingestion (15-min windows)
- Native Delta Lake support via `delta-spark` package
- Single engine for all transformation stages simplifies operations and debugging

### Decision 2: Orchestration — Airflow vs Step Functions vs Dagster

**Context:** Need a workflow orchestrator to manage pipeline dependencies, scheduling, retries, and monitoring.

**Options Considered:**

1. **Apache Airflow 2.x (MWAA)** — DAG-based workflow orchestrator
   - Pros: Already deployed on AWS MWAA, team familiarity, rich operator ecosystem, DAG-as-code, built-in retry and alerting
   - Cons: Scheduler can be a bottleneck, DAG parsing overhead, limited dynamic task generation
2. **AWS Step Functions** — Serverless state machine
   - Pros: Fully managed, tight AWS integration, visual workflow editor
   - Cons: Verbose JSON definitions, limited operator ecosystem, harder to test locally, no native Spark/Snowflake operators
3. **Dagster** — Modern data orchestrator
   - Pros: Asset-based model, excellent testing, built-in data quality, type system
   - Cons: Not yet deployed in our infrastructure, migration cost, smaller community

**Decision:** Apache Airflow 2.x on AWS MWAA

**Rationale:**
- MWAA is already deployed and operational — zero infrastructure setup
- Team is proficient with Airflow DAG development and debugging
- Rich operator library: `EmrAddStepsOperator`, `SnowflakeOperator`, `S3KeySensor`
- DAG-as-code versioned in Git alongside pipeline code
- Built-in retry policies, SLA monitoring, and Slack/PagerDuty integration
- Dagster's advantages (asset model, type system) don't justify migration cost for this project

### Decision 3: Storage Format — Parquet vs Delta Lake vs Apache Iceberg

**Context:** Need a storage format for intermediate pipeline data on S3 that supports schema enforcement, idempotent writes, and time travel for debugging.

**Options Considered:**

1. **Plain Parquet** — Columnar storage format
   - Pros: Universal compatibility, simple, no additional dependencies
   - Cons: No ACID transactions, no schema enforcement, no upsert support, manual partition management
2. **Delta Lake** — Open-source storage layer on Parquet
   - Pros: ACID transactions, schema enforcement and evolution, MERGE (upsert) support, time travel, compatible with Spark natively
   - Cons: Additional dependency (`delta-spark`), Delta-specific tooling for non-Spark readers
3. **Apache Iceberg** — Open table format
   - Pros: Engine-agnostic, hidden partitioning, snapshot isolation, growing ecosystem
   - Cons: Less mature Spark integration than Delta Lake, more complex configuration, team has no Iceberg experience

**Decision:** Delta Lake on S3

**Rationale:**
- ACID transactions ensure idempotent writes — critical for retry and backfill scenarios
- Schema enforcement catches upstream schema drift before it corrupts downstream tables
- `MERGE INTO` enables efficient upserts for the aggregation stage (reprocess T-1, T-2)
- Time travel (7-day default) enables debugging and auditing without separate snapshot tables
- Native Spark integration via `delta-spark` package (single JAR dependency)
- Team has prior Delta Lake experience from a related project

## Pipeline Stage Design

### Stage 1: Ingestion (Kafka to S3 Raw Zone)

**Input:**
- Kafka `user-events` topic (12 partitions, Avro-encoded with JSON fallback)
- Consumer group: `user-activity-pipeline`
- Starting offset: latest (initial), committed offset (subsequent)

**Output:**
- S3: `s3://data-lake/raw/user_events/event_date=YYYY-MM-DD/hour=HH/*.parquet`
- Partitioned by `event_date` and `hour`
- Parquet with Snappy compression

**Processing Logic:**
1. Create Spark Structured Streaming session with Kafka source
2. Deserialize Avro payload using Schema Registry client
3. Validate event schema: required fields (`event_id`, `user_id`, `event_type`, `timestamp`), type checks
4. Route invalid events to `user-events-dlq` Kafka topic with error reason
5. Deduplicate by `event_id` using watermark (24-hour window) and `dropDuplicates`
6. Normalize `timestamp` to UTC (handle timezone-aware and epoch formats)
7. Add processing metadata: `_ingested_at`, `_batch_id`, `_source_partition`
8. Write to S3 raw zone as Parquet, partitioned by `event_date` and `hour`
9. Commit Kafka offsets after successful write

**Error Handling:**
- Schema validation failures: route to DLQ, increment `events_rejected` counter
- Kafka connection loss: retry with exponential backoff (max 5 retries, 30s initial delay)
- S3 write failure: retry batch (idempotent writes via unique `_batch_id`)
- Out-of-order events: handled by 24-hour dedup watermark window

**Configuration:**
```python
INGESTION_CONFIG = {
    "kafka_bootstrap_servers": "${KAFKA_BROKERS}",
    "kafka_topic": "user-events",
    "consumer_group": "user-activity-pipeline",
    "trigger_interval": "15 minutes",
    "max_offsets_per_trigger": 500000,
    "watermark_delay": "24 hours",
    "output_path": "s3://data-lake/raw/user_events/",
    "checkpoint_path": "s3://data-lake/checkpoints/ingestion/",
    "dlq_topic": "user-events-dlq"
}
```

### Stage 2: Staging (Raw to Cleaned/Typed)

**Input:**
- S3 raw zone: `s3://data-lake/raw/user_events/event_date={date}/`
- Date range: T-2 to T (reprocess 2 trailing days for late arrivals)

**Output:**
- Delta Lake: `s3://data-lake/staging/user_events_cleaned/`
- Partitioned by `event_date`

**Processing Logic:**
1. Read Parquet files from raw zone for target date range
2. Apply strict type coercion:
   - `event_id`: STRING (UUID format validation)
   - `user_id`: STRING (non-empty)
   - `event_type`: STRING (validated against allowlist)
   - `timestamp`: TIMESTAMP (UTC)
   - `page_url`: STRING (URL format validation)
   - `session_id`: STRING (non-empty)
   - `duration_seconds`: INTEGER (>= 0)
   - `metadata`: MAP<STRING, STRING> (parse JSON, flatten top-level keys)
3. Normalize `event_type` values (lowercase, trim whitespace)
4. Filter out test/internal events (`user_id` not in internal allowlist)
5. Write to Delta Lake staging table using `MERGE` (upsert by `event_id`)
6. Compact small files (target: 128 MB per file)

**Error Handling:**
- Type coercion failures: log warning, cast to NULL, flag row with `_has_quality_issue = true`
- Empty input partitions: log warning, skip (do not fail pipeline)
- Delta Lake write conflicts: retry with conflict resolution (latest write wins)

**Configuration:**
```python
STAGING_CONFIG = {
    "input_path": "s3://data-lake/raw/user_events/",
    "output_path": "s3://data-lake/staging/user_events_cleaned/",
    "lookback_days": 2,
    "allowed_event_types": [
        "page_view", "click", "scroll", "form_submit", "search",
        "login", "logout", "signup", "purchase", "add_to_cart"
    ],
    "target_file_size_mb": 128
}
```

### Stage 3: Enrichment (Join with User Dimension)

**Input:**
- Delta Lake staging: `s3://data-lake/staging/user_events_cleaned/`
- User dimension snapshot: `s3://data-lake/dimensions/users/snapshot_date={date}/`

**Output:**
- Delta Lake: `s3://data-lake/enriched/user_events_enriched/`
- Partitioned by `event_date`

**Processing Logic:**
1. Export user dimension from PostgreSQL replica to S3 (daily snapshot via Airflow task)
   ```sql
   SELECT user_id, user_tier, signup_date, region, account_status, company_size
   FROM users
   WHERE account_status IN ('active', 'suspended')
      OR deactivated_at > CURRENT_DATE - INTERVAL '90 days'
   ```
2. Read staging events and user dimension snapshot
3. LEFT JOIN on `user_id` — preserve all events (including those from unknown/deleted users)
4. Add enrichment columns: `user_tier`, `signup_date`, `region`, `account_status`, `company_size`
5. Add derived columns:
   - `days_since_signup`: DATEDIFF(`event_date`, `signup_date`)
   - `user_cohort_week`: DATE_TRUNC('week', `signup_date`)
   - `is_new_user`: `days_since_signup` < 7
6. Write to Delta Lake enriched table using `MERGE` (upsert by `event_id`)

**Error Handling:**
- Dimension snapshot missing: fail task, alert (enrichment requires dimension data)
- User not found in dimension: set enrichment columns to NULL, flag `_enrichment_status = 'unmatched'`
- Stale dimension data (snapshot > 24h old): log warning, proceed with available snapshot

**Configuration:**
```python
ENRICHMENT_CONFIG = {
    "staging_path": "s3://data-lake/staging/user_events_cleaned/",
    "dimension_path": "s3://data-lake/dimensions/users/",
    "output_path": "s3://data-lake/enriched/user_events_enriched/",
    "pg_connection": "${POSTGRES_REPLICA_URI}",
    "dimension_query_path": "sql/extract_user_dimension.sql"
}
```

### Stage 4: Aggregation (Daily User Activity Rollup)

**Input:**
- Delta Lake enriched: `s3://data-lake/enriched/user_events_enriched/`
- Date range: T-2 to T (reprocess trailing days)

**Output:**
- Delta Lake: `s3://data-lake/aggregated/user_activity_daily/`
- Partitioned by `event_date`

**Processing Logic:**
1. Read enriched events for target date range
2. Compute session boundaries:
   - Order events by (`user_id`, `timestamp`)
   - New session starts when gap between consecutive events > 30 minutes
   - Assign `session_id` using window function with lag
3. Aggregate by (`user_id`, `event_date`):
   ```sql
   SELECT
     user_id,
     event_date,
     COUNT(DISTINCT session_id) AS session_count,
     SUM(duration_seconds) AS total_duration_seconds,
     COUNT(CASE WHEN event_type = 'page_view' THEN 1 END) AS page_views,
     COUNT(DISTINCT page_url) AS unique_pages,
     COUNT(*) AS total_events,
     MAP_FROM_ENTRIES(COLLECT_LIST(STRUCT(event_type, cnt))) AS actions_by_type,
     MIN(timestamp) AS first_event_at,
     MAX(timestamp) AS last_event_at,
     AVG(session_duration) AS avg_session_duration_seconds,
     -- Enrichment columns (take first non-null)
     FIRST(user_tier, true) AS user_tier,
     FIRST(signup_date, true) AS signup_date,
     FIRST(region, true) AS region,
     FIRST(account_status, true) AS account_status,
     FIRST(days_since_signup, true) AS days_since_signup,
     FIRST(user_cohort_week, true) AS user_cohort_week,
     FIRST(is_new_user, true) AS is_new_user
   FROM enriched_events
   GROUP BY user_id, event_date
   ```
4. Compute `actions_by_type` as a JSON map: `{"page_view": 45, "click": 12, "search": 3}`
5. Write to Delta Lake using `MERGE`:
   - Match on (`user_id`, `event_date`)
   - Update existing rows (re-aggregation for late events)
   - Insert new rows
6. Run OPTIMIZE on output table (Z-ORDER by `user_id`)

**Error Handling:**
- Zero events for a date: write empty partition marker, do not fail
- Aggregation produces unexpected row count (> 2x or < 0.5x previous day): log warning, continue
- Delta Lake merge conflicts: retry (last writer wins with idempotent aggregation)

**Configuration:**
```python
AGGREGATION_CONFIG = {
    "input_path": "s3://data-lake/enriched/user_events_enriched/",
    "output_path": "s3://data-lake/aggregated/user_activity_daily/",
    "lookback_days": 2,
    "session_timeout_minutes": 30,
    "z_order_columns": ["user_id"]
}
```

### Stage 5: Loading (Delta Lake to Snowflake)

**Input:**
- Delta Lake aggregated: `s3://data-lake/aggregated/user_activity_daily/`
- Date range: T-2 to T

**Output:**
- Snowflake table: `analytics.user_activity_daily`
- Materialized views: `analytics.mv_daily_active_users`, `analytics.mv_weekly_active_users`, `analytics.mv_monthly_active_users`, `analytics.mv_retention_cohorts`

**Processing Logic:**
1. Export aggregated Delta Lake partition to Snowflake-compatible Parquet on S3 staging area
   - Path: `s3://data-lake/snowflake-staging/user_activity_daily/{date}/`
2. Execute Snowflake `COPY INTO` from S3 staging:
   ```sql
   COPY INTO analytics.user_activity_daily
   FROM @data_lake_stage/snowflake-staging/user_activity_daily/{date}/
   FILE_FORMAT = (TYPE = PARQUET)
   MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
   ON_ERROR = ABORT_STATEMENT;
   ```
3. Handle existing data with DELETE + COPY (idempotent load):
   ```sql
   DELETE FROM analytics.user_activity_daily
   WHERE event_date BETWEEN '{start_date}' AND '{end_date}';

   COPY INTO analytics.user_activity_daily ...;
   ```
4. Refresh materialized views:
   ```sql
   ALTER MATERIALIZED VIEW analytics.mv_daily_active_users RESUME RECLUSTER;
   ALTER MATERIALIZED VIEW analytics.mv_weekly_active_users RESUME RECLUSTER;
   ALTER MATERIALIZED VIEW analytics.mv_monthly_active_users RESUME RECLUSTER;
   ALTER MATERIALIZED VIEW analytics.mv_retention_cohorts RESUME RECLUSTER;
   ```
5. Update pipeline metadata table:
   ```sql
   INSERT INTO analytics.pipeline_runs (pipeline_name, run_id, loaded_dates, row_count, loaded_at)
   VALUES ('user_activity_daily', '{run_id}', '{dates}', {count}, CURRENT_TIMESTAMP());
   ```

**Error Handling:**
- Snowflake `COPY INTO` failure: retry up to 3 times with exponential backoff
- Partial load (some files fail): `ON_ERROR = ABORT_STATEMENT` ensures atomicity
- Materialized view refresh timeout: log warning, views will auto-refresh on next query
- Snowflake warehouse suspended: auto-resume via warehouse configuration

**Configuration:**
```python
LOADING_CONFIG = {
    "staging_path": "s3://data-lake/snowflake-staging/user_activity_daily/",
    "snowflake_table": "analytics.user_activity_daily",
    "snowflake_warehouse": "COMPUTE_WH",
    "snowflake_role": "DATA_PIPELINE_ROLE",
    "snowflake_stage": "@data_lake_stage",
    "copy_on_error": "ABORT_STATEMENT"
}
```

## Data Flow Diagram

```
                         +------------------+
                         |   Kafka Cluster  |
                         | user-events topic|
                         |  (12 partitions) |
                         +--------+---------+
                                  |
                                  | Spark Structured Streaming
                                  | (15-min micro-batch)
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
          +-----------------+        +-------------------+
          | S3 Raw Zone     |        | Kafka DLQ Topic   |
          | (Parquet)       |        | user-events-dlq   |
          | /raw/user_events|        | (malformed events)|
          +--------+--------+        +-------------------+
                   |
                   | PySpark Batch (Daily 02:00 UTC)
                   | Type coercion, normalization
                   |
                   v
          +-------------------+
          | S3 Staging Zone   |
          | (Delta Lake)      |         +--------------------+
          | /staging/         |<------->| Great Expectations |
          | user_events_cleaned         | (Stage Validation) |
          +--------+----------+         +--------------------+
                   |
                   | LEFT JOIN
                   |
          +--------+----------+         +--------------------+
          |                   |         | PostgreSQL Replica  |
          v                   +-------->| users table         |
  +-------------------+                 | (daily S3 snapshot) |
  | S3 Enriched Zone  |                 +--------------------+
  | (Delta Lake)      |
  | /enriched/        |
  | user_events_enriched
  +--------+----------+
           |
           | GROUP BY user_id + event_date
           | Session computation, metrics
           |
           v
  +-------------------+
  | S3 Aggregated Zone|         +--------------------+
  | (Delta Lake)      |<------->| Great Expectations |
  | /aggregated/      |         | (Output Validation)|
  | user_activity_daily         +--------------------+
  +--------+----------+
           |
           | COPY INTO (DELETE + LOAD)
           |
           v
  +-------------------+         +--------------------+
  | Snowflake         |         | Analytics          |
  | analytics.        |-------->| Materialized Views |
  | user_activity_    |         | - mv_dau           |
  | daily             |         | - mv_wau           |
  +-------------------+         | - mv_mau           |
                                | - mv_retention     |
                                +--------------------+

  Orchestration: Apache Airflow (MWAA)
  +------------------------------------------------------------------+
  | DAG: dag_analytics_user_activity_v1                              |
  |                                                                  |
  | dimension_export -> ingestion_check -> staging -> enrichment     |
  |                                         |                        |
  |                                    quality_check_staging         |
  |                                         |                        |
  |                     enrichment -> aggregation -> quality_check   |
  |                                         |           |            |
  |                                    snowflake_load -> mv_refresh  |
  |                                         |                        |
  |                                    notify_completion             |
  +------------------------------------------------------------------+
```

## Schema Design

### Source Schema: Kafka Event (Avro/JSON)

```json
{
  "type": "record",
  "name": "UserEvent",
  "namespace": "com.example.events",
  "fields": [
    {"name": "event_id", "type": "string", "doc": "UUID, unique event identifier"},
    {"name": "user_id", "type": "string", "doc": "User identifier"},
    {"name": "event_type", "type": "string", "doc": "Event category (page_view, click, etc.)"},
    {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis", "doc": "Event time in epoch ms"},
    {"name": "page_url", "type": ["null", "string"], "default": null, "doc": "Page URL if applicable"},
    {"name": "session_id", "type": "string", "doc": "Client-generated session identifier"},
    {"name": "duration_seconds", "type": ["null", "int"], "default": null, "doc": "Time spent in seconds"},
    {"name": "metadata", "type": ["null", {"type": "map", "values": "string"}], "default": null, "doc": "Additional key-value metadata"}
  ]
}
```

### Staging Schema: Delta Lake (Cleaned/Typed)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `event_id` | STRING | No | UUID, primary dedup key |
| `user_id` | STRING | No | User identifier |
| `event_type` | STRING | No | Normalized event category |
| `timestamp` | TIMESTAMP | No | Event time (UTC) |
| `event_date` | DATE | No | Derived from timestamp (partition key) |
| `page_url` | STRING | Yes | Page URL |
| `session_id` | STRING | No | Client session identifier |
| `duration_seconds` | INT | Yes | Time spent (seconds, >= 0) |
| `metadata` | MAP<STRING, STRING> | Yes | Parsed key-value metadata |
| `_ingested_at` | TIMESTAMP | No | Ingestion timestamp |
| `_batch_id` | STRING | No | Ingestion batch identifier |
| `_has_quality_issue` | BOOLEAN | No | Flag for type coercion issues |

### Target Schema: Snowflake `analytics.user_activity_daily`

```sql
CREATE TABLE analytics.user_activity_daily (
    user_id            VARCHAR(64)       NOT NULL,
    event_date         DATE              NOT NULL,
    session_count      INTEGER           NOT NULL DEFAULT 0,
    total_duration_seconds  INTEGER      NOT NULL DEFAULT 0,
    page_views         INTEGER           NOT NULL DEFAULT 0,
    unique_pages       INTEGER           NOT NULL DEFAULT 0,
    total_events       INTEGER           NOT NULL DEFAULT 0,
    actions_by_type    VARIANT           NOT NULL,  -- JSON map {"page_view": 45, "click": 12}
    first_event_at     TIMESTAMP_NTZ     NOT NULL,
    last_event_at      TIMESTAMP_NTZ     NOT NULL,
    avg_session_duration_seconds  FLOAT  NULL,
    -- Enrichment columns
    user_tier          VARCHAR(32)       NULL,      -- 'free', 'pro', 'enterprise'
    signup_date        DATE              NULL,
    region             VARCHAR(64)       NULL,
    account_status     VARCHAR(32)       NULL,      -- 'active', 'suspended', 'deactivated'
    days_since_signup  INTEGER           NULL,
    user_cohort_week   DATE              NULL,
    is_new_user        BOOLEAN           NULL,
    -- Metadata
    _loaded_at         TIMESTAMP_NTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    _pipeline_run_id   VARCHAR(128)      NOT NULL,

    CONSTRAINT pk_user_activity_daily PRIMARY KEY (user_id, event_date)
);

-- Clustering for query performance
ALTER TABLE analytics.user_activity_daily
  CLUSTER BY (event_date, region);

-- Grant access
GRANT SELECT ON analytics.user_activity_daily TO ROLE ANALYTICS_READER;
GRANT SELECT ON analytics.user_activity_daily TO ROLE DASHBOARD_SERVICE;
```

### Materialized Views

```sql
-- Daily Active Users
CREATE MATERIALIZED VIEW analytics.mv_daily_active_users AS
SELECT
    event_date,
    region,
    user_tier,
    COUNT(DISTINCT user_id) AS dau,
    SUM(total_events) AS total_events,
    SUM(page_views) AS total_page_views,
    AVG(session_count) AS avg_sessions_per_user,
    AVG(total_duration_seconds) AS avg_duration_per_user
FROM analytics.user_activity_daily
GROUP BY event_date, region, user_tier;

-- Weekly Active Users
CREATE MATERIALIZED VIEW analytics.mv_weekly_active_users AS
SELECT
    DATE_TRUNC('week', event_date) AS week_start,
    region,
    user_tier,
    COUNT(DISTINCT user_id) AS wau
FROM analytics.user_activity_daily
GROUP BY DATE_TRUNC('week', event_date), region, user_tier;

-- Monthly Active Users
CREATE MATERIALIZED VIEW analytics.mv_monthly_active_users AS
SELECT
    DATE_TRUNC('month', event_date) AS month_start,
    region,
    user_tier,
    COUNT(DISTINCT user_id) AS mau
FROM analytics.user_activity_daily
GROUP BY DATE_TRUNC('month', event_date), region, user_tier;

-- Retention Cohorts
CREATE MATERIALIZED VIEW analytics.mv_retention_cohorts AS
SELECT
    user_cohort_week,
    region,
    user_tier,
    COUNT(DISTINCT CASE WHEN days_since_signup BETWEEN 0 AND 6 THEN user_id END) AS week_0_users,
    COUNT(DISTINCT CASE WHEN days_since_signup BETWEEN 7 AND 13 THEN user_id END) AS week_1_users,
    COUNT(DISTINCT CASE WHEN days_since_signup BETWEEN 14 AND 27 THEN user_id END) AS week_2_users,
    COUNT(DISTINCT CASE WHEN days_since_signup BETWEEN 28 AND 55 THEN user_id END) AS week_4_users,
    COUNT(DISTINCT CASE WHEN days_since_signup BETWEEN 56 AND 83 THEN user_id END) AS week_8_users,
    COUNT(DISTINCT CASE WHEN days_since_signup BETWEEN 84 AND 90 THEN user_id END) AS week_12_users
FROM analytics.user_activity_daily
WHERE user_cohort_week IS NOT NULL
GROUP BY user_cohort_week, region, user_tier;
```

### Quality Metrics Table

```sql
CREATE TABLE analytics.data_quality_results (
    run_id             VARCHAR(128)      NOT NULL,
    pipeline_name      VARCHAR(128)      NOT NULL,
    stage_name         VARCHAR(64)       NOT NULL,
    check_name         VARCHAR(256)      NOT NULL,
    check_type         VARCHAR(64)       NOT NULL,  -- 'completeness', 'validity', 'uniqueness', 'accuracy'
    status             VARCHAR(16)       NOT NULL,  -- 'passed', 'failed', 'warning'
    expected_value     VARCHAR(256)      NULL,
    observed_value     VARCHAR(256)      NULL,
    details            VARIANT           NULL,
    checked_at         TIMESTAMP_NTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP(),

    CONSTRAINT pk_quality_results PRIMARY KEY (run_id, stage_name, check_name)
);
```

## Data Contracts

### Input Contract: Kafka Event Schema

**Registry:** Confluent Schema Registry at `${SCHEMA_REGISTRY_URL}`
**Subject:** `user-events-value`
**Compatibility:** BACKWARD (new schemas can remove optional fields, add optional fields)

| Field | Type | Required | Contract |
|-------|------|----------|----------|
| `event_id` | string (UUID) | Yes | Globally unique, producer-generated |
| `user_id` | string | Yes | Non-empty, matches `^[a-zA-Z0-9_-]+$` |
| `event_type` | string | Yes | Must be in registered allowlist |
| `timestamp` | long (epoch ms) | Yes | Within 48 hours of current time |
| `page_url` | string | No | Valid URL format if present |
| `session_id` | string | Yes | Non-empty |
| `duration_seconds` | int | No | >= 0 if present |
| `metadata` | map<string, string> | No | Max 20 keys, max 256 chars per value |

**SLA:** Events must be produced within 5 seconds of user action. Schema Registry must be available 99.9% of the time.

### Output Contract: Snowflake Aggregated Table

**Table:** `analytics.user_activity_daily`
**Owner:** Data Engineering team
**Consumers:** Analytics team, Dashboard service, Data Science team

| Guarantee | Details |
|-----------|---------|
| Freshness | Previous day's data available by 04:00 UTC |
| Completeness | >= 99.5% of events reflected in aggregation |
| Uniqueness | One row per (`user_id`, `event_date`) — enforced by primary key |
| Schema stability | Columns are additive-only; existing columns never removed or renamed |
| Backfill | Historical corrections within 48h; consumers notified via Slack |

### Breaking Change Policy

- **Additive changes** (new optional columns, new event types): No notice required, backward compatible
- **Non-breaking modifications** (column type widening, default value changes): 1-week notice via Slack `#data-contracts` channel
- **Breaking changes** (column removal, rename, type narrowing): 2-week deprecation period, migration guide provided, coordinated with all consumers
- **Emergency changes** (security, data corruption): Immediate change with post-incident notification

## Data Quality & Validation

### Great Expectations Suite: `user_activity_pipeline`

**Stage: Ingestion (post-raw zone write)**
```yaml
expectations:
  - expect_column_to_exist: event_id
  - expect_column_to_exist: user_id
  - expect_column_to_exist: event_type
  - expect_column_to_exist: timestamp
  - expect_column_values_to_not_be_null:
      column: event_id
  - expect_column_values_to_not_be_null:
      column: user_id
  - expect_column_values_to_not_be_null:
      column: event_type
  - expect_column_values_to_be_unique:
      column: event_id
  - expect_column_values_to_be_in_set:
      column: event_type
      value_set: [page_view, click, scroll, form_submit, search, login, logout, signup, purchase, add_to_cart]
  - expect_table_row_count_to_be_between:
      min_value: 1000000   # At least 1M events per day
      max_value: 200000000 # Circuit breaker at 200M
```

**Stage: Staging (post-Delta Lake write)**
```yaml
expectations:
  - expect_column_values_to_not_be_null:
      column: event_date
  - expect_column_values_to_match_regex:
      column: event_id
      regex: "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
  - expect_column_values_to_be_between:
      column: duration_seconds
      min_value: 0
      max_value: 86400   # Max 24 hours
      mostly: 0.99
  - expect_column_values_to_not_be_null:
      column: session_id
  - expect_column_proportion_of_unique_values_to_be_between:
      column: event_id
      min_value: 0.999
```

**Stage: Aggregation (post-aggregated Delta Lake write)**
```yaml
expectations:
  - expect_compound_columns_to_be_unique:
      column_list: [user_id, event_date]
  - expect_column_values_to_be_between:
      column: session_count
      min_value: 1
      max_value: 1000
      mostly: 0.999
  - expect_column_values_to_be_between:
      column: total_duration_seconds
      min_value: 0
      max_value: 86400
      mostly: 0.999
  - expect_column_values_to_be_between:
      column: page_views
      min_value: 0
      max_value: 50000
      mostly: 0.999
  - expect_table_row_count_to_be_between:
      min_value: 500000    # At least 500K users/day
      max_value: 10000000  # Circuit breaker at 10M
```

**Cross-Stage Reconciliation:**
```yaml
reconciliation:
  - name: raw_vs_aggregated_event_count
    source_query: "SELECT COUNT(*) FROM raw_events WHERE event_date = '{date}'"
    target_query: "SELECT SUM(total_events) FROM aggregated WHERE event_date = '{date}'"
    tolerance: 0.005  # 0.5% variance allowed
  - name: raw_vs_aggregated_user_count
    source_query: "SELECT COUNT(DISTINCT user_id) FROM raw_events WHERE event_date = '{date}'"
    target_query: "SELECT COUNT(*) FROM aggregated WHERE event_date = '{date}'"
    tolerance: 0.001  # 0.1% variance allowed
```

## Throughput & Latency

### Ingestion Performance

| Metric | Target | Sizing |
|--------|--------|--------|
| Kafka consumption rate | 5,000 events/sec sustained | 12 partitions, 3 Spark executors |
| Micro-batch processing | < 5 min per 15-min window | ~4.5M events per batch |
| S3 write throughput | 200 MB/min | Snappy-compressed Parquet |
| End-to-end ingestion lag | < 30 min | Trigger interval + processing |

### Aggregation Performance

| Metric | Target | Sizing |
|--------|--------|--------|
| Daily batch processing | < 90 min for 50M events | 10-node EMR cluster (r5.2xlarge) |
| Staging transformation | < 20 min | Parallel partition processing |
| Enrichment (with join) | < 15 min | Broadcast join (user dim ~500 MB) |
| Aggregation computation | < 40 min | Shuffle-based GROUP BY |
| Delta Lake MERGE | < 15 min | Z-ORDER optimized, partition pruning |

### EMR Cluster Sizing

```
Cluster: emr-user-activity-pipeline
Master:  1x m5.2xlarge (8 vCPU, 32 GB)
Core:    5x r5.2xlarge (8 vCPU, 64 GB) — on-demand
Task:    5x r5.2xlarge (8 vCPU, 64 GB) — spot instances (60-70% savings)

Spark Configuration:
  spark.executor.memory = 48g
  spark.executor.cores = 4
  spark.executor.instances = 18
  spark.sql.shuffle.partitions = 200
  spark.sql.adaptive.enabled = true
  spark.sql.adaptive.coalescePartitions.enabled = true
  spark.delta.optimizeWrite.enabled = true
```

### Snowflake Loading Performance

| Metric | Target | Configuration |
|--------|--------|---------------|
| COPY INTO throughput | < 30 min for 2M rows | Medium warehouse, parallel files |
| MV refresh | < 15 min (all 4 views) | Auto-suspend after 5 min idle |
| Query latency (MVs) | < 5 sec (p95) | Clustered on `event_date` |

### Bottleneck Analysis

| Stage | Bottleneck | Mitigation |
|-------|-----------|------------|
| Enrichment | JDBC read from PostgreSQL replica | Daily S3 snapshot (eliminates JDBC during pipeline) |
| Aggregation | Shuffle for GROUP BY on 50M rows | Adaptive query execution, salted keys for hot users |
| Loading | Snowflake warehouse cold start | Keep warehouse auto-resume with 5-min auto-suspend |
| MV Refresh | Full table scan for retention cohorts | Partition by `event_date`, limit scan to 90-day window |

## Backfill Strategy

### Approach

Backfill uses a parameterized Airflow DAG (`dag_analytics_user_activity_backfill_v1`) that accepts `start_date` and `end_date` parameters and reprocesses all pipeline stages for the specified date range.

### Process

1. **Trigger:** Manual trigger via Airflow UI or CLI with date range parameters
2. **Source:** Re-read from S3 raw zone (Parquet files retained for 90 days per lifecycle policy)
3. **Processing:** Run staging, enrichment, and aggregation for each date in range (parallelism: 5 dates concurrently)
4. **Loading:** DELETE + COPY INTO for each backfilled date in Snowflake (idempotent)
5. **Validation:** Run Great Expectations suite on backfilled data
6. **Notification:** Slack notification on completion with summary (dates processed, row counts, quality results)

### Performance Estimates

| Scenario | Duration | Resources |
|----------|----------|-----------|
| Single day backfill | ~45 min | Existing EMR cluster |
| 7-day backfill | ~3 hours | Existing EMR cluster (5 dates parallel) |
| 30-day backfill | ~6 hours | Dedicated EMR cluster (10 dates parallel) |
| 90-day backfill (full) | ~12 hours | Dedicated larger EMR cluster (15 dates parallel) |

### Constraints

- Raw data retention: 90 days (cannot backfill beyond this without restoring from Glacier)
- Dedicated EMR cluster recommended for backfills > 7 days (avoid impacting daily pipeline)
- Snowflake warehouse should be scaled up to Large for backfills > 30 days
- User dimension snapshots retained for 90 days; older backfills use earliest available snapshot
- Backfill DAG has lower Airflow pool priority than daily DAG to avoid resource contention

### Backfill DAG Configuration

```python
BACKFILL_CONFIG = {
    "dag_id": "dag_analytics_user_activity_backfill_v1",
    "max_parallel_dates": 5,
    "emr_instance_count": 15,      # Larger cluster for backfill
    "emr_instance_type": "r5.2xlarge",
    "snowflake_warehouse": "COMPUTE_WH_LARGE",  # Scale up for bulk load
    "pool": "backfill_pool",        # Separate pool from daily
    "priority_weight": 1            # Lower than daily (weight 10)
}
```

## Testing Strategy

### Unit Tests (PySpark)

- **Transformation functions:** Test each transformation function (dedup, type coercion, sessionization, aggregation) with small DataFrames using `pyspark.testing`
- **Schema validation:** Test Avro deserialization with valid and invalid payloads
- **Configuration parsing:** Test config loading with valid, invalid, and missing values
- **Error handling:** Test DLQ routing, retry logic, and graceful degradation

### Integration Tests (Local Spark + Delta Lake)

- **End-to-end stage tests:** Run each pipeline stage with synthetic data on local Spark
- **Delta Lake operations:** Test MERGE upsert, schema enforcement, and time travel on local Delta tables
- **Cross-stage data flow:** Verify data flows correctly from raw -> staging -> enriched -> aggregated
- **Idempotency:** Run same stage twice with identical input, verify identical output

### Great Expectations Tests

- **Suite validation:** Run expectation suites against synthetic datasets with known properties
- **Failure scenarios:** Test with data that intentionally violates expectations (nulls, out-of-range, duplicates)
- **Alert routing:** Verify critical failures trigger PagerDuty, warnings trigger Slack

### Airflow DAG Tests

- **DAG parsing:** Verify DAG loads without errors (`python -c "from dags import ..."`)
- **Task dependencies:** Validate task dependency graph matches expected order
- **Sensor behavior:** Test S3KeySensor with mock S3 (file exists, timeout scenarios)
- **Retry behavior:** Verify retry configuration per task

### Load Tests

- **Production-scale synthetic data:** Generate 50M events and run full pipeline
- **Verify SLA compliance:** Processing completes within 2 hours
- **Resource monitoring:** Track EMR memory, CPU, shuffle spill, and Spark executor utilization
- **Snowflake credit tracking:** Measure warehouse credit consumption per run

## Risks & Mitigations

### Risk 1: Kafka Consumer Lag Under High Volume

**Impact:** Ingestion falls behind, data freshness SLA violated
**Probability:** Medium (peak traffic during product launches or marketing campaigns)
**Mitigation:**
- Configure `max_offsets_per_trigger` to bound each micro-batch
- Auto-scale Spark Structured Streaming executors based on lag metric
- Set up CloudWatch alarm on consumer lag > 1M offsets
- Emergency procedure: increase trigger frequency temporarily (15 min -> 5 min)

### Risk 2: EMR Spot Instance Termination

**Impact:** Running Spark job fails mid-execution, requires restart
**Probability:** Medium (spot instances have 5-15% interruption rate)
**Mitigation:**
- Use spot instances only for task nodes (core nodes are on-demand)
- Enable Spark speculation for long-running tasks
- Configure EMR managed scaling with instance fleet (fall back to alternative instance types)
- Delta Lake checkpointing ensures no data loss on restart
- Airflow retry policy: 3 retries with 10-minute delay

### Risk 3: Schema Evolution Breaking Pipeline

**Impact:** Deserialization failures, data loss, pipeline halt
**Probability:** Low (Schema Registry enforces backward compatibility)
**Mitigation:**
- Avro Schema Registry with BACKWARD compatibility mode
- Schema validation at ingestion stage routes incompatible events to DLQ
- Pipeline alerts on DLQ message rate > threshold
- Schema change review process: data engineering approval required for `user-events` schema changes

### Risk 4: Snowflake Credit Overconsumption

**Impact:** Unexpected cloud costs, budget overrun
**Probability:** Low-Medium (backfills, query spikes, or warehouse left running)
**Mitigation:**
- Warehouse auto-suspend after 5 minutes of inactivity
- Resource monitor with credit quota (alert at 80%, suspend at 100%)
- Use Medium warehouse for daily loads; scale up only for backfills
- Monthly cost review with resource monitor reports
- Estimated daily cost: ~$8-12 (Snowflake) + ~$15-20 (EMR spot)

### Risk 5: PostgreSQL Replica Load from Dimension Export

**Impact:** Replica lag increases, affecting other consumers
**Probability:** Low (daily snapshot is a single bounded query)
**Mitigation:**
- Export runs during off-peak hours (01:00-02:00 UTC)
- Query uses read replica, never primary
- S3 snapshot approach eliminates repeated JDBC queries during pipeline
- If replica is lagging, use previous day's snapshot (with warning)
