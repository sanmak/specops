# Infrastructure Design: Kubernetes Autoscaling & Monitoring

## Architecture Overview

The autoscaling and monitoring infrastructure spans AWS EKS managed node groups and Kubernetes-native autoscaling controllers. Terraform provisions the underlying AWS resources (EKS node groups, IAM roles, S3 backend), while Helm deploys Kubernetes components (Prometheus Adapter, Cluster Autoscaler, HPA/VPA/PDB manifests, Grafana dashboards).

**Key architectural layers:**

- **Compute Layer**: EKS managed node groups with Cluster Autoscaler for node-level scaling
- **Pod Autoscaling Layer**: HPA (horizontal) driven by CPU, memory, and custom RPS metric; VPA (vertical) in recommendation mode for right-sizing
- **Resilience Layer**: PodDisruptionBudgets to protect availability during maintenance
- **Observability Layer**: Prometheus Operator (kube-prometheus-stack) for metrics collection, Prometheus Adapter for custom metrics API, Grafana for dashboards, Alertmanager + PagerDuty for incident routing
- **IaC Layer**: Terraform for AWS resources, Helm for Kubernetes resources, S3 + DynamoDB for Terraform state

## Technical Decisions

### Decision 1: HPA Metric Source — metrics-server vs Prometheus Adapter
**Context:** HPA needs CPU/memory metrics (available from metrics-server) and custom metrics (requests per second from application).

**Options Considered:**
1. **metrics-server only**
   - Pros: Already installed on EKS, no extra components, simple setup
   - Cons: Only supports CPU and memory; cannot use custom application metrics like RPS
2. **Prometheus Adapter**
   - Pros: Exposes any Prometheus metric as a Kubernetes custom metric; HPA can scale on RPS, error rate, queue depth
   - Cons: Additional component to deploy and maintain; requires Prometheus to be running
3. **KEDA**
   - Pros: Event-driven, supports many scalers (queues, databases, Prometheus)
   - Cons: Additional CRDs, operator complexity, team unfamiliar with KEDA

**Decision:** Prometheus Adapter
**Rationale:**
- Custom metrics (RPS) are a core requirement for traffic-aware scaling
- Prometheus is already deployed; Adapter leverages existing investment
- Simpler than KEDA for the current use case (HTTP-based services)
- Team can extend to additional custom metrics later without new tooling

### Decision 2: IaC Approach — Terraform + Helm vs Pulumi vs ArgoCD
**Context:** Need to provision AWS infrastructure and deploy Kubernetes resources reproducibly across environments.

**Options Considered:**
1. **Terraform + Helm**
   - Pros: Team already uses Terraform for AWS; Helm is standard for K8s packaging; clear separation of AWS vs K8s
   - Cons: Two tools to maintain; Helm templating can be complex
2. **Pulumi**
   - Pros: Single language (TypeScript) for both AWS and K8s; strong typing
   - Cons: Team has no Pulumi experience; migration cost from existing Terraform
3. **ArgoCD (GitOps)**
   - Pros: Declarative, automatic sync, audit trail
   - Cons: Does not manage AWS resources; still needs Terraform for EKS node groups

**Decision:** Terraform + Helm
**Rationale:**
- Team has 2+ years of Terraform experience; no onboarding cost
- Helm charts available for all required components (Prometheus Adapter, Cluster Autoscaler)
- Clear responsibility boundary: Terraform owns AWS, Helm owns Kubernetes
- ArgoCD can be added later as a deployment layer without changing IaC

### Decision 3: Monitoring Stack — Prometheus + Grafana vs Datadog vs CloudWatch Container Insights
**Context:** Need metrics collection, dashboards, and alerting for autoscaling components.

**Options Considered:**
1. **Prometheus Operator + Grafana (kube-prometheus-stack)**
   - Pros: Already deployed in cluster; no additional licensing cost; native Kubernetes integration; ServiceMonitor CRDs
   - Cons: Self-managed storage; requires tuning for retention and performance
2. **Datadog**
   - Pros: Managed SaaS; rich K8s integration; built-in autoscaling dashboards
   - Cons: Per-host licensing ($23/host/month); data egress; vendor lock-in
3. **CloudWatch Container Insights**
   - Pros: Native AWS integration; no extra agents for EKS
   - Cons: Limited custom metrics; dashboarding inferior to Grafana; higher query costs at scale

**Decision:** Prometheus Operator + Grafana (existing kube-prometheus-stack)
**Rationale:**
- Already deployed and operational; zero additional infrastructure cost
- ServiceMonitor CRDs provide declarative metric scraping
- Grafana dashboards are version-controlled as JSON ConfigMaps
- Alertmanager natively integrates with PagerDuty
- Prometheus Adapter requires Prometheus as a prerequisite anyway

## Infrastructure Topology

### Component 1: Horizontal Pod Autoscaler Configuration

HPA for the `api-gateway` deployment, scaling on CPU utilization, memory utilization, and custom RPS metric from Prometheus Adapter.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: api
  labels:
    app: api-gateway
    managed-by: specops
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 3
  maxReplicas: 15
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Pods
          value: 4
          periodSeconds: 60
        - type: Percent
          value: 100
          periodSeconds: 60
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Pods
          value: 1
          periodSeconds: 120
      selectPolicy: Min
```

The `user-service` HPA follows the same structure with `maxReplicas: 10` and `averageValue: "500"` for RPS.

### Component 2: Vertical Pod Autoscaler Configuration

VPA in `Off` mode (recommendation-only). The VPA controller observes actual resource consumption and produces recommendations without modifying pod resource requests.

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: api-gateway-vpa
  namespace: api
  labels:
    app: api-gateway
    managed-by: specops
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  updatePolicy:
    updateMode: "Off"
  resourcePolicy:
    containerPolicies:
      - containerName: api-gateway
        minAllowed:
          cpu: "100m"
          memory: "128Mi"
        maxAllowed:
          cpu: "4"
          memory: "4Gi"
        controlledResources:
          - cpu
          - memory
```

### Component 3: PodDisruptionBudget

PDB ensures at least `N-1` pods remain available during voluntary disruptions (rolling updates, node drains, cluster upgrades).

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-gateway-pdb
  namespace: api
  labels:
    app: api-gateway
    managed-by: specops
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: api-gateway
```

### Component 4: EKS Node Group with Cluster Autoscaler

Terraform configuration for the EKS managed node group with autoscaling boundaries.

```hcl
module "eks_node_group" {
  source  = "terraform-aws-modules/eks/aws//modules/eks-managed-node-group"
  version = "~> 19.0"

  name            = "api-workloads"
  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version
  subnet_ids      = var.private_subnet_ids

  min_size     = 3
  max_size     = 20
  desired_size = 5

  instance_types = ["m5.xlarge", "m5a.xlarge"]
  capacity_type  = "ON_DEMAND"

  labels = {
    role        = "api-workloads"
    environment = var.environment
    team        = "platform"
    managed-by  = "terraform"
  }

  tags = {
    "k8s.io/cluster-autoscaler/enabled"             = "true"
    "k8s.io/cluster-autoscaler/${var.cluster_name}"  = "owned"
    "CostCenter"                                      = "platform-infra"
  }

  block_device_mappings = {
    xvda = {
      device_name = "/dev/xvda"
      ebs = {
        volume_size           = 100
        volume_type           = "gp3"
        encrypted             = true
        delete_on_termination = true
      }
    }
  }

  iam_role_additional_policies = {
    CloudWatchAgentServerPolicy = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
  }
}
```

### Component 5: Prometheus Adapter Configuration

Helm values for the Prometheus Adapter, mapping the `http_requests_total` counter to a `http_requests_per_second` rate metric exposed via the custom metrics API.

```yaml
# helm-values/prometheus-adapter.yaml
prometheus:
  url: http://prometheus-operated.monitoring.svc
  port: 9090

rules:
  custom:
    - seriesQuery: 'http_requests_total{namespace!="",pod!=""}'
      resources:
        overrides:
          namespace:
            resource: namespace
          pod:
            resource: pod
      name:
        matches: "^(.*)_total$"
        as: "${1}_per_second"
      metricsQuery: 'sum(rate(<<.Series>>{<<.LabelMatchers>>}[2m])) by (<<.GroupBy>>)'

  resource:
    cpu:
      containerQuery: 'sum(rate(container_cpu_usage_seconds_total{<<.LabelMatchers>>}[3m])) by (<<.GroupBy>>)'
      nodeQuery: 'sum(rate(container_cpu_usage_seconds_total{<<.LabelMatchers>>, id="/"}[3m])) by (<<.GroupBy>>)'
      resources:
        overrides:
          namespace:
            resource: namespace
          node:
            resource: node
          pod:
            resource: pod
      containerLabel: container
    memory:
      containerQuery: 'sum(container_memory_working_set_bytes{<<.LabelMatchers>>}) by (<<.GroupBy>>)'
      nodeQuery: 'sum(container_memory_working_set_bytes{<<.LabelMatchers>>,id="/"}) by (<<.GroupBy>>)'
      resources:
        overrides:
          namespace:
            resource: namespace
          node:
            resource: node
          pod:
            resource: pod
      containerLabel: container
```

### Component 6: Prometheus Alerting Rules

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: autoscaling-alerts
  namespace: monitoring
  labels:
    release: kube-prometheus-stack
spec:
  groups:
    - name: hpa-alerts
      rules:
        - alert: HPAAtMaxReplicas
          expr: |
            kube_horizontalpodautoscaler_status_current_replicas
              == kube_horizontalpodautoscaler_spec_max_replicas
          for: 5m
          labels:
            severity: warning
            team: platform
          annotations:
            summary: "HPA {{ $labels.horizontalpodautoscaler }} is at max replicas"
            description: "HPA {{ $labels.horizontalpodautoscaler }} in namespace {{ $labels.namespace }} has been at max replicas ({{ $value }}) for more than 5 minutes."
            runbook_url: "https://wiki.internal/runbooks/hpa-max-replicas"

        - alert: HPAScalingFailure
          expr: |
            kube_horizontalpodautoscaler_status_condition{condition="ScalingActive",status="false"} == 1
          for: 5m
          labels:
            severity: critical
            team: platform
          annotations:
            summary: "HPA {{ $labels.horizontalpodautoscaler }} cannot scale"
            description: "HPA {{ $labels.horizontalpodautoscaler }} in namespace {{ $labels.namespace }} has ScalingActive=false for more than 5 minutes."

    - name: latency-alerts
      rules:
        - alert: HighP95Latency
          expr: |
            histogram_quantile(0.95,
              sum(rate(http_request_duration_seconds_bucket{namespace="api"}[5m])) by (le, service)
            ) > 0.5
          for: 2m
          labels:
            severity: critical
            team: platform
          annotations:
            summary: "P95 latency for {{ $labels.service }} exceeds 500ms"
            description: "Service {{ $labels.service }} P95 latency is {{ $value }}s, exceeding 500ms SLO for more than 2 minutes."

    - name: pod-health-alerts
      rules:
        - alert: HighPodRestartRate
          expr: |
            increase(kube_pod_container_status_restarts_total{namespace="api"}[10m]) > 3
          labels:
            severity: warning
            team: platform
          annotations:
            summary: "Pod {{ $labels.pod }} restarting frequently"
            description: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} has restarted {{ $value }} times in the last 10 minutes."

        - alert: ClusterAutoscalerUnschedulable
          expr: |
            cluster_autoscaler_unschedulable_pods_count > 0
          for: 5m
          labels:
            severity: critical
            team: platform
          annotations:
            summary: "Cluster Autoscaler cannot schedule {{ $value }} pods"
            description: "There are {{ $value }} unschedulable pods for more than 5 minutes. Check node group capacity and AWS quotas."
```

## Provisioning/Deployment Flow

### Flow 1: Initial Infrastructure Setup
```
Operator -> Terraform: terraform init (S3 backend, DynamoDB lock)
Terraform -> AWS: Create/update EKS managed node group
AWS -> Terraform: Node group ARN, ASG name
Terraform -> State: Store in S3 with DynamoDB lock
Operator -> Terraform: terraform plan (review changes)
Terraform -> Operator: Plan output (resources to create/modify)
Operator -> Terraform: terraform apply -auto-approve=false
Terraform -> AWS: Apply EKS node group changes
AWS -> EKS: Nodes join cluster, Ready status
Operator -> Helm: helm upgrade --install prometheus-adapter prometheus-community/prometheus-adapter -f values.yaml
Helm -> K8s API: Create Prometheus Adapter deployment, service, APIService
K8s API -> Helm: Release deployed
Operator -> Helm: helm upgrade --install cluster-autoscaler autoscaler/cluster-autoscaler -f values.yaml
Helm -> K8s API: Create Cluster Autoscaler deployment, RBAC, ServiceAccount
K8s API -> Helm: Release deployed
Operator -> kubectl: Apply HPA, VPA, PDB manifests (via Helm subchart)
kubectl -> K8s API: Create autoscaling resources
K8s API -> Operator: Resources created
Operator -> Verify: kubectl get hpa,vpa,pdb -n api
Verify -> Operator: All resources running
```

### Flow 2: Horizontal Scaling Event
```
Traffic Spike -> API Pods: Increased request rate
API Pods -> Prometheus: Scrape /metrics endpoint (http_requests_total counter increases)
Prometheus -> Prometheus Adapter: Rate query via custom metrics API
HPA Controller -> Prometheus Adapter: GET /apis/custom.metrics.k8s.io/v1beta1/namespaces/api/pods/*/http_requests_per_second
Prometheus Adapter -> HPA Controller: Current average RPS per pod
HPA Controller -> HPA Controller: Compare current (1500 RPS/pod) vs target (1000 RPS/pod)
HPA Controller -> HPA Controller: Calculate desired replicas = ceil(current_replicas * 1500/1000)
HPA Controller -> Deployment: Scale replicas from 5 to 8 (capped by scaleUp policy: +4 max per 60s)
Deployment -> Scheduler: Schedule 3 new pods
Scheduler -> Nodes: Pods scheduled on existing nodes (if capacity available)
Alt: No node capacity
  Scheduler -> Scheduler: Pods remain Pending
  Cluster Autoscaler -> Scheduler: Detect unschedulable pods
  Cluster Autoscaler -> AWS ASG: Increase desired capacity
  AWS ASG -> EC2: Launch new m5.xlarge instances
  EC2 -> EKS: Nodes join cluster (2-3 min)
  Scheduler -> New Nodes: Schedule pending pods
End
Deployment -> Service: New pods receive traffic via Endpoints
Service -> Traffic: Load balanced across all healthy pods
HPA Controller -> Prometheus: Continue monitoring (scale-down after 300s stabilization)
```

### Flow 3: Alert and Incident Flow
```
Prometheus -> PrometheusRule: Evaluate alerting rules every 15s
PrometheusRule -> Prometheus: HPAAtMaxReplicas firing for >5 minutes
Prometheus -> Alertmanager: Send alert with labels (severity: critical, team: platform)
Alertmanager -> Alertmanager: Match routing rules by severity
Alt: severity=critical
  Alertmanager -> PagerDuty: POST /v2/enqueue (event with routing key)
  PagerDuty -> On-Call SRE: Page via phone/SMS/push notification
  On-Call SRE -> Grafana: Open autoscaling dashboard, assess situation
  On-Call SRE -> kubectl: Investigate (describe hpa, top pods, get events)
  On-Call SRE -> Resolution: Increase maxReplicas / add node capacity / investigate root cause
  On-Call SRE -> PagerDuty: Acknowledge and resolve incident
Else: severity=warning
  Alertmanager -> Slack: Post to #platform-alerts channel
  Alertmanager -> Email: Send to platform-team@company.com
End
Alertmanager -> Alertmanager: Group, deduplicate, silence repeated alerts
```

## State & Configuration Management

### Terraform State
- **Backend**: S3 bucket (`company-terraform-state`) with versioning enabled
- **Locking**: DynamoDB table (`terraform-locks`) for state locking
- **Encryption**: AES-256 server-side encryption on S3
- **Structure**: `environments/{env}/k8s-autoscaling/terraform.tfstate`

```hcl
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "environments/prod/k8s-autoscaling/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

### Helm Values (Per Environment)

Values are stored in the Git repository under `helm-values/` with environment-specific overrides.

```
helm-values/
├── base/
│   ├── prometheus-adapter.yaml
│   ├── cluster-autoscaler.yaml
│   └── autoscaling-resources.yaml
├── dev/
│   ├── prometheus-adapter.yaml     # minReplicas: 1, maxReplicas: 3
│   └── cluster-autoscaler.yaml     # maxNodes: 5
├── staging/
│   ├── prometheus-adapter.yaml     # minReplicas: 2, maxReplicas: 8
│   └── cluster-autoscaler.yaml     # maxNodes: 10
└── prod/
    ├── prometheus-adapter.yaml     # minReplicas: 3, maxReplicas: 15
    └── cluster-autoscaler.yaml     # maxNodes: 20
```

### Secrets Management
- **AWS Secrets Manager**: PagerDuty integration key, Grafana admin password
- **IRSA (IAM Roles for Service Accounts)**: Cluster Autoscaler ServiceAccount bound to IAM role with `autoscaling:*` and `ec2:Describe*` permissions
- **No secrets in Helm values**: Secrets referenced via `ExternalSecret` CRD or environment variables from AWS Secrets Manager

```yaml
# Cluster Autoscaler IRSA
apiVersion: v1
kind: ServiceAccount
metadata:
  name: cluster-autoscaler
  namespace: kube-system
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/cluster-autoscaler-role
```

### ConfigMaps
- **Prometheus alerting rules**: Stored as `PrometheusRule` CRD (managed by Prometheus Operator)
- **Grafana dashboards**: Stored as `ConfigMap` with `grafana_dashboard: "1"` label (auto-discovered by Grafana sidecar)
- **Prometheus Adapter rules**: Stored in Helm values, deployed as ConfigMap by the Adapter chart

## Resource Definitions

### Terraform Resources

| Resource | Type | Key Attributes |
|----------|------|----------------|
| EKS Node Group | `aws_eks_node_group` | min_size=3, max_size=20, instance_types=[m5.xlarge, m5a.xlarge] |
| IAM Role (Cluster Autoscaler) | `aws_iam_role` | IRSA trust policy, autoscaling:* permissions |
| IAM Policy (Cluster Autoscaler) | `aws_iam_policy` | ec2:Describe*, autoscaling:SetDesiredCapacity, autoscaling:TerminateInstanceInAutoScalingGroup |
| IAM Role (Prometheus) | `aws_iam_role` | IRSA trust policy, CloudWatch read permissions |
| CloudWatch Alarm (Cost) | `aws_cloudwatch_metric_alarm` | EstimatedCharges > $5000, SNS notification |
| S3 Backend | `aws_s3_bucket` | Versioning enabled, AES-256 encryption |
| DynamoDB Lock | `aws_dynamodb_table` | LockID partition key, PAY_PER_REQUEST |

### Kubernetes Resources

| Resource | API Group | Namespace | Key Attributes |
|----------|-----------|-----------|----------------|
| HPA (api-gateway) | autoscaling/v2 | api | CPU 70%, memory 80%, RPS 1000, min 3, max 15 |
| HPA (user-service) | autoscaling/v2 | api | CPU 70%, memory 80%, RPS 500, min 3, max 10 |
| VPA (api-gateway) | autoscaling.k8s.io/v1 | api | updateMode: Off, cpu 100m-4, memory 128Mi-4Gi |
| VPA (user-service) | autoscaling.k8s.io/v1 | api | updateMode: Off, cpu 100m-2, memory 128Mi-2Gi |
| PDB (api-gateway) | policy/v1 | api | maxUnavailable: 1 |
| PDB (user-service) | policy/v1 | api | maxUnavailable: 1 |
| ServiceMonitor | monitoring.coreos.com/v1 | monitoring | selector: app in (api-gateway, user-service), interval: 15s |
| PrometheusRule | monitoring.coreos.com/v1 | monitoring | 5 alert rules (HPA, latency, restarts, CA) |
| Grafana Dashboard | v1 ConfigMap | monitoring | JSON dashboard, label: grafana_dashboard=1 |
| Prometheus Adapter | Helm release | monitoring | Custom metrics rules for RPS |
| Cluster Autoscaler | Helm release | kube-system | IRSA, scan-interval=10s, balance-similar-node-groups |

## Security & Compliance

### RBAC
- Cluster Autoscaler ServiceAccount: ClusterRole with `nodes`, `pods`, `replicasets`, `deployments` read; `nodes` scale
- Prometheus Adapter ServiceAccount: ClusterRole with `pods`, `services`, `endpoints` read; custom metrics API delegation
- HPA controller (built-in): Uses `system:controller:horizontal-pod-autoscaler` ClusterRole
- Grafana ServiceAccount: Read-only access to ConfigMaps in `monitoring` namespace
- Operator access: `platform-sre` ClusterRole with read/write on HPA, VPA, PDB resources

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-prometheus-scrape
  namespace: api
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/part-of: api-services
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: monitoring
          podSelector:
            matchLabels:
              app.kubernetes.io/name: prometheus
      ports:
        - protocol: TCP
          port: 8080
```

### Encryption
- EBS volumes encrypted with AWS-managed KMS key (gp3)
- Terraform state encrypted at rest (S3 SSE-AES256)
- Prometheus TSDB stored on encrypted EBS volumes
- All in-cluster communication uses mTLS where service mesh is adopted (future)

### Audit Logging
- EKS control plane audit logs sent to CloudWatch Logs (90-day retention)
- Terraform plan/apply outputs stored in CI/CD pipeline artifacts
- All HPA scaling events captured via Kubernetes events (visible in `kubectl get events`)
- Alertmanager notification history retained for 120 hours

## Performance Considerations

### HPA Evaluation
- Default HPA sync period: 15 seconds (configurable via `--horizontal-pod-autoscaler-sync-period`)
- Tolerance: 10% (default) — HPA does not scale if current/desired ratio is within 0.9-1.1
- Scale-up policy: max 4 pods per 60 seconds (prevents pod avalanche)
- Scale-down stabilization: 300 seconds (prevents flapping during traffic oscillation)

### Prometheus Adapter
- Query cache: 30-second TTL to reduce Prometheus load
- Rate window: 2 minutes (`rate(...[2m])`) balances responsiveness with noise filtering
- Series query limited to `namespace="api"` to reduce cardinality

### Cluster Autoscaler
- Scan interval: 10 seconds (default)
- Scale-down delay after add: 10 minutes (prevent premature scale-down of new nodes)
- Scale-down unneeded time: 10 minutes
- Max node provision time: 15 minutes (EKS node join typically 2-3 minutes)
- Balance similar node groups: enabled (distributes across AZs)

### Prometheus Storage
- Retention: 15 days local TSDB
- Scrape interval: 15 seconds for API services, 30 seconds for infrastructure components
- Estimated cardinality: ~50,000 active series for 20 pods across 2 services
- Memory per 1000 series: ~2MB (total ~100MB for Prometheus ingestion buffer)

## Deployment Strategy

### Rollout Stages
Deployment follows a staged approach across environments with validation gates between stages.

**Stage 1: Dev Environment**
- Apply Terraform changes to dev EKS cluster
- Deploy Helm charts with dev values
- Validate all resources are running
- Run synthetic load test (low volume)
- Gate: All resources healthy, HPA responds to synthetic load

**Stage 2: Staging Environment**
- Apply Terraform changes to staging EKS cluster
- Deploy Helm charts with staging values
- Run realistic load test simulating production traffic patterns
- Validate alerting pipeline (trigger test alert to PagerDuty)
- Gate: HPA scales correctly, alerts fire, no false positives, PDB respected during rolling update

**Stage 3: Production Environment**
- Apply Terraform changes to prod EKS cluster during maintenance window
- Deploy Helm charts with prod values
- Monitor for 30 minutes post-deployment
- Validate Grafana dashboards show correct data
- Gate: Zero errors in scaling events, dashboards functional, alerts armed

### Validation Between Stages
```bash
# Verify HPA is functional
kubectl get hpa -n api -o wide
kubectl describe hpa api-gateway-hpa -n api

# Verify custom metrics are available
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1/namespaces/api/pods/*/http_requests_per_second" | jq .

# Verify VPA recommendations
kubectl describe vpa api-gateway-vpa -n api

# Verify PDB status
kubectl get pdb -n api

# Verify Cluster Autoscaler logs
kubectl logs -l app.kubernetes.io/name=cluster-autoscaler -n kube-system --tail=50

# Verify Prometheus targets
kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.namespace=="api")'

# Verify alerting rules loaded
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[] | select(.name | startswith("hpa-"))'
```

### Rollback Procedures

**Helm Rollback** (Kubernetes resources):
```bash
# List release history
helm history prometheus-adapter -n monitoring
helm history cluster-autoscaler -n kube-system

# Rollback to previous revision
helm rollback prometheus-adapter <revision> -n monitoring
helm rollback cluster-autoscaler <revision> -n kube-system

# Delete HPA/VPA/PDB if needed
kubectl delete hpa api-gateway-hpa -n api
kubectl delete vpa api-gateway-vpa -n api
kubectl delete pdb api-gateway-pdb -n api
```

**Terraform Rollback** (AWS resources):
```bash
# Review what will be destroyed
terraform plan -destroy -target=module.eks_node_group

# Revert to previous Terraform state
git revert <commit-sha>
terraform plan
terraform apply
```

## Risks & Mitigations

### Risk 1: HPA Flapping (Rapid Scale-Up/Down Cycles)
**Impact:** Pod churn, connection drops, increased latency during frequent scaling
**Probability:** Medium
**Mitigation:**
- Scale-down stabilization window set to 300 seconds
- Scale-up policy limited to 4 pods per 60 seconds
- HPA tolerance at 10% (default) prevents micro-adjustments
- Monitor `kube_horizontalpodautoscaler_status_current_replicas` for oscillation patterns
- Alert if replica count changes more than 5 times in 10 minutes

### Risk 2: Cluster Autoscaler Node Provisioning Lag
**Impact:** Pods remain Pending for 2-5 minutes while new EC2 instances launch and join the cluster
**Probability:** Medium
**Mitigation:**
- Maintain headroom by setting `desired_size` slightly above minimum
- Use `--expander=least-waste` to optimize node selection
- Pre-warm capacity with priority-based scheduling (low-priority placeholder pods)
- Monitor `cluster_autoscaler_unschedulable_pods_count` with alert at >0 for 5 minutes
- Consider AWS Karpenter as future replacement for faster provisioning

### Risk 3: Prometheus Storage Exhaustion
**Impact:** Metrics loss, dashboard gaps, alerting blackout
**Probability:** Low
**Mitigation:**
- Configure 15-day retention with `--storage.tsdb.retention.time=15d`
- Set storage size limit with `--storage.tsdb.retention.size=50GB`
- Monitor `prometheus_tsdb_storage_blocks_bytes` and alert at 80% capacity
- Use persistent volume with gp3 and auto-expansion enabled
- Long-term storage via Thanos or Grafana Mimir (future consideration)

### Risk 4: Runaway Cost from Autoscaling
**Impact:** Unexpected infrastructure bill if max replicas or max nodes are set too high
**Probability:** Low
**Mitigation:**
- Hard cap on node group max size (20 nodes)
- Hard cap on HPA max replicas per service
- CloudWatch alarm on EstimatedCharges > $5,000/month
- AWS Budget configured with 80% threshold notification
- Weekly cost review dashboard in Grafana using CloudWatch data source

### Risk 5: Prometheus Adapter CRD Conflicts with metrics-server
**Impact:** Custom metrics API fails, HPA cannot scale on custom metrics
**Probability:** Medium (if metrics-server is also registered for `custom.metrics.k8s.io`)
**Mitigation:**
- Verify only one provider is registered per API group
- Prometheus Adapter replaces metrics-server for custom metrics; metrics-server remains for resource metrics only
- Check `kubectl get apiservices | grep metrics` before deployment
- Test with `kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1` after deployment

## Future Enhancements

- KEDA integration for queue-based autoscaling (SQS, Kafka)
- Karpenter for faster, more efficient node provisioning
- Thanos or Grafana Mimir for long-term metrics storage
- Multi-cluster federation for cross-region scaling
- Spot instance integration for cost optimization on fault-tolerant workloads
- Predictive autoscaling using ML-based traffic forecasting
