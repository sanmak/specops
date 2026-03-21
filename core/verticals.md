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

### builder

**Domain vocabulary:** "Components" → "Product Modules"; "API Endpoints" → "Integration Points"; "User Stories" → "Product Requirements"; "Sequence Diagrams" → "System Flow"; "Data Model" → "Data Architecture"; "Rollout Plan" → "Ship Plan"

**requirements.md:** Replace "User Stories" with "Product Requirements" (As a user/customer, I need... — framed around product outcomes, not implementation layers). Replace "Non-Functional Requirements" with "Product Quality Attributes" (performance, reliability, security, cost — from a product-shipping perspective). Add "Scope Boundary" section (explicitly state what ships in v1 vs. what is deferred — this is mandatory for builders to prevent scope creep).

**design.md:** Replace "Component Design" with "Product Module Design" (each module is a shippable product capability, not a code component). Replace "Sequence Diagrams" with "System Flow" (end-to-end flow from user action to infrastructure, crossing all layers). Replace "API Changes" with "Integration Points" (APIs, webhooks, third-party services, infra interfaces — anything that connects modules). Rename "Rollout Plan" to "Ship Plan" (what goes live first, how to validate with real users, rollback triggers). Skip sections that don't apply — a builder spec should be lean.

**tasks.md:** Add "Domain" tag per task (e.g., `frontend`, `backend`, `infra`, `data`, `devops`) — the builder works all domains, so tasks must be tagged for context-switching clarity. Add "Ship Blocking" flag per task (is this task required for the first shippable version, or can it follow later).

**Builder simplicity guardrail:** The Builder vertical covers the broadest possible scope. To prevent spec bloat: (1) Only include design.md sections for domains the specific request actually touches — do NOT speculatively add infrastructure, data, or frontend sections "because a builder might need them." (2) The Scope Boundary section in requirements.md is mandatory — it forces explicit deferral of non-essential work. (3) Tasks should target the shortest path to a shippable product; optimization, observability, and polish tasks should be flagged as non-ship-blocking unless the request specifically demands them.

### migration

**Domain vocabulary:** "Components" → "Systems"; "API Endpoints" → "Integration Boundaries"; "User Stories" → "Migration Requirements"; "Sequence Diagrams" → "Migration Flow"; "Data Model" → "Data Migration Design"; "Rollout Plan" → "Cutover Plan"

**requirements.md:** Replace "User Stories" with "Migration Requirements" (As a [role], I need [capability] migrated from [source] to [target] so that [benefit]). Replace "Non-Functional Requirements" with "Migration Constraints" (downtime tolerance, data integrity requirements, performance parity, backward compatibility period). Add "Source System Analysis" section (current system capabilities being migrated, known limitations, dependencies). Add "Compatibility Requirements" section (coexistence period, backward compatibility, rollback window).

**design.md:** Replace "Component Design" with "Migration Architecture". Add "Source System" section (current architecture being migrated from). Add "Target System" section (architecture being migrated to). Replace "Sequence Diagrams" with "Migration Flow" (data migration sequence, traffic cutover sequence). Replace "Data Model Changes" with "Data Migration Design" (schema mapping, transformation rules, validation). Replace "API Changes" with "Integration Boundaries" (APIs that must remain stable during migration, adapter/facade interfaces). Replace "Rollout Plan" with "Cutover Plan" (migration phases, coexistence strategy, traffic shifting, rollback triggers, success criteria per phase). Add "Coexistence Strategy" section (how source and target systems run simultaneously — routing rules, feature flags, data sync). Skip "Future Enhancements" (migrations have a defined end state).

**tasks.md:** Add "Migration Phase" tag per task (values: `prepare`, `migrate`, `validate`, `cutover`). Add "Rollback Steps" per task (what to undo if this task's migration fails). Add "Validation Steps" per task (how to verify this step completed correctly before proceeding).

### backend / fullstack

No adaptations needed — default templates are designed for these verticals.

### Vocabulary Verification

After generating spec files in Phase 2, verify that vertical-specific vocabulary was applied. For each non-default vertical, check that prohibited default terms do not remain in the generated spec files:

| Vertical | Prohibited Default Terms |
| --- | --- |
| infrastructure | "User Stories", "API Endpoints", "Components" (when "Resources" applies), "Sequence Diagrams", "Data Model" |
| data | "User Stories", "API Endpoints", "Components" (when "Pipeline Stages" applies), "Sequence Diagrams", "Data Model" |
| library | "User Stories" (when "Developer Use Cases" applies), "API Endpoints" (when "Public API Surface" applies) |
| builder | "User Stories" (when "Product Requirements" applies), "API Endpoints" (when "Integration Points" applies), "Rollout Plan" (when "Ship Plan" applies) |
| migration | "User Stories" (when "Migration Requirements" applies), "API Endpoints" (when "Integration Boundaries" applies), "Rollout Plan" (when "Cutover Plan" applies), "Components" (when "Systems" applies) |

Scan each generated spec file (requirements.md/bugfix.md/refactor.md, design.md, tasks.md) for prohibited terms. If any are found, replace with the vertical-specific term. Record the result in implementation.md Phase 1 Context Summary as `- Vocabulary check: [pass / N term(s) replaced]`.

This check does NOT apply when:

- The vertical is `backend`, `fullstack`, or `frontend` (default vocabulary is correct)
- A custom template is used (custom templates define their own structure)

### Applying Adaptation Rules

1. Check the detected vertical
2. Apply the relevant rules: skip listed sections, rename headers, use domain vocabulary
3. If a section is listed as "skip" but IS relevant to the specific request, keep it — use judgment
4. Adaptation rules are NOT applied when using a custom template file (the custom template defines its own structure)
