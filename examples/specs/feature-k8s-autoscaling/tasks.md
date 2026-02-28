# Implementation Tasks: Kubernetes Autoscaling & Monitoring

## Task Breakdown

### Task 1: Create Terraform Module for EKS Node Group Autoscaling
**Status:** Pending
**Estimated Effort:** M (2-3 hours)
**Dependencies:** None
**Priority:** High

**Description:**
Create a Terraform module that configures the EKS managed node group with autoscaling boundaries, instance types, tagging for Cluster Autoscaler discovery, and encrypted EBS volumes.

**Implementation Steps:**
1. Create module directory `terraform/modules/eks-node-group/`
2. Define `variables.tf` with cluster_name, min/max/desired size, instance types, subnet IDs
3. Define `main.tf` with `aws_eks_node_group` resource and launch template
4. Add Cluster Autoscaler discovery tags (`k8s.io/cluster-autoscaler/enabled`, `k8s.io/cluster-autoscaler/<cluster-name>`)
5. Configure EBS encryption with gp3 volumes
6. Define `outputs.tf` with node group ARN, ASG name, role ARN
7. Create environment-specific tfvars files (dev, staging, prod)
8. Add `terraform.tf` with required providers and S3 backend configuration
9. Run `terraform fmt` and `terraform validate`

**Acceptance Criteria:**
- [ ] Terraform module creates EKS node group with min=3, max=20, desired=5
- [ ] Instance types are m5.xlarge and m5a.xlarge (mixed)
- [ ] Cluster Autoscaler tags applied to node group and ASG
- [ ] EBS volumes encrypted with gp3
- [ ] All resources tagged with team, environment, managed-by
- [ ] Module passes `terraform validate` and `terraform plan` without errors

**Validation Steps:**
```bash
terraform init
terraform validate
terraform plan -out=plan.tfplan
terraform show plan.tfplan  # Review planned changes
# After apply:
aws eks describe-nodegroup --cluster-name <cluster> --nodegroup-name api-workloads --query 'nodegroup.scalingConfig'
kubectl get nodes -l role=api-workloads
```

**Rollback Steps:**
```bash
terraform plan -destroy -target=module.eks_node_group
terraform apply -target=module.eks_node_group  # Revert to previous state via git revert + apply
```

**Files to Modify:**
- `terraform/modules/eks-node-group/main.tf`
- `terraform/modules/eks-node-group/variables.tf`
- `terraform/modules/eks-node-group/outputs.tf`
- `terraform/environments/prod/main.tf`
- `terraform/environments/prod/terraform.tfvars`

---

### Task 2: Deploy Prometheus Adapter via Helm
**Status:** Pending
**Estimated Effort:** M (2 hours)
**Dependencies:** None
**Priority:** High

**Description:**
Install the Prometheus Adapter Helm chart to expose custom application metrics (http_requests_per_second) via the Kubernetes custom metrics API, enabling HPA to scale on RPS.

**Implementation Steps:**
1. Add `prometheus-community/prometheus-adapter` Helm repo
2. Create base values file (`helm-values/base/prometheus-adapter.yaml`)
3. Configure Prometheus URL pointing to `prometheus-operated.monitoring.svc:9090`
4. Define custom metrics rule: map `http_requests_total` counter to `http_requests_per_second` rate
5. Configure resource metrics rules for CPU and memory
6. Create environment-specific overrides (dev, staging, prod)
7. Deploy with `helm upgrade --install prometheus-adapter prometheus-community/prometheus-adapter`
8. Verify custom metrics API is available

**Acceptance Criteria:**
- [ ] Prometheus Adapter pods running in `monitoring` namespace
- [ ] Custom metrics API registered (`kubectl get apiservices | grep custom.metrics`)
- [ ] `http_requests_per_second` metric available via custom metrics API
- [ ] No conflicts with existing metrics-server (resource metrics still work)
- [ ] Helm chart version pinned in deployment scripts

**Validation Steps:**
```bash
kubectl get pods -n monitoring -l app.kubernetes.io/name=prometheus-adapter
kubectl get apiservices | grep custom.metrics.k8s.io
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1" | jq .
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1/namespaces/api/pods/*/http_requests_per_second" | jq .
# Verify resource metrics still work:
kubectl top pods -n api
kubectl top nodes
```

**Rollback Steps:**
```bash
helm uninstall prometheus-adapter -n monitoring
# Verify resource metrics-server is unaffected:
kubectl get apiservices v1beta1.metrics.k8s.io
kubectl top nodes
```

**Files to Modify:**
- `helm-values/base/prometheus-adapter.yaml`
- `helm-values/dev/prometheus-adapter.yaml`
- `helm-values/staging/prometheus-adapter.yaml`
- `helm-values/prod/prometheus-adapter.yaml`
- `scripts/deploy-prometheus-adapter.sh`

---

### Task 3: Configure HPA for api-gateway Service
**Status:** Pending
**Estimated Effort:** M (2-3 hours)
**Dependencies:** Task 2
**Priority:** High

**Description:**
Create the HorizontalPodAutoscaler resource for the `api-gateway` deployment with CPU, memory, and custom RPS metric targets, along with scaling behavior policies.

**Implementation Steps:**
1. Create HPA manifest as Helm template (`charts/autoscaling/templates/hpa-api-gateway.yaml`)
2. Configure `scaleTargetRef` pointing to `api-gateway` Deployment
3. Set `minReplicas: 3`, `maxReplicas: 15`
4. Add CPU metric target at 70% utilization
5. Add memory metric target at 80% utilization
6. Add custom `http_requests_per_second` metric with averageValue 1000
7. Configure `behavior.scaleUp`: max 4 pods per 60 seconds, 0s stabilization
8. Configure `behavior.scaleDown`: max 1 pod per 120 seconds, 300s stabilization
9. Add labels (app, managed-by) and annotations (description, last-applied)
10. Deploy to dev and verify scaling behavior

**Acceptance Criteria:**
- [ ] HPA resource created in `api` namespace
- [ ] HPA shows `AbleToScale: True` and `ScalingActive: True`
- [ ] HPA references correct deployment and metrics
- [ ] Scale-up responds within 2 minutes of threshold breach
- [ ] Scale-down stabilization prevents premature downsizing
- [ ] Custom RPS metric resolves correctly from Prometheus Adapter

**Validation Steps:**
```bash
kubectl get hpa api-gateway-hpa -n api -o wide
kubectl describe hpa api-gateway-hpa -n api
# Check all metric targets are resolving:
kubectl get hpa api-gateway-hpa -n api -o jsonpath='{.status.conditions[*].type}'
# Verify custom metric:
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1/namespaces/api/pods/*/http_requests_per_second" | jq '.items[0].value'
# Generate load and observe scale-up:
kubectl run load-test --image=busybox --rm -it -- sh -c "while true; do wget -q -O- http://api-gateway.api.svc/health; done"
kubectl get hpa api-gateway-hpa -n api -w  # Watch replica changes
```

**Rollback Steps:**
```bash
kubectl delete hpa api-gateway-hpa -n api
# Or rollback Helm chart:
helm rollback autoscaling <previous-revision> -n api
```

**Files to Modify:**
- `charts/autoscaling/templates/hpa-api-gateway.yaml`
- `charts/autoscaling/values.yaml`
- `charts/autoscaling/values-dev.yaml`
- `charts/autoscaling/values-prod.yaml`

---

### Task 4: Configure HPA for user-service
**Status:** Pending
**Estimated Effort:** S (1 hour)
**Dependencies:** Task 2
**Priority:** High

**Description:**
Create the HorizontalPodAutoscaler resource for the `user-service` deployment, following the same pattern as api-gateway but with lower scaling limits.

**Implementation Steps:**
1. Create HPA manifest (`charts/autoscaling/templates/hpa-user-service.yaml`)
2. Configure `scaleTargetRef` pointing to `user-service` Deployment
3. Set `minReplicas: 3`, `maxReplicas: 10`
4. Add CPU (70%), memory (80%), and RPS (averageValue 500) targets
5. Apply same scaling behavior policies as api-gateway
6. Deploy and verify

**Acceptance Criteria:**
- [ ] HPA resource created in `api` namespace
- [ ] HPA shows `AbleToScale: True` and `ScalingActive: True`
- [ ] Max replicas capped at 10
- [ ] RPS target set to 500 (lower traffic service)
- [ ] Scaling behavior matches api-gateway pattern

**Validation Steps:**
```bash
kubectl get hpa user-service-hpa -n api -o wide
kubectl describe hpa user-service-hpa -n api
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1/namespaces/api/pods/*/http_requests_per_second" | jq '.items[] | select(.describedObject.name | startswith("user-service"))'
```

**Rollback Steps:**
```bash
kubectl delete hpa user-service-hpa -n api
```

**Files to Modify:**
- `charts/autoscaling/templates/hpa-user-service.yaml`
- `charts/autoscaling/values.yaml`

---

### Task 5: Deploy VPA in Recommendation Mode
**Status:** Pending
**Estimated Effort:** M (2 hours)
**Dependencies:** None
**Priority:** Medium

**Description:**
Deploy VerticalPodAutoscaler resources in `Off` mode (recommendation-only) for both API services, allowing operators to review and manually apply resource right-sizing suggestions.

**Implementation Steps:**
1. Verify VPA CRDs are installed (`kubectl get crd verticalpodautoscalers.autoscaling.k8s.io`)
2. If not installed, deploy VPA components via Helm or YAML manifests
3. Create VPA manifest for api-gateway with `updateMode: Off`
4. Create VPA manifest for user-service with `updateMode: Off`
5. Configure resource policies (minAllowed, maxAllowed) per container
6. Deploy to dev and verify recommendations appear
7. Document weekly review process for VPA recommendations

**Acceptance Criteria:**
- [ ] VPA resources created in `api` namespace with `updateMode: Off`
- [ ] VPA recommendations appear in `kubectl describe vpa`
- [ ] VPA does not restart or modify running pods
- [ ] Resource policies set reasonable bounds (cpu: 100m-4, memory: 128Mi-4Gi)
- [ ] VPA does not conflict with HPA (HPA manages replicas, VPA only recommends resources)

**Validation Steps:**
```bash
kubectl get vpa -n api
kubectl describe vpa api-gateway-vpa -n api
# Check recommendation section:
kubectl get vpa api-gateway-vpa -n api -o jsonpath='{.status.recommendation.containerRecommendations[0]}' | jq .
kubectl describe vpa user-service-vpa -n api
# Verify pods are NOT being restarted by VPA:
kubectl get pods -n api -w  # Watch for 5 minutes, no restarts
```

**Rollback Steps:**
```bash
kubectl delete vpa api-gateway-vpa -n api
kubectl delete vpa user-service-vpa -n api
# VPA in Off mode has no impact on running pods; deletion is safe
```

**Files to Modify:**
- `charts/autoscaling/templates/vpa-api-gateway.yaml`
- `charts/autoscaling/templates/vpa-user-service.yaml`
- `charts/autoscaling/values.yaml`

---

### Task 6: Create PodDisruptionBudgets
**Status:** Pending
**Estimated Effort:** S (1 hour)
**Dependencies:** None
**Priority:** High

**Description:**
Create PodDisruptionBudget resources for both API services to ensure at most 1 pod is unavailable during voluntary disruptions.

**Implementation Steps:**
1. Create PDB manifest for api-gateway with `maxUnavailable: 1`
2. Create PDB manifest for user-service with `maxUnavailable: 1`
3. Ensure label selectors match deployment pod template labels
4. Deploy and test with a simulated node drain

**Acceptance Criteria:**
- [ ] PDB resources created in `api` namespace
- [ ] PDB status shows `disruptionsAllowed >= 1` under normal conditions
- [ ] Node drain respects PDB (only evicts 1 pod at a time)
- [ ] Rolling updates respect PDB constraints
- [ ] Cluster Autoscaler respects PDB when scaling down nodes

**Validation Steps:**
```bash
kubectl get pdb -n api
kubectl describe pdb api-gateway-pdb -n api
# Verify disruptionsAllowed:
kubectl get pdb -n api -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.disruptionsAllowed}{"\n"}{end}'
# Test with node drain (non-prod):
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data --dry-run=client
```

**Rollback Steps:**
```bash
kubectl delete pdb api-gateway-pdb -n api
kubectl delete pdb user-service-pdb -n api
# PDB deletion has no impact on running pods
```

**Files to Modify:**
- `charts/autoscaling/templates/pdb-api-gateway.yaml`
- `charts/autoscaling/templates/pdb-user-service.yaml`
- `charts/autoscaling/values.yaml`

---

### Task 7: Create Prometheus ServiceMonitor and Alerting Rules
**Status:** Pending
**Estimated Effort:** M (3 hours)
**Dependencies:** Task 2
**Priority:** High

**Description:**
Create ServiceMonitor resources for API services to enable Prometheus scraping, and define PrometheusRule resources with alerting rules for HPA scaling failures, high latency, pod restarts, and Cluster Autoscaler issues.

**Implementation Steps:**
1. Create ServiceMonitor for `api-gateway` and `user-service` (scrape interval 15s, port `http-metrics`)
2. Verify Prometheus discovers the new targets
3. Create PrometheusRule with alert group `hpa-alerts`:
   - `HPAAtMaxReplicas`: firing when current == max for 5 minutes
   - `HPAScalingFailure`: firing when ScalingActive is false for 5 minutes
4. Create PrometheusRule with alert group `latency-alerts`:
   - `HighP95Latency`: P95 > 500ms for 2 minutes
5. Create PrometheusRule with alert group `pod-health-alerts`:
   - `HighPodRestartRate`: > 3 restarts in 10 minutes
   - `ClusterAutoscalerUnschedulable`: unschedulable pods > 0 for 5 minutes
6. Add severity labels and runbook URLs to all alerts
7. Verify alert rules are loaded by Prometheus

**Acceptance Criteria:**
- [ ] ServiceMonitor resources created and targets appear in Prometheus
- [ ] All 5 alerting rules loaded in Prometheus (`/api/v1/rules`)
- [ ] Alert expressions are syntactically valid (Prometheus evaluates without errors)
- [ ] Severity labels set correctly (critical for scaling failures, warning for capacity)
- [ ] Runbook URLs point to valid internal wiki pages
- [ ] `release: kube-prometheus-stack` label set for Prometheus Operator discovery

**Validation Steps:**
```bash
kubectl get servicemonitor -n monitoring
kubectl get prometheusrule -n monitoring
# Verify Prometheus targets:
kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring &
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.namespace=="api") | {endpoint: .scrapeUrl, health: .health}'
# Verify rules loaded:
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[] | select(.name | test("hpa|latency|pod-health")) | {name: .name, rules: [.rules[].name]}'
# Test alert expression manually:
curl -s 'http://localhost:9090/api/v1/query?query=kube_horizontalpodautoscaler_status_current_replicas==kube_horizontalpodautoscaler_spec_max_replicas' | jq .
```

**Rollback Steps:**
```bash
kubectl delete servicemonitor api-services -n monitoring
kubectl delete prometheusrule autoscaling-alerts -n monitoring
# Prometheus will stop scraping and remove alerting rules within 1 evaluation cycle (15s)
```

**Files to Modify:**
- `charts/autoscaling/templates/servicemonitor.yaml`
- `charts/autoscaling/templates/prometheusrule.yaml`
- `charts/autoscaling/values.yaml`

---

### Task 8: Build Grafana Dashboard for Autoscaling
**Status:** Pending
**Estimated Effort:** M (3 hours)
**Dependencies:** Task 7
**Priority:** Medium

**Description:**
Create a comprehensive Grafana dashboard as a JSON ConfigMap that visualizes autoscaling metrics: CPU/memory utilization, replica counts, RPS, P95 latency, VPA recommendations, Cluster Autoscaler status, and alert history.

**Implementation Steps:**
1. Design dashboard layout with rows: Overview, HPA Metrics, Pod Resources, Latency, Cluster Autoscaler, VPA Recommendations
2. Create panels:
   - Current replicas vs desired replicas (time series, per service)
   - CPU utilization vs HPA target (gauge + time series)
   - Memory utilization vs HPA target (gauge + time series)
   - RPS per service (time series)
   - P95 / P99 latency per service (time series)
   - Cluster node count (time series)
   - VPA recommended vs actual CPU/memory (table)
   - HPA scaling events (annotations on time series)
   - Active alerts (stat panel)
3. Add template variables: namespace, service, time range
4. Export dashboard as JSON
5. Create ConfigMap with `grafana_dashboard: "1"` label for sidecar auto-import
6. Deploy and verify dashboard loads in Grafana

**Acceptance Criteria:**
- [ ] Dashboard accessible at `/d/k8s-autoscaling` in Grafana
- [ ] All panels render data correctly with 7-day time range
- [ ] Template variables filter by namespace and service
- [ ] Dashboard loads within 3 seconds
- [ ] Dashboard is version-controlled as ConfigMap JSON
- [ ] Grafana sidecar auto-imports the dashboard on deployment

**Validation Steps:**
```bash
kubectl get configmap -n monitoring -l grafana_dashboard=1 | grep k8s-autoscaling
# Verify dashboard JSON is valid:
kubectl get configmap k8s-autoscaling-dashboard -n monitoring -o jsonpath='{.data.k8s-autoscaling\.json}' | python3 -m json.tool > /dev/null && echo "Valid JSON"
# Verify in Grafana UI:
curl -s -H "Authorization: Bearer <api-key>" https://grafana.internal/api/dashboards/uid/k8s-autoscaling | jq '.dashboard.title'
# Check panel count:
curl -s -H "Authorization: Bearer <api-key>" https://grafana.internal/api/dashboards/uid/k8s-autoscaling | jq '.dashboard.panels | length'
```

**Rollback Steps:**
```bash
kubectl delete configmap k8s-autoscaling-dashboard -n monitoring
# Grafana sidecar will remove the dashboard within its sync interval (60s default)
```

**Files to Modify:**
- `charts/autoscaling/templates/grafana-dashboard-configmap.yaml`
- `charts/autoscaling/dashboards/k8s-autoscaling.json`

---

### Task 9: Configure Cluster Autoscaler
**Status:** Pending
**Estimated Effort:** M (2-3 hours)
**Dependencies:** Task 1
**Priority:** High

**Description:**
Deploy the Cluster Autoscaler via Helm chart with IRSA authentication, configured to discover and manage the EKS managed node group auto-scaling group.

**Implementation Steps:**
1. Create IAM role and policy for Cluster Autoscaler via Terraform (IRSA)
2. Define IAM policy with `autoscaling:SetDesiredCapacity`, `autoscaling:TerminateInstanceInAutoScalingGroup`, `ec2:DescribeInstances`, `ec2:DescribeLaunchTemplateVersions`
3. Create trust policy for EKS OIDC provider
4. Create Helm values file with:
   - `autoDiscovery.clusterName: <cluster-name>`
   - `rbac.serviceAccount.annotations.eks.amazonaws.com/role-arn: <role-arn>`
   - `extraArgs.balance-similar-node-groups: true`
   - `extraArgs.scale-down-delay-after-add: 10m`
   - `extraArgs.scale-down-unneeded-time: 10m`
   - `extraArgs.scan-interval: 10s`
5. Deploy with `helm upgrade --install cluster-autoscaler autoscaler/cluster-autoscaler`
6. Verify Cluster Autoscaler discovers node groups
7. Test node scale-up by creating pods that exceed current capacity

**Acceptance Criteria:**
- [ ] Cluster Autoscaler pod running in `kube-system` namespace
- [ ] IRSA configured (ServiceAccount annotated with IAM role ARN)
- [ ] Cluster Autoscaler discovers EKS node group via autodiscovery tags
- [ ] Scale-up triggered when pods are unschedulable
- [ ] Scale-down triggered when nodes are underutilized for 10 minutes
- [ ] Balance across AZs when using multiple subnets

**Validation Steps:**
```bash
kubectl get pods -n kube-system -l app.kubernetes.io/name=cluster-autoscaler
kubectl logs -l app.kubernetes.io/name=cluster-autoscaler -n kube-system --tail=20
# Check node group discovery:
kubectl logs -l app.kubernetes.io/name=cluster-autoscaler -n kube-system | grep "node group"
# Check IRSA:
kubectl get sa cluster-autoscaler -n kube-system -o jsonpath='{.metadata.annotations.eks\.amazonaws\.com/role-arn}'
# Verify IAM role works:
kubectl exec -it deploy/cluster-autoscaler -n kube-system -- aws sts get-caller-identity
# Test scale-up:
kubectl run scale-test --image=nginx --replicas=50 --requests='cpu=500m,memory=512Mi' --dry-run=client -o yaml | kubectl apply -f -
kubectl get nodes -w  # Watch for new nodes joining
kubectl delete deployment scale-test  # Cleanup
```

**Rollback Steps:**
```bash
helm uninstall cluster-autoscaler -n kube-system
# Terraform rollback for IAM resources:
terraform destroy -target=aws_iam_role.cluster_autoscaler -target=aws_iam_policy.cluster_autoscaler
# Node group remains, but no automatic scaling; manual scaling via AWS console or eksctl
```

**Files to Modify:**
- `terraform/modules/cluster-autoscaler-iam/main.tf`
- `terraform/modules/cluster-autoscaler-iam/variables.tf`
- `terraform/modules/cluster-autoscaler-iam/outputs.tf`
- `helm-values/base/cluster-autoscaler.yaml`
- `helm-values/prod/cluster-autoscaler.yaml`
- `scripts/deploy-cluster-autoscaler.sh`

---

### Task 10: Set Up PagerDuty Alerting Integration
**Status:** Pending
**Estimated Effort:** M (2 hours)
**Dependencies:** Task 7
**Priority:** Medium

**Description:**
Configure Alertmanager to route critical alerts to PagerDuty and non-critical alerts to Slack/email, using the existing kube-prometheus-stack Alertmanager instance.

**Implementation Steps:**
1. Store PagerDuty integration key in AWS Secrets Manager
2. Create ExternalSecret to inject PagerDuty key into `alertmanager-secret` Secret
3. Update Alertmanager configuration in kube-prometheus-stack Helm values:
   - Route `severity=critical` to PagerDuty receiver
   - Route `severity=warning` to Slack receiver
   - Set group_by, group_wait, group_interval, repeat_interval
4. Add PagerDuty receiver configuration with routing key
5. Add Slack receiver configuration with webhook URL
6. Apply updated Helm values
7. Test alert routing by triggering a test alert

**Acceptance Criteria:**
- [ ] PagerDuty integration key stored in AWS Secrets Manager (not in Helm values)
- [ ] Alertmanager routes critical alerts to PagerDuty
- [ ] Alertmanager routes warning alerts to Slack channel
- [ ] Test alert received in PagerDuty within 60 seconds
- [ ] Alert grouping and deduplication working
- [ ] Silence and inhibition rules configured to prevent alert storms

**Validation Steps:**
```bash
# Check Alertmanager config:
kubectl get secret alertmanager-kube-prometheus-stack-alertmanager -n monitoring -o jsonpath='{.data.alertmanager\.yaml}' | base64 -d | head -50
# Verify Alertmanager is healthy:
kubectl port-forward svc/alertmanager-operated 9093:9093 -n monitoring &
curl -s http://localhost:9093/api/v2/status | jq '.config'
# Send test alert:
curl -X POST http://localhost:9093/api/v2/alerts -H 'Content-Type: application/json' -d '[{"labels":{"alertname":"TestAlert","severity":"critical","team":"platform"},"annotations":{"summary":"Test alert for PagerDuty integration"}}]'
# Verify in PagerDuty UI that incident was created
# Check Alertmanager logs:
kubectl logs -l app.kubernetes.io/name=alertmanager -n monitoring --tail=20
```

**Rollback Steps:**
```bash
# Revert Alertmanager configuration:
helm rollback kube-prometheus-stack <previous-revision> -n monitoring
# Or remove PagerDuty receiver from values and re-apply:
helm upgrade kube-prometheus-stack prometheus-community/kube-prometheus-stack -f values-without-pagerduty.yaml -n monitoring
```

**Files to Modify:**
- `helm-values/base/kube-prometheus-stack-alertmanager.yaml`
- `terraform/modules/secrets/pagerduty.tf`
- `charts/autoscaling/templates/external-secret-pagerduty.yaml`

---

### Task 11: Create Cost Monitoring Alerts
**Status:** Pending
**Estimated Effort:** S (1-2 hours)
**Dependencies:** Task 9
**Priority:** Medium

**Description:**
Set up AWS CloudWatch alarms and Grafana panels to monitor infrastructure costs related to autoscaling, including estimated monthly charges and node count thresholds.

**Implementation Steps:**
1. Create Terraform resource for CloudWatch metric alarm on `EstimatedCharges` > $5,000
2. Configure SNS topic for cost alert notifications (email to finance and platform teams)
3. Add AWS Cost Explorer tags to all autoscaling resources (`CostCenter: platform-infra`)
4. Create Grafana panel showing node count over time (from `kube_node_info` metric)
5. Create Grafana panel showing total pod count and resource utilization summary
6. Add AWS Budget with 80% threshold notification (Terraform)

**Acceptance Criteria:**
- [ ] CloudWatch alarm fires when estimated charges exceed $5,000/month
- [ ] SNS notifications sent to platform team and finance
- [ ] All autoscaling resources tagged for Cost Explorer filtering
- [ ] Grafana cost overview panels show node count and resource trends
- [ ] AWS Budget configured with 80% threshold alert

**Validation Steps:**
```bash
# Verify CloudWatch alarm:
aws cloudwatch describe-alarms --alarm-names "k8s-autoscaling-cost-threshold" --query 'MetricAlarms[0].{State:StateValue,Threshold:Threshold}'
# Verify SNS subscription:
aws sns list-subscriptions-by-topic --topic-arn <topic-arn> --query 'Subscriptions[*].{Endpoint:Endpoint,Protocol:Protocol}'
# Verify resource tags:
aws eks describe-nodegroup --cluster-name <cluster> --nodegroup-name api-workloads --query 'nodegroup.tags'
# Verify Budget:
aws budgets describe-budgets --account-id <account-id> --query 'Budgets[?BudgetName==`k8s-autoscaling-monthly`]'
```

**Rollback Steps:**
```bash
terraform destroy -target=aws_cloudwatch_metric_alarm.cost_threshold
terraform destroy -target=aws_sns_topic.cost_alerts
terraform destroy -target=aws_budgets_budget.k8s_autoscaling
# Tags can be removed via Terraform revert
```

**Files to Modify:**
- `terraform/modules/cost-monitoring/main.tf`
- `terraform/modules/cost-monitoring/variables.tf`
- `charts/autoscaling/dashboards/k8s-autoscaling.json` (add cost panels)

---

### Task 12: Load Test and Validate Scaling Behavior
**Status:** Pending
**Estimated Effort:** L (4-5 hours)
**Dependencies:** Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9
**Priority:** High

**Description:**
Execute comprehensive load tests to validate end-to-end autoscaling behavior, including HPA scale-up/down timing, Cluster Autoscaler node provisioning, PDB enforcement, and alerting pipeline.

**Implementation Steps:**
1. Set up load testing tool (k6 or Locust) with scripts targeting api-gateway and user-service
2. Baseline test: measure current performance at normal load (100 RPS)
3. Scale-up test: ramp from 100 to 5,000 RPS over 5 minutes, observe HPA and CA behavior
4. Sustained load test: hold 3,000 RPS for 30 minutes, verify stability
5. Scale-down test: drop load to 100 RPS, verify 300s stabilization window before scale-down
6. PDB test: trigger rolling update during load, verify zero dropped requests
7. Alert test: push services to max replicas, verify HPAAtMaxReplicas alert fires
8. Node drain test: drain a node during load, verify PDB and CA response
9. Document results: scale-up latency, throughput, error rate, cost impact

**Acceptance Criteria:**
- [ ] HPA scale-up completes within 120 seconds of threshold breach
- [ ] Zero HTTP 5xx errors during scale-up and scale-down events
- [ ] Zero dropped requests during PDB-protected rolling update
- [ ] Cluster Autoscaler provisions new nodes within 3 minutes when needed
- [ ] Scale-down respects 300s stabilization window
- [ ] All alerts fire correctly during overload scenario
- [ ] P95 latency stays under 500ms at 3,000 RPS sustained load
- [ ] Results documented in test report

**Validation Steps:**
```bash
# Install k6:
brew install k6  # or download binary

# Run baseline test:
k6 run --vus 10 --duration 5m scripts/load-test-baseline.js

# Run scale-up test:
k6 run --stage '0s:10,2m:500,5m:500' scripts/load-test-scaleup.js

# Monitor in real-time:
kubectl get hpa -n api -w &
kubectl get pods -n api -w &
kubectl get nodes -w &

# Verify metrics in Prometheus:
curl -s 'http://localhost:9090/api/v1/query?query=kube_horizontalpodautoscaler_status_current_replicas{namespace="api"}' | jq .

# Check error rate during test:
curl -s 'http://localhost:9090/api/v1/query?query=sum(rate(http_requests_total{namespace="api",code=~"5.."}[1m]))/sum(rate(http_requests_total{namespace="api"}[1m]))' | jq .
```

**Rollback Steps:**
```bash
# Stop load test:
# Ctrl+C the k6 process

# If services are in a bad state, manually scale down:
kubectl scale deployment api-gateway --replicas=3 -n api
kubectl scale deployment user-service --replicas=3 -n api

# Cleanup test resources:
kubectl delete deployment load-test-runner -n api 2>/dev/null
```

**Files to Modify:**
- `tests/load/scripts/load-test-baseline.js`
- `tests/load/scripts/load-test-scaleup.js`
- `tests/load/scripts/load-test-sustained.js`
- `tests/load/results/load-test-report.md`

---

### Task 13: Write Runbooks and Documentation
**Status:** Pending
**Estimated Effort:** M (2-3 hours)
**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12
**Priority:** Medium

**Description:**
Create operational runbooks for each alerting rule, document the autoscaling architecture, and write operational procedures for common maintenance tasks.

**Implementation Steps:**
1. Create runbook: HPAAtMaxReplicas — investigation steps, escalation, resolution
2. Create runbook: HPAScalingFailure — common causes, debugging, resolution
3. Create runbook: HighP95Latency — investigation, correlation with scaling events
4. Create runbook: HighPodRestartRate — OOMKill analysis, resource tuning
5. Create runbook: ClusterAutoscalerUnschedulable — node capacity, quotas, ASG health
6. Document architecture overview with diagram
7. Document weekly VPA review process
8. Document Terraform/Helm deployment procedures
9. Document rollback procedures for each component
10. Add troubleshooting FAQ

**Acceptance Criteria:**
- [ ] Runbook exists for each PrometheusRule alert
- [ ] Runbooks include investigation steps, common causes, and resolution procedures
- [ ] Architecture documentation reflects current deployed state
- [ ] Deployment and rollback procedures tested and accurate
- [ ] VPA review process documented with schedule
- [ ] Documentation accessible at internal wiki and linked from alert annotations

**Validation Steps:**
```bash
# Verify runbook URLs in PrometheusRule annotations:
kubectl get prometheusrule autoscaling-alerts -n monitoring -o jsonpath='{range .spec.groups[*].rules[*]}{.alert}{"\t"}{.annotations.runbook_url}{"\n"}{end}'
# Verify each runbook URL is accessible:
for url in $(kubectl get prometheusrule autoscaling-alerts -n monitoring -o jsonpath='{range .spec.groups[*].rules[*]}{.annotations.runbook_url}{"\n"}{end}'); do
  curl -s -o /dev/null -w "%{http_code} $url\n" "$url"
done
```

**Rollback Steps:**
```bash
# Documentation is version-controlled in Git; rollback via git revert
git log --oneline -- docs/runbooks/ docs/architecture/
git revert <commit-sha>
```

**Files to Modify:**
- `docs/runbooks/hpa-max-replicas.md`
- `docs/runbooks/hpa-scaling-failure.md`
- `docs/runbooks/high-p95-latency.md`
- `docs/runbooks/high-pod-restart-rate.md`
- `docs/runbooks/cluster-autoscaler-unschedulable.md`
- `docs/architecture/autoscaling-overview.md`
- `docs/operations/vpa-review-process.md`
- `docs/operations/deployment-procedures.md`

---

### Task 14: Chaos Testing
**Status:** Pending
**Estimated Effort:** M (3 hours)
**Dependencies:** Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9
**Priority:** High

**Description:**
Execute chaos engineering experiments to validate resilience of the autoscaling infrastructure under failure conditions: pod kills, node failures, Prometheus Adapter unavailability, and network partitions.

**Implementation Steps:**
1. Pod kill experiment: randomly terminate 50% of api-gateway pods, verify HPA restores replicas
2. Node failure experiment: cordon and drain a node, verify PDB enforcement and CA replacement
3. Prometheus Adapter failure: scale Adapter to 0, verify HPA falls back to resource metrics
4. High-latency injection: add network delay to api-gateway pods, verify latency alert fires
5. Resource exhaustion: set api-gateway memory limit low, trigger OOMKill, verify restart alert
6. Scaling limit: push to maxReplicas, verify HPAAtMaxReplicas alert fires
7. Cluster Autoscaler failure: scale CA to 0, verify unschedulable alert fires
8. Document results and update runbooks with observed behavior

**Acceptance Criteria:**
- [ ] HPA restores pod count within 2 minutes after 50% pod kill
- [ ] PDB prevents total service outage during node drain
- [ ] HPA continues scaling on CPU/memory when Prometheus Adapter is unavailable
- [ ] All relevant alerts fire correctly during each chaos scenario
- [ ] Zero data loss or corruption across all experiments
- [ ] Service recovers to healthy state within 5 minutes after each experiment
- [ ] Results documented with timestamps and observations

**Validation Steps:**
```bash
# Pod kill:
kubectl delete pod -l app=api-gateway -n api --grace-period=0 --force $(kubectl get pods -l app=api-gateway -n api -o name | head -3)
kubectl get pods -n api -w  # Watch recovery
kubectl get hpa api-gateway-hpa -n api -w  # Watch scaling

# Node drain:
NODE=$(kubectl get pods -l app=api-gateway -n api -o jsonpath='{.items[0].spec.nodeName}')
kubectl drain $NODE --ignore-daemonsets --delete-emptydir-data
kubectl get pdb -n api  # Verify disruptionsAllowed
kubectl uncordon $NODE  # Restore node

# Prometheus Adapter failure:
kubectl scale deploy prometheus-adapter -n monitoring --replicas=0
kubectl describe hpa api-gateway-hpa -n api  # Check if resource metrics still work
kubectl scale deploy prometheus-adapter -n monitoring --replicas=1  # Restore

# Verify service health after each experiment:
curl -s http://api-gateway.api.svc/health
kubectl get events -n api --sort-by='.lastTimestamp' | tail -20
```

**Rollback Steps:**
```bash
# Restore all chaos experiments:
kubectl uncordon --all  # Uncordon any drained nodes
kubectl scale deploy prometheus-adapter -n monitoring --replicas=1
kubectl scale deploy cluster-autoscaler -n kube-system --replicas=1

# If services are unhealthy, restart deployments:
kubectl rollout restart deployment api-gateway -n api
kubectl rollout restart deployment user-service -n api
```

**Files to Modify:**
- `tests/chaos/pod-kill-experiment.yaml`
- `tests/chaos/node-drain-experiment.sh`
- `tests/chaos/adapter-failure-experiment.sh`
- `tests/chaos/results/chaos-test-report.md`

---

## Implementation Order

### Week 1: Infrastructure Foundation & Core Autoscaling

**Day 1 (Foundation):**
1. Task 1: Terraform module for EKS node group (2-3h) — no dependencies, creates compute foundation
2. Task 2: Deploy Prometheus Adapter (2h) — no dependencies, enables custom metrics

**Day 2 (HPA & VPA):**
3. Task 3: HPA for api-gateway (2-3h) — depends on Task 2
4. Task 4: HPA for user-service (1h) — depends on Task 2, mirrors Task 3
5. Task 5: VPA in recommendation mode (2h) — no dependencies, parallel with HPAs

**Day 3 (Resilience & Monitoring):**
6. Task 6: PodDisruptionBudgets (1h) — no dependencies
7. Task 7: Prometheus ServiceMonitor and alerting rules (3h) — depends on Task 2
8. Task 9: Cluster Autoscaler (2-3h) — depends on Task 1

**Day 4 (Dashboards & Alerting):**
9. Task 8: Grafana dashboard (3h) — depends on Task 7
10. Task 10: PagerDuty integration (2h) — depends on Task 7

**Day 5 (Cost & Validation):**
11. Task 11: Cost monitoring alerts (1-2h) — depends on Task 9
12. Task 12: Load testing and scaling validation (4-5h) — depends on Tasks 3-9

### Week 2: Validation, Chaos Testing & Documentation

**Day 1-2:**
13. Task 14: Chaos testing (3h) — depends on Tasks 3-9
14. Task 13: Runbooks and documentation (2-3h) — depends on Tasks 1-12

**Day 3-5:**
- Staging environment deployment and validation
- Production environment deployment
- Post-deployment monitoring (30 min observation)
- Final documentation review

## Progress Tracking

**Total Tasks:** 14
**Completed:** 0
**In Progress:** 0
**Remaining:** 14

**Estimated Total Effort:** ~32-40 hours (~1.5-2 weeks for 1 SRE)

### Status Legend
- **Pending**: Not started
- **In Progress**: Currently being worked on
- **Completed**: Done, validated, and deployed
- **Blocked**: Waiting on dependencies or external factors (e.g., AWS quota increase)

### Progress by Category
- **Terraform/AWS**: 0/3 (Tasks 1, 9, 11)
- **Autoscaling Resources**: 0/4 (Tasks 3, 4, 5, 6)
- **Monitoring & Alerting**: 0/4 (Tasks 2, 7, 8, 10)
- **Validation & Testing**: 0/2 (Tasks 12, 14)
- **Documentation**: 0/1 (Task 13)

## Notes

- Tasks 1 and 2 are foundational and should be done first (no dependencies)
- Tasks 3, 4, 5, 6 can run in parallel after Task 2 is complete
- Task 9 (Cluster Autoscaler) depends on Task 1 (node group must exist first)
- Task 12 (load testing) is the critical validation gate before production deployment
- Task 14 (chaos testing) should be done in staging before production
- AWS service quota for EC2 instances must be verified before Task 1 (max 20 nodes)
- PagerDuty integration key must be provisioned before Task 10

## Risk Items

- **AWS quota limits**: Verify EC2 instance limits can accommodate 20 nodes before Task 1
- **Prometheus Adapter CRD conflicts**: Check for existing custom metrics API registrations before Task 2
- **HPA flapping**: Monitor closely after Task 3; may need to adjust stabilization windows
- **Cluster Autoscaler IAM permissions**: Verify IRSA is configured on the EKS cluster before Task 9
- **PagerDuty service provisioning**: Ensure integration key is available before Task 10
- **Load testing impact**: Run Task 12 in staging only; never load test production directly
