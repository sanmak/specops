## Vertical Adaptation Rules

When using the default hardcoded templates (not custom templates), adapt the spec structure based on the detected vertical. These rules tell you which sections to skip, rename, or replace.

### infrastructure

**Domain vocabulary:** "Components" → "Resources"; "API Endpoints" → "Resource Definitions"; "User Stories" → "Infrastructure Requirements"; "Sequence Diagrams" → "Provisioning Flow"; "Data Model" → "State & Configuration"

**requirements.md:** Replace "User Stories" with "Infrastructure Requirements" (As an operator/SRE, I need...). Replace "Non-Functional Requirements" with "Operational Requirements" (SLOs, uptime, recovery). Add "Resource Inventory" section.

**design.md:** Replace "Component Design" with "Infrastructure Topology". Replace "Sequence Diagrams" with "Provisioning/Deployment Flow". Replace "Data Model Changes" with "State & Configuration Management". Replace "API Changes" with "Resource Definitions" (Terraform resources, K8s manifests, etc.). Rename "Rollout Plan" to "Deployment Strategy" (blue-green, canary, rolling). Rename "Security Considerations" to "Security & Compliance".

**tasks.md:** Add "Validation Steps" per task (plan output, dry-run results). Add "Rollback Steps" per task.

### data

**Domain vocabulary:** "Components" → "Pipeline Stages"; "API Endpoints" → "Data Contracts"; "User Stories" → "Data Requirements"; "Sequence Diagrams" → "Data Flow Diagrams"; "Data Model" → "Schema Design"

**requirements.md:** Replace "User Stories" with "Data Requirements" (sources, transformations, destinations). Add "Data Quality Requirements" section (validation rules, SLAs, freshness). Add "Volume & Velocity" section. Replace "Non-Functional Requirements" with "Pipeline SLAs" (latency, throughput, freshness).

**design.md:** Replace "Component Design" with "Pipeline Stage Design". Replace "Sequence Diagrams" with "Data Flow Diagrams". Replace "Data Model Changes" with "Schema Design" (source, staging, target schemas). Replace "API Changes" with "Data Contracts" (input/output schemas, formats). Add "Backfill Strategy" section. Rename "Performance Considerations" to "Throughput & Latency".

**tasks.md:** Add "Data Validation" acceptance criteria per task. Replace "Tests Required" with "Validation Required" (data quality checks, reconciliation).

### library

**Domain vocabulary:** "User Stories" → "Developer Use Cases"; "Users" → "Consumers/Developers"; "API Endpoints" → "Public API Surface"; "Components" → "Modules"

**requirements.md:** Replace "User Stories" with "Developer Use Cases" (As a developer using this library, I want...). Add "API Design Principles" section. Add "Compatibility Requirements" section (runtimes, module formats, bundle size). Replace "Non-Functional Requirements" with "Library Quality Requirements" (tree-shaking, type safety, dependencies).

**design.md:** Replace "Component Design" with "Module Design". Replace "API Changes" with "Public API Surface" (exports, types, function signatures). Replace "Sequence Diagrams" with "Usage Examples" (code snippets). Rename "Rollout Plan" to "Release Plan" (versioning, changelog, migration guide). Skip "Data Model Changes" unless the library manages state.

**tasks.md:** Add "Documentation Required" flag per task. Add "Breaking Change" flag per task. Add "Migration Guide" acceptance criterion for breaking changes.

### frontend

**design.md only:** Rename "Data Model Changes" to "State Management" (if using Redux/Zustand/etc.) or skip entirely. Skip "API Changes" if only consuming existing APIs.

No other adaptations — frontend is well-served by default templates.

### backend / fullstack

No adaptations needed — default templates are designed for these verticals.

### Applying Adaptation Rules

1. Check the detected vertical
2. Apply the relevant rules: skip listed sections, rename headers, use domain vocabulary
3. If a section is listed as "skip" but IS relevant to the specific request, keep it — use judgment
4. Adaptation rules are NOT applied when using a custom template file (the custom template defines its own structure)
