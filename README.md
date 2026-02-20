# 🤖 TARS CLI - The SRE's Best Friend

> *"This is no time for caution."* - TARS

**T**echnical **A**ssistance & **R**eliability **S**ystem - Your AI-powered Kubernetes companion for on-call engineers and SREs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎯 Why TARS?

TARS is built by SREs, for SREs. It's not just another kubectl wrapper - it's your intelligent incident response partner that:

- **Thinks like an SRE** - Prioritizes what matters during incidents
- **Saves time** - Automates repetitive diagnostic tasks
- **Reduces MTTR** - AI-powered analysis and recommendations
- **Prevents incidents** - Proactive monitoring and alerting
- **Documents everything** - Auto-generates runbooks and incident reports

## 🚀 Quick Start

```bash
# Install
pip install tars-cli

# Setup (one-time)
export GEMINI_API_KEY='your-key'  # Get free key at https://makersuite.google.com
tars setup

# Start monitoring
tars oncall
```

## 💪 Core Features for SREs

### 🚨 Incident Response

```bash
# Quick triage - see all critical issues at once
tars triage

# On-call dashboard - everything you need in one view
tars oncall

# Deep dive into a problematic pod
tars diagnose <pod-name>

# Generate incident runbook
tars runbook <pod-name>

# AI-powered incident report
tars incident-report
```

### 📊 Real-Time Monitoring

```bash
# Live pod monitoring
tars watch

# Resource spike detection
tars spike

# Custom alerting with thresholds
tars alert --threshold-cpu 80 --threshold-memory 85 --interval 30

# Cluster health pulse
tars pulse

# Timeline of recent events
tars timeline
```

### 🔧 Auto-Remediation

```bash
# Auto-fix common issues (dry-run by default)
tars autofix

# Apply fixes automatically
tars autofix --no-dry-run

# AI-powered smart scaling
tars smart-scale <deployment>

# Quick restart
tars restart <pod-name>
```

### 📸 Incident Documentation

```bash
# Take complete cluster snapshot
tars snapshot

# Generate runbook for any pod
tars runbook <pod-name>

# Create incident report with AI analysis
tars incident-report

# Show cluster story - what happened today?
tars story
```

### 🔍 Advanced Analysis

```bash
# Blast radius analysis
tars blast <pod-name>

# Predict future issues
tars forecast

# Chaos engineering insights
tars chaos

# Compare two clusters
tars diff <context1> <context2>
```

### 📈 SRE Metrics

```bash
# Service Level Objectives
tars slo

# Service Level Indicators
tars sli

# Resource usage comparison
tars compare

# Top resource consumers
tars top
```

## 🎓 Real-World SRE Scenarios

### Scenario 1: 3 AM Page - Pod CrashLooping

```bash
# Quick triage
tars triage
# Shows: CrashLoopBackOff detected in payment-service

# Deep diagnosis
tars diagnose payment-service
# AI analysis: "OOMKilled - memory limit too low"

# Check blast radius
tars blast payment-service
# Shows: Affects checkout flow, 3 dependent services

# Auto-fix
tars autofix
# Recommendation: Increase memory limit to 512Mi

# Generate incident report
tars incident-report
```

### Scenario 2: Proactive Monitoring

```bash
# Start alert monitoring
tars alert --threshold-cpu 80 --threshold-memory 85

# In another terminal, watch for spikes
tars spike

# Check SLO compliance
tars slo
```

### Scenario 3: Capacity Planning

```bash
# Take snapshot for analysis
tars snapshot

# Compare production vs staging
tars diff prod-context staging-context

# Forecast future issues
tars forecast
```

### Scenario 4: Multi-Cluster Management

```bash
# Compare clusters
tars diff us-east-1 us-west-2

# Switch context and check health
tars context
tars health
```

### Scenario 5: Prometheus Metrics Analysis

```bash
# Check Prometheus connection
tars prom-check --url http://prometheus.example.com:9090

# View metrics dashboard
tars prom-dashboard --namespace production

# Check specific pod metrics
tars prom-metrics --namespace production --pod api-server-xyz

# Monitor active alerts
tars prom-alerts

# Run custom PromQL queries
tars prom-query 'rate(http_requests_total[5m])'
tars prom-query 'container_memory_usage_bytes{namespace="production"}'
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- kubectl configured
- Kubernetes cluster access (GKE, EKS, or any K8s cluster)

### Install

```bash
pip install tars-cli
```

### Configure

```bash
# Set Gemini API key (for AI features)
export GEMINI_API_KEY='your-key'

# Set Prometheus URL (for metrics features)
export PROMETHEUS_URL='http://localhost:9090'

# Verify setup
tars setup

# Check Prometheus connection
tars prom-check
```

### Optional: Shell Completion

```bash
# Bash
tars --install-completion bash

# Zsh
tars --install-completion zsh
```

## 📋 Command Reference

### Essential Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `tars oncall` | On-call dashboard | Start of shift |
| `tars triage` | Quick incident overview | During incidents |
| `tars health` | Cluster health check | Regular monitoring |
| `tars diagnose <pod>` | Deep pod analysis | Troubleshooting |
| `tars alert` | Real-time alerting | Proactive monitoring |

### Monitoring

| Command | Description |
|---------|-------------|
| `tars watch` | Live pod monitoring |
| `tars spike` | Resource spike detection |
| `tars pulse` | Cluster heartbeat |
| `tars timeline` | Recent events |
| `tars metrics` | Resource usage |
| `tars top` | Top consumers |
| `tars resources <ns>` | All resources in namespace |

### Prometheus Integration

| Command | Description |
|---------|-------------|
| `tars prom-check` | Check Prometheus connection |
| `tars prom-metrics` | Show pod metrics from Prometheus |
| `tars prom-alerts` | Show active Prometheus alerts |
| `tars prom-query <query>` | Run custom PromQL query |
| `tars prom-dashboard` | Metrics dashboard |

### Troubleshooting

| Command | Description |
|---------|-------------|
| `tars errors` | Show all errors |
| `tars crashloop` | CrashLoop detection |
| `tars oom` | OOM killed pods |
| `tars pending` | Pending pods analysis |
| `tars logs <pod>` | AI-summarized logs |
| `tars events` | Cluster events |

### Operations

| Command | Description |
|---------|-------------|
| `tars restart <pod>` | Restart pod |
| `tars scale <dep> <n>` | Scale deployment |
| `tars rollback <dep>` | Rollback deployment |
| `tars drain <node>` | Drain node |
| `tars autofix` | Auto-remediation |

### Analysis

| Command | Description |
|---------|-------------|
| `tars analyze` | AI cluster analysis |
| `tars blast <pod>` | Blast radius |
| `tars forecast` | Predict issues |
| `tars chaos` | Chaos insights |
| `tars compare` | Compare namespaces |

### Documentation

| Command | Description |
|---------|-------------|
| `tars snapshot` | Cluster snapshot |
| `tars runbook <pod>` | Generate runbook |
| `tars incident-report` | Incident report |
| `tars story` | Cluster story |

### Multi-Cluster

| Command | Description |
|---------|-------------|
| `tars context` | Switch contexts |
| `tars diff <c1> <c2>` | Compare clusters |

## 🎨 Features That Make TARS Unique

### 1. AI-Powered Analysis
- Uses Google Gemini for intelligent insights
- Natural language explanations
- Actionable recommendations

### 2. SRE-First Design
- Commands designed for incident response
- Prioritizes critical information
- Reduces cognitive load during incidents

### 3. Auto-Remediation
- Safe dry-run mode by default
- Smart scaling decisions
- Common issue detection and fixes

### 4. Comprehensive Documentation
- Auto-generated runbooks
- Incident reports with AI analysis
- Cluster snapshots for post-mortems

### 5. Real-Time Monitoring
- Custom alerting thresholds
- Live dashboards
- Resource spike detection

### 6. Multi-Cluster Support
- Context switching
- Cluster comparison
- Unified monitoring

## 🔒 Security Best Practices

TARS follows security best practices:

- Uses kubectl config (no separate credentials)
- Read-only by default (except explicit operations)
- Dry-run mode for auto-remediation
- No data sent to external services (except Gemini API for AI features)
- API keys via environment variables only

## 🤝 Contributing

TARS is open source and welcomes contributions!

```bash
# Clone repo
git clone https://github.com/orathore93-hue/tars-cli.git
cd tars-cli

# Install in development mode
pip install -e .

# Make changes and test
tars <command>
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- Built for the SRE community
- Powered by Google Gemini AI

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/orathore93-hue/tars-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/orathore93-hue/tars-cli/discussions)
- **Email**: orathore93@gmail.com

## 🌟 Star History

If TARS helps you during incidents, consider giving it a star! ⭐

---

**Built with ❤️ by SREs, for SREs**

*"Humor setting: 90%. Let's monitor this cluster."* - TARS
