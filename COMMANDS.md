# TARS CLI - Complete Command Reference

**Total Commands: 88**

## Core Monitoring (10)
- `health` - Check cluster health
- `pods` - List pods with status and resource usage
- `nodes` - List cluster nodes with status
- `events` - Show recent cluster events
- `watch` - Real-time pod monitoring dashboard
- `top` - Show top resource-consuming pods
- `metrics` - Show resource metrics
- `check` - Quick cluster health check
- `pulse` - Show cluster pulse (quick overview)
- `god` - God mode - show everything

## Diagnostics & Troubleshooting (12)
- `diagnose` - Diagnose pod issues with AI
- `analyze` - Analyze cluster with AI insights
- `triage` - AI-powered issue triage
- `errors` - Show pods with errors and failures
- `crashloop` - Find pods in CrashLoopBackOff
- `pending` - Find pending pods
- `oom` - Find OOMKilled pods
- `logs` - Get pod logs
- `aggregate_logs` - Aggregate logs from multiple pods
- `describe` - Describe a Kubernetes resource
- `trace` - Trace service requests
- `bottleneck` - Find performance bottlenecks

## Resource Management (15)
- `deployments` - List deployments
- `services` - List services
- `namespaces` - List all namespaces
- `configmaps` - List configmaps
- `secrets` - List secrets
- `ingress` - List ingress resources
- `volumes` - List persistent volumes and claims
- `crds` - List Custom Resource Definitions
- `resources` - Show resource usage and quotas
- `quota` - Show resource quotas
- `context` - Show current Kubernetes context
- `restart` - Restart a deployment or statefulset
- `scale` - Scale a deployment or statefulset
- `rollback` - Rollback a deployment or statefulset
- `history` - Show rollout history

## Node Operations (4)
- `cordon` - Cordon a node (mark unschedulable)
- `uncordon` - Uncordon a node (mark schedulable)
- `drain` - Drain a node
- `exec` - Execute command in a pod

## Security & Compliance (4)
- `security_scan` - Scan for security issues
- `compliance` - Check compliance with best practices
- `audit` - Show audit logs
- `network` - Show network policies and connectivity

## Alerts & Monitoring (4)
- `alert` - Create an alert rule
- `alert_history` - Show alert history
- `alert_webhook` - Configure alert webhook
- `spike` - Monitor for metric spikes

## Prometheus Integration (10)
- `prom_check` - Check Prometheus connection
- `prom_metrics` - List Prometheus metrics
- `prom_query` - Execute Prometheus query
- `prom_alerts` - Show Prometheus alerts
- `prom_dashboard` - Open Prometheus dashboard
- `prom_export` - Export Prometheus data
- `prom_compare` - Compare Prometheus metrics
- `prom_record` - Create Prometheus recording rule
- `cardinality` - Show metric cardinality
- `cardinality_labels` - Show label cardinality for metric

## Performance & Testing (6)
- `benchmark` - Run performance benchmarks
- `blast` - Load test a service
- `profile` - Profile pod performance
- `forecast` - Forecast resource usage
- `heatmap` - Generate resource heatmap
- `compare` - Compare two resources

## SRE & Reliability (10)
- `sli` - Show Service Level Indicators
- `slo` - Show Service Level Objectives
- `incident_report` - Generate incident report
- `timeline` - Show resource timeline
- `story` - Generate cluster story (timeline)
- `oncall` - Show on-call information
- `runbook` - Show runbook for issue
- `replay` - Replay past incident
- `autofix` - Auto-fix common issues
- `smart_scale` - AI-powered smart scaling

## Advanced Operations (8)
- `chaos` - Chaos engineering experiments
- `multi_cluster` - Multi-cluster operations
- `snapshot` - Create cluster snapshot
- `export` - Export cluster resources
- `diff` - Show diff between live and file
- `dashboard` - Launch interactive dashboard
- `port_forward` - Forward local port to pod
- `cost` - Estimate resource costs

## Utility & Fun (5)
- `setup` - Setup and validate TARS configuration
- `version` - Show version
- `humor` - Set TARS humor level
- `quote` - Get a random TARS quote
- `creator` - Show TARS creator info

---

## Usage Examples

```bash
# Quick health check
tars health

# Watch pods in real-time
tars watch -n production

# Find problematic pods
tars crashloop -n default
tars oom -n production

# AI-powered diagnostics
tars diagnose my-pod -n default
tars triage -n production

# Resource management
tars scale deployment my-app 5 -n production
tars restart deployment my-app -n production

# Security & compliance
tars security-scan -n production
tars compliance -n default

# Prometheus queries
tars prom-query 'rate(http_requests_total[5m])'
tars prom-alerts

# SRE operations
tars sli -n production
tars slo -n production
tars runbook crashloop

# Fun
tars humor 95
tars quote
tars god
```

## AI-Powered Features

TARS includes AI-powered analysis when `GEMINI_API_KEY` is set:
- `diagnose` - AI diagnosis of pod issues
- `analyze` - AI cluster analysis
- `triage` - AI-powered issue prioritization
- `smart_scale` - AI-based scaling recommendations

## Configuration

Set environment variables:
```bash
export GEMINI_API_KEY='your-key'
export PROMETHEUS_URL='http://prometheus:9090'
```

Run setup:
```bash
tars setup
```

---

**TARS CLI** - Technical Assistance & Reliability System
Built for Kubernetes SREs and DevOps Engineers
