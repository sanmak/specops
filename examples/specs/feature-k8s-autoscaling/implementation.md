# Implementation Journal: Kubernetes Autoscaling & Monitoring

## Summary
All 14 tasks completed. 3 key decisions (kube-prometheus-stack chart, HPA stabilization window, Prometheus Adapter pin). 3 deviations from design (VPA recommendation-only mode, AWS Cost Explorer over Kubecost, single ServiceMonitor). 3 blockers resolved (CRD conflict, EC2 quota, Grafana sidecar). Zero downtime observed during scaling events across 48 hours of production monitoring.

## Decision Log
| # | Decision | Rationale | Task | Timestamp |
|---|----------|-----------|------|-----------|
| 1 | Used `kube-prometheus-stack` Helm chart instead of deploying Prometheus Operator and Grafana separately | The umbrella chart manages CRD lifecycle, Alertmanager config, and Grafana sidecar in one release — reduces Helm release sprawl | Task 7, Task 8 | 2025-02-20 |
| 2 | Set HPA `scaleDown.stabilizationWindowSeconds` to 300s | Observed traffic oscillation in staging causing 3 rapid scale-down/up cycles within 10 minutes; 300s stabilization eliminated flapping | Task 3 | 2025-02-17 |
| 3 | Pinned Prometheus Adapter Helm chart to v4.10.0 | v4.11.0 introduced a breaking change in custom metrics rule format; pinned to last stable version until upstream fix is released | Task 2 | 2025-02-16 |

## Deviations from Design
| Planned | Actual | Reason | Task |
|---------|--------|--------|------|
| VPA `updateMode: Auto` for gradual rollout | VPA `updateMode: Off` (recommendation-only) | Auto mode caused unexpected pod restarts in staging during peak hours; switched to Off and apply recommendations manually during maintenance windows | Task 4 |
| Kubecost for cost monitoring | AWS Cost Explorer with resource tags | Kubecost Helm chart conflicted with existing Prometheus TSDB storage limits; AWS Cost Explorer tags provide sufficient cost attribution without additional in-cluster components | Task 10 |
| Separate ServiceMonitor per service | Single ServiceMonitor with label selector `app in (api-gateway, user-service)` | Reduces manifest duplication; Prometheus discovers both services via one ServiceMonitor with a set-based selector | Task 8 |

## Blockers Encountered
| Blocker | Resolution | Impact | Task |
|---------|------------|--------|------|
| Prometheus Adapter CRDs conflicted with existing metrics-server registration for `custom.metrics.k8s.io` | Removed metrics-server `--enable-custom-metrics` flag; metrics-server now handles only `metrics.k8s.io` (resource metrics), Prometheus Adapter handles `custom.metrics.k8s.io` | Task 2 delayed by 3 hours | Task 2 |
| EKS managed node group `maxSize: 20` hit AWS EC2 service quota (limit was 15 on-demand m5.xlarge in us-east-1) | Submitted AWS quota increase request; approved after 1 business day; temporarily set maxSize to 15 until quota was raised | Task 1 delayed by 1 day | Task 1 |
| Grafana sidecar not discovering dashboard ConfigMap | Missing label `grafana_dashboard: "1"` on ConfigMap; Grafana sidecar requires this exact label for auto-import | Task 8 delayed by 30 minutes | Task 8 |

## Session Log
- **2025-02-15**: Started implementation. Completed Task 1 (delayed by EC2 quota). Tasks 2-3 started.
- **2025-02-16**: Resumed at Task 2. Completed Tasks 2-5. Blocker hit on Task 2 (CRD conflict).
- **2025-02-20**: Resumed at Task 6. Completed Tasks 6-10. Blocker hit on Task 8 (Grafana sidecar).
- **2025-02-24**: Resumed at Task 11. Completed Tasks 11-14. All tasks done.
