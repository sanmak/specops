# Infrastructure Design: {{title}}

## Architecture Overview
High-level description of the infrastructure solution.

## Technical Decisions

### Decision 1: [Title]
**Context:** Why this decision is needed
**Options Considered:**
1. Option A - Pros/Cons
2. Option B - Pros/Cons

**Decision:** Option [selected]
**Rationale:** Why this option was chosen

## Infrastructure Topology

### Resource 1: [Name]
**Type:** [e.g., AWS ECS Service, K8s Deployment, Terraform module]
**Configuration:** Key settings and parameters
**Dependencies:** What it depends on

### Resource 2: [Name]
...

## Provisioning/Deployment Flow

```
Trigger -> Validate -> Plan -> Apply -> Verify
```

## State & Configuration Management
- State backend: [e.g., S3, Terraform Cloud, etcd]
- Configuration source: [e.g., environment variables, SSM Parameter Store, ConfigMaps]
- Secrets management: [e.g., Vault, AWS Secrets Manager, K8s Secrets]

## Resource Definitions
- [List of resources to create/modify with key attributes]

## Security & Compliance
- IAM/RBAC: [approach]
- Network policies: [approach]
- Encryption: [at-rest and in-transit]
- Compliance: [relevant frameworks]

## Scalability & Reliability
- Auto-scaling: [strategy]
- High availability: [approach]
- Disaster recovery: [approach]

## Deployment Strategy
- Method: [blue-green / canary / rolling]
- Validation: [smoke tests, health checks]
- Rollback: [procedure]

## Risks & Mitigations
- **Risk 1:** Description -> **Mitigation:** Strategy
- **Risk 2:** Description -> **Mitigation:** Strategy
