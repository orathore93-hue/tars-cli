# Prometheus Integration Guide

## Overview

TARS CLI now includes production-ready Prometheus integration to query metrics, monitor alerts, and display dashboards directly from your terminal.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Prometheus URL

```bash
# Set environment variable (recommended)
export PROMETHEUS_URL='http://your-prometheus-server:9090'

# Or use --url flag with each command
tars prom-check --url http://prometheus.example.com:9090
```

### 3. Verify Connection

```bash
tars prom-check
```

## Available Commands

### `tars prom-check`
Check Prometheus connection and get basic info.

```bash
tars prom-check
tars prom-check --url http://prometheus.example.com:9090
```

**Output:**
- Connection status
- Total metrics available

---

### `tars prom-metrics`
Show CPU and memory metrics for pods from Prometheus.

```bash
# All pods in default namespace
tars prom-metrics

# Specific namespace
tars prom-metrics --namespace production

# Specific pod
tars prom-metrics --namespace production --pod api-server-xyz
```

**Metrics Shown:**
- CPU usage (cores) - 5 minute average
- Memory usage (MB)
- Per container breakdown

---

### `tars prom-alerts`
Display active Prometheus alerts.

```bash
tars prom-alerts
tars prom-alerts --url http://prometheus.example.com:9090
```

**Output:**
- Alert name
- Severity level
- Instance
- Summary

---

### `tars prom-query`
Run custom PromQL queries.

```bash
# CPU rate
tars prom-query 'rate(container_cpu_usage_seconds_total[5m])'

# Memory usage
tars prom-query 'container_memory_usage_bytes{namespace="production"}'

# HTTP request rate
tars prom-query 'rate(http_requests_total[5m])'

# Custom metrics
tars prom-query 'your_custom_metric{label="value"}'
```

**Features:**
- Displays up to 20 results
- Shows metric name, labels, and values
- Supports any valid PromQL query

---

### `tars prom-dashboard`
Comprehensive metrics dashboard for a namespace.

```bash
# Default namespace
tars prom-dashboard

# Specific namespace
tars prom-dashboard --namespace production
```

**Displays:**
1. **CPU Usage** - Top 10 pods by CPU (5m avg)
2. **Memory Usage** - Top 10 pods by memory
3. **Network I/O** - Top 10 pods by network receive rate

---

## Common Use Cases

### 1. Monitor Resource Usage

```bash
# Quick dashboard view
tars prom-dashboard --namespace production

# Detailed pod metrics
tars prom-metrics --namespace production
```

### 2. Check Active Alerts

```bash
# View all firing alerts
tars prom-alerts

# Combine with triage
tars triage
tars prom-alerts
```

### 3. Custom Metric Analysis

```bash
# Application-specific metrics
tars prom-query 'http_request_duration_seconds{job="api"}'

# Database connections
tars prom-query 'pg_stat_database_numbackends'

# Custom business metrics
tars prom-query 'orders_processed_total'
```

### 4. Capacity Planning

```bash
# Historical CPU trends
tars prom-query 'rate(container_cpu_usage_seconds_total{namespace="production"}[1h])'

# Memory growth
tars prom-query 'container_memory_working_set_bytes{namespace="production"}'
```

### 5. Incident Response

```bash
# Check alerts
tars prom-alerts

# View metrics for affected pods
tars prom-metrics --namespace production --pod failing-pod

# Compare with normal behavior
tars prom-query 'rate(http_requests_total{status="500"}[5m])'
```

## Integration with Existing Commands

Prometheus commands work seamlessly with existing TARS commands:

```bash
# Traditional workflow
tars triage                    # Identify issues
tars diagnose pod-name         # Deep dive

# Enhanced with Prometheus
tars triage                    # Identify issues
tars prom-alerts               # Check Prometheus alerts
tars prom-metrics --pod pod-name  # Get precise metrics
tars diagnose pod-name         # Deep dive with context
```

## Troubleshooting

### Connection Issues

```bash
# Check if Prometheus is accessible
curl http://your-prometheus-server:9090/-/healthy

# Verify URL is correct
echo $PROMETHEUS_URL

# Test with explicit URL
tars prom-check --url http://prometheus.example.com:9090
```

### No Metrics Found

**Possible causes:**
1. Prometheus not scraping your cluster
2. Wrong namespace
3. Metrics not exposed by containers

**Solutions:**
```bash
# Check available metrics
tars prom-query 'up'

# Verify namespace
kubectl get namespaces

# Check if metrics-server is running
kubectl get pods -n kube-system | grep metrics
```

### SSL/TLS Issues

The client uses `disable_ssl=True` by default for internal Prometheus instances. For production with SSL:

Modify `get_prometheus_client()` in `tars.py`:
```python
prom = PrometheusConnect(url=url, disable_ssl=False)
```

## Production Considerations

### 1. Authentication

For authenticated Prometheus:

```python
# Add to get_prometheus_client() function
prom = PrometheusConnect(
    url=url,
    headers={"Authorization": f"Bearer {token}"},
    disable_ssl=False
)
```

### 2. Timeouts

For slow queries, increase timeout:

```python
prom = PrometheusConnect(url=url, timeout=30)
```

### 3. Rate Limiting

Be mindful of query frequency to avoid overloading Prometheus.

### 4. Query Optimization

- Use appropriate time ranges
- Limit result sets
- Use recording rules for complex queries

## Technical Details

### Library Used
- **prometheus-api-client** (v0.7.0+)
- Official Python client for Prometheus HTTP API
- Supports all PromQL query types

### Metrics Queried

**CPU:**
```promql
rate(container_cpu_usage_seconds_total{namespace="X"}[5m])
```

**Memory:**
```promql
container_memory_working_set_bytes{namespace="X"}
```

**Network:**
```promql
rate(container_network_receive_bytes_total{namespace="X"}[5m])
```

**Alerts:**
```promql
ALERTS{alertstate="firing"}
```

## Future Enhancements

Potential additions:
- Historical trend visualization
- Alert rule management
- Recording rule suggestions
- Grafana dashboard links
- Metric correlation analysis
- Anomaly detection

## Support

For issues or questions:
- GitHub: https://github.com/orathore93-hue/tars-cli
- Email: orathore93@gmail.com

---

**Note:** Prometheus integration requires a running Prometheus server with access to your Kubernetes cluster metrics.
