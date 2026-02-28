# Implementation Notes: Kubernetes Autoscaling & Monitoring

## Decisions Made During Implementation
| Decision | Rationale | Task |
|----------|-----------|------|
| Used `kube-prometheus-stack` Helm chart instead of deploying Prometheus Operator and Grafana separately | The umbrella chart manages CRD lifecycle, Alertmanager config, and Grafana sidecar in one release — reduces Helm release sprawl | Task 7, Task 8 |
| Set HPA `scaleDown.stabilizationWindowSeconds` to 300s (up from default 0s for scale-up, 300s kept for scale-down) | Observed traffic oscillation in staging causing 3 rapid scale-down/up cycles within 10 minutes; 300s stabilization eliminated flapping | Task 3 |
| Pinned Prometheus Adapter Helm chart to v4.10.0 | v4.11.0 introduced a breaking change in custom metrics rule format; pinned to last stable version until upstream fix is released | Task 2 |

## Deviations from Design
| Planned | Actual | Reason |
|---------|--------|--------|
| VPA `updateMode: Auto` for gradual rollout | VPA `updateMode: Off` (recommendation-only) | Auto mode caused unexpected pod restarts in staging during peak hours; switched to Off and apply recommendations manually during maintenance windows |
| Kubecost for cost monitoring | AWS Cost Explorer with resource tags | Kubecost Helm chart conflicted with existing Prometheus TSDB storage limits; AWS Cost Explorer tags provide sufficient cost attribution without additional in-cluster components |
| Separate ServiceMonitor per service | Single ServiceMonitor with label selector `app in (api-gateway, user-service)` | Reduces manifest duplication; Prometheus discovers both services via one ServiceMonitor with a set-based selector |

## Blockers Encountered
| Blocker | Resolution | Impact |
|---------|------------|--------|
| Prometheus Adapter CRDs conflicted with existing metrics-server registration for `custom.metrics.k8s.io` | Removed metrics-server `--enable-custom-metrics` flag; metrics-server now handles only `metrics.k8s.io` (resource metrics), Prometheus Adapter handles `custom.metrics.k8s.io` | Task 2 delayed by 3 hours |
| EKS managed node group `maxSize: 20` hit AWS EC2 service quota (limit was 15 on-demand m5.xlarge in us-east-1) | Submitted AWS quota increase request; approved after 1 business day; temporarily set maxSize to 15 until quota was raised | Task 1 delayed by 1 day |
| Grafana sidecar not discovering dashboard ConfigMap | Missing label `grafana_dashboard: "1"` on ConfigMap; Grafana sidecar requires this exact label for auto-import | Task 8 delayed by 30 minutes |

## Notes
- All 14 tasks completed; zero downtime observed during scaling events across 48 hours of production monitoring
- Load test results: HPA scale-up latency averaged 87 seconds (well under 120s target); P95 latency remained under 400ms at 3,000 RPS
- VPA recommendations applied during first weekly review: api-gateway CPU request reduced from 500m to 350m, memory from 512Mi to 384Mi — projected 23% cost reduction
- Chaos testing passed all 7 experiments; updated runbooks with observed recovery times
