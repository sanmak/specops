# Infrastructure: Kubernetes Autoscaling & Monitoring

## Overview
Set up comprehensive Kubernetes autoscaling and monitoring for API microservices running on AWS EKS. This includes Horizontal Pod Autoscaling (HPA) with custom metrics, Vertical Pod Autoscaling (VPA) in recommendation mode, PodDisruptionBudgets for safe rollouts, Prometheus-based monitoring with Grafana dashboards, and cost-aware scaling boundaries. The infrastructure is provisioned with Terraform and deployed with Helm, integrating into the existing kube-prometheus-stack for observability.

## Infrastructure Requirements

### Requirement 1: Horizontal Pod Autoscaling
**As an** SRE
**I need** API services to scale horizontally based on CPU, memory, and custom metrics (requests per second)
**So that** the platform maintains target latency during traffic spikes without manual intervention

**Acceptance Criteria:**
- [ ] HPA resources created for `api-gateway` and `user-service` deployments (autoscaling/v2)
- [ ] CPU target utilization set to 70%, memory target utilization set to 80%
- [ ] Custom metric `http_requests_per_second` sourced from Prometheus Adapter
- [ ] Minimum replicas set to 3, maximum replicas set to 15 per service
- [ ] Scale-up completes within 2 minutes of threshold breach
- [ ] Scale-down stabilization window set to 300 seconds to prevent flapping
- [ ] HPA status shows `AbleToScale: True` and `ScalingActive: True` after deployment
- [ ] HPA behavior policies limit scale-up to 4 pods per 60 seconds

### Requirement 2: Vertical Pod Autoscaling
**As an** operator
**I need** resource requests and limits to be automatically right-sized based on actual usage
**So that** pods are neither over-provisioned (wasting cost) nor under-provisioned (risking OOMKills)

**Acceptance Criteria:**
- [ ] VPA resources created for `api-gateway` and `user-service` deployments
- [ ] VPA updateMode set to `Off` (recommendation-only, no automatic restarts)
- [ ] VPA recommendations logged and visible via `kubectl describe vpa`
- [ ] Recommendations reviewed weekly and applied during maintenance windows
- [ ] VPA does not conflict with HPA resource-based scaling targets
- [ ] Lower bound, upper bound, and uncapped target visible in VPA status

### Requirement 3: Pod Disruption Budgets
**As an** SRE
**I need** disruption budgets enforced during rolling updates, node drains, and cluster upgrades
**So that** API services maintain availability during maintenance operations

**Acceptance Criteria:**
- [ ] PDB created for each API service with `maxUnavailable: 1`
- [ ] PDB prevents node drain from terminating more than 1 pod simultaneously
- [ ] Rolling updates respect PDB constraints (verified with `kubectl rollout status`)
- [ ] PDB status shows `disruptionsAllowed >= 1` under normal conditions
- [ ] Cluster Autoscaler respects PDB when scaling down node groups

### Requirement 4: Monitoring & Alerting
**As an** operator
**I need** Prometheus metrics collection, Grafana dashboards, and PagerDuty alerting for all autoscaling components
**So that** I can observe scaling behavior, detect failures, and respond to incidents within SLO targets

**Acceptance Criteria:**
- [ ] ServiceMonitor resources created for API services (scrape interval 15s)
- [ ] Grafana dashboard shows CPU/memory utilization, replica count, RPS, and P95 latency per service
- [ ] PrometheusRule fires alert when HPA is at max replicas for >5 minutes
- [ ] PrometheusRule fires alert when P95 latency exceeds 500ms for >2 minutes
- [ ] PrometheusRule fires alert when pod restarts exceed 3 in 10 minutes
- [ ] Alerts route to PagerDuty for P1 (scaling failure) and email/Slack for P2 (high utilization)
- [ ] Dashboard accessible at `https://grafana.internal/d/k8s-autoscaling`

### Requirement 5: Cost Optimization
**As an** infrastructure manager
**I need** scaling boundaries and cost visibility to prevent runaway infrastructure spend
**So that** autoscaling operates within approved budget while meeting performance targets

**Acceptance Criteria:**
- [ ] Maximum replicas capped per service (15 for api-gateway, 10 for user-service)
- [ ] EKS managed node group autoscaler configured with min 3, max 20 nodes
- [ ] Node group uses mixed instance types (m5.xlarge, m5a.xlarge) for cost optimization
- [ ] AWS Cost Explorer tags applied to all autoscaling-related resources
- [ ] CloudWatch alarm fires when estimated monthly cost exceeds $5,000 threshold
- [ ] VPA recommendations reviewed monthly for right-sizing savings

## Resource Inventory

| Resource | Type | Provider | Status |
|----------|------|----------|--------|
| HPA (api-gateway) | autoscaling/v2 HorizontalPodAutoscaler | Kubernetes | New |
| HPA (user-service) | autoscaling/v2 HorizontalPodAutoscaler | Kubernetes | New |
| VPA (api-gateway) | autoscaling.k8s.io/v1 VerticalPodAutoscaler | Kubernetes | New |
| VPA (user-service) | autoscaling.k8s.io/v1 VerticalPodAutoscaler | Kubernetes | New |
| PDB (api-gateway) | policy/v1 PodDisruptionBudget | Kubernetes | New |
| PDB (user-service) | policy/v1 PodDisruptionBudget | Kubernetes | New |
| ServiceMonitor (api-services) | monitoring.coreos.com/v1 ServiceMonitor | Prometheus Operator | New |
| PrometheusRule (autoscaling-alerts) | monitoring.coreos.com/v1 PrometheusRule | Prometheus Operator | New |
| Grafana Dashboard (k8s-autoscaling) | ConfigMap (JSON) | Grafana | New |
| Prometheus Adapter | Helm release | Prometheus Adapter | New |
| Cluster Autoscaler | Helm release | Kubernetes Autoscaler | New |
| EKS Node Group | aws_eks_node_group | Terraform (AWS) | Modify |
| Terraform S3 Backend | aws_s3_bucket / aws_dynamodb_table | Terraform (AWS) | Existing |

## Operational Requirements

### Availability
- API services maintain 99.95% uptime during scaling events
- Zero downtime during horizontal scale-up and scale-down
- Zero dropped requests during node group scaling

### Recovery
- RTO: 5 minutes — autoscaling resumes after control plane recovery
- RPO: 0 — no stateful data in autoscaling components; Prometheus retains 15 days of metrics

### Monitoring
- Prometheus scrapes all API service metrics at 15-second intervals
- Grafana dashboards refresh every 30 seconds
- PagerDuty alerts fire within 60 seconds of threshold breach via Alertmanager

### Compliance
- All Terraform state changes logged in S3 versioned bucket
- IAM roles follow least-privilege via IRSA (IAM Roles for Service Accounts)
- Audit trail for scaling events retained 90 days (SOC 2)
- No secrets stored in Helm values or ConfigMaps (use AWS Secrets Manager)

## Constraints & Assumptions

### Constraints
- EKS cluster version 1.28 or later (required for autoscaling/v2 stable API)
- Terraform v1.5+ with AWS provider v5.x
- Helm v3.12+ for OCI registry support
- Must not disrupt existing workloads during rollout
- AWS service quotas must accommodate max node group size (20 nodes)

### Assumptions
- Prometheus Operator (kube-prometheus-stack) is already deployed in the `monitoring` namespace
- EKS cluster OIDC provider is configured for IRSA
- VPC and subnets have capacity for additional nodes
- API services expose `/metrics` endpoint in Prometheus format
- PagerDuty service and integration key are provisioned

## Team Conventions
- Use Terraform modules for reusable infrastructure components
- Pin Helm chart versions in `Chart.yaml` dependencies
- Store all Kubernetes manifests as Helm templates (no raw `kubectl apply`)
- Tag all AWS resources with `team`, `environment`, `managed-by` labels
- Use `kustomize` overlays for environment-specific values only if Helm values are insufficient
- Document all Terraform variables with descriptions and validation rules
- Require `terraform plan` output in PR reviews

## Success Metrics
- HPA scale-up completes in under 120 seconds from threshold breach
- Zero downtime during all scaling events (measured by synthetic probes)
- 20% infrastructure cost reduction from VPA right-sizing recommendations within 30 days
- All P1 alerts fire correctly during chaos testing (100% true-positive rate)
- Grafana dashboards load within 3 seconds with 7-day time range
- Mean time to acknowledge scaling incidents < 5 minutes via PagerDuty

## Out of Scope (Future Considerations)
- Multi-region EKS cluster federation
- Cluster migration from self-managed to EKS
- KEDA (Kubernetes Event-Driven Autoscaling) for queue-based scaling
- Service mesh integration (Istio/Linkerd) for traffic-aware scaling
- Spot instance integration for non-critical workloads
- Custom metrics beyond RPS (e.g., queue depth, error rate)
