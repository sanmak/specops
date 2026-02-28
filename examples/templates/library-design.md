# Library Design: {{title}}

## Architecture Overview
High-level description of the library architecture.

## Technical Decisions

### Decision 1: [Title]
**Context:** Why this decision is needed
**Options Considered:**
1. Option A - Pros/Cons
2. Option B - Pros/Cons

**Decision:** Option [selected]
**Rationale:** Why this option was chosen

## Module Design

### Module 1: [Name]
**Responsibility:** What this module does
**Exports:** Public functions and types
**Dependencies:** What it depends on

### Module 2: [Name]
...

## Public API Surface

### Exports
```typescript
// Main entry point
export { functionA, functionB } from './moduleA'
export { functionC } from './moduleB'

// Types
export type { TypeA, TypeB } from './types'
```

### Function Signatures
- `functionA(param: Type): ReturnType` - Description
- `functionB(param: Type): ReturnType` - Description

## Usage Examples

### Example 1: [Common Use Case]
```typescript
import { functionA } from '{{package-name}}'

const result = functionA(input)
```

### Example 2: [Advanced Use Case]
```typescript
import { functionB, functionC } from '{{package-name}}'

const intermediate = functionB(input)
const result = functionC(intermediate, options)
```

## Testing Strategy
- Unit tests: [scope and framework]
- Integration tests: [scope]
- Browser tests: [if applicable]
- Bundle size tests: [CI size check]

## Release Plan
- Versioning: Semantic versioning (semver)
- Changelog: [generation approach]
- Publishing: [npm registry, CI/CD]
- Migration guides: [for breaking changes]

## Risks & Mitigations
- **Risk 1:** Description -> **Mitigation:** Strategy
- **Risk 2:** Description -> **Mitigation:** Strategy
