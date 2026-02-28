# Data Pipeline Design: {{title}}

## Architecture Overview
High-level description of the pipeline architecture.

## Technical Decisions

### Decision 1: [Title]
**Context:** Why this decision is needed
**Options Considered:**
1. Option A - Pros/Cons
2. Option B - Pros/Cons

**Decision:** Option [selected]
**Rationale:** Why this option was chosen

## Pipeline Stage Design

### Stage 1: [Name]
**Type:** [Ingestion / Transformation / Validation / Loading]
**Input:** [schema/format]
**Output:** [schema/format]
**Processing:** [logic description]
**Error Handling:** [dead-letter, retry, skip]

### Stage 2: [Name]
...

## Data Flow Diagram

```
Source A -> Ingestion -> Staging -> Transform -> Validate -> Target
Source B -> Ingestion ---^
```

## Schema Design

### Source Schema
```
source_table:
  - field1: type
  - field2: type
```

### Target Schema
```
target_table:
  - field1: type (from source.field1)
  - field2: type (derived)
```

## Data Contracts
- Input format: [JSON/Avro/Parquet/CSV]
- Output format: [JSON/Avro/Parquet/CSV]
- Schema versioning: [approach]
- Breaking change policy: [approach]

## Data Quality & Validation
- Validation rules: [per-field or per-record]
- Anomaly detection: [approach]
- Reconciliation: [source-to-target checks]

## Throughput & Latency
- Processing rate target: [records/second]
- Bottleneck analysis: [identified bottlenecks]
- Optimization approach: [partitioning, parallelism, etc.]

## Backfill Strategy
- Approach: [full reprocess / incremental]
- Time estimate: [duration]
- Impact on production: [description]

## Testing Strategy
- Unit tests: [transformation logic]
- Integration tests: [end-to-end pipeline]
- Data validation: [quality checks]

## Risks & Mitigations
- **Risk 1:** Description -> **Mitigation:** Strategy
- **Risk 2:** Description -> **Mitigation:** Strategy
