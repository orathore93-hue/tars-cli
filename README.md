# 🤖 STARS CLI - AI-Powered Kubernetes Monitoring & Incident Response Tool for SREs

> *"Site Technical Assistance & Reliability System"*

**STARS CLI** - Production-ready Kubernetes monitoring, incident management, and AI-powered troubleshooting tool for Site Reliability Engineers (SREs) and DevOps teams. Monitor clusters, detect issues, manage incidents, and reduce MTTR with intelligent automation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Security: Hardened](https://img.shields.io/badge/security-hardened-green.svg)](SECURITY.md)
[![Kubernetes](https://img.shields.io/badge/kubernetes-monitoring-326CE5.svg)](https://kubernetes.io/)
[![AI Powered](https://img.shields.io/badge/AI-Gemini-4285F4.svg)](https://ai.google.dev/)

**Keywords**: kubernetes monitoring, SRE tools, incident management, on-call engineer, kubernetes troubleshooting, AI-powered diagnostics, cluster monitoring, DevOps automation, kubernetes CLI, site reliability engineering, MTTR reduction, incident response, kubernetes security, RBAC enforcement, crashloop debugging

## 🎯 Why STARS CLI?

STARS is the ultimate **Kubernetes monitoring and incident response tool** built by SREs, for SREs. It's not just another kubectl wrapper - it's your intelligent incident response partner that:

- **Thinks like an SRE** - Prioritizes what matters during incidents
- **Saves time** - Automates repetitive diagnostic tasks  
- **Reduces MTTR** - AI-powered analysis and recommendations
- **Prevents incidents** - Proactive monitoring and alerting
- **Documents everything** - Auto-generates runbooks and incident reports
- **Security first** - RBAC enforcement, input validation, audit logging

## 🚀 Installation

### One-Line Install (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/orathore93-hue/STARS-CLI/main/install.sh | bash
```

**What happens during installation:**
1. Detects your OS (Linux/macOS/Windows) and architecture (amd64/arm64)
2. Downloads the latest release binary from GitHub
3. **Verifies SHA-256 checksum** to ensure binary integrity
4. Installs to `/usr/local/bin` (requires sudo)

**Security:** The installer automatically verifies cryptographic checksums before installation. If the binary has been tampered with or corrupted, installation will fail immediately with an error. This protects against man-in-the-middle attacks and compromised downloads.

### Alternative: Install via pip

```bash
pip install stars-cli
```

### Get Started

```bash
# Initialize and configure
stars init

# Verify RBAC permissions (recommended)
kubectl auth can-i --list

# Start monitoring
stars oncall
```

## 🔒 Security & Authentication

### Secure Credential Storage

STARS uses **OS-native encrypted storage** for sensitive credentials instead of plaintext files:

| Platform | Storage Backend | Encryption |
|----------|----------------|------------|
| **macOS** | Keychain | AES-256 |
| **Windows** | Credential Manager | DPAPI |
| **Linux** | Secret Service (GNOME/KDE) | Encrypted |

**First-time setup:**
```bash
# Store your Gemini API key securely
stars set-api-key
# Enter your API key when prompted (input hidden)
```

Your API key is encrypted and stored in your OS keychain. STARS will retrieve it automatically on subsequent runs.

**Important:** On first use, your OS may prompt you to grant STARS access to the keychain. This is standard behavior for secure CLI tools (similar to AWS CLI, Docker, or kubectl). Click "Allow" to proceed.

**For CI/CD environments:**
```bash
# Use environment variable for headless servers
export GEMINI_API_KEY='your-key-here'
```

STARS automatically falls back to environment variables when keychain access is unavailable.

## 🔐 Security & Privacy

**STARS is production-ready with enterprise-grade security:**

- ✅ **RBAC Enforcement** - All operations check permissions first
- ✅ **Input Validation** - K8s DNS-1123 compliant validation
- ✅ **Explicit Consent** - AI features require user opt-in
- ✅ **Data Redaction** - Secrets never leave your cluster
- ✅ **Audit Logging** - Complete trail in `~/.stars/audit.log`
- ✅ **Dry-Run Default** - Destructive operations safe by default

**Privacy Note**: AI features send anonymized cluster data to Google Gemini. See [Privacy Policy](docs/PRIVACY.md). Use `--no-ai` flag to opt-out.

**RBAC Note**: STARS requires specific Kubernetes RBAC permissions. See [RBAC Requirements](docs/RBAC_REQUIREMENTS.md) for details.

## 💪 Core Features for SREs

### 🚨 Incident Response

```bash
# Start incident tracking
stars incident start --title "API Gateway Down" --severity critical

# Quick triage - see all critical issues at once
stars triage

# On-call dashboard - everything you need in one view
stars oncall

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
pip install stars-cli
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

## 🎨 Features That Make STARS Unique

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

STARS follows security best practices:

- Uses kubectl config (no separate credentials)
- Read-only by default (except explicit operations)
- Dry-run mode for auto-remediation
- No data sent to external services (except Gemini API for AI features)
- API keys via environment variables only

## 🤝 Contributing

STARS is open source and welcomes contributions!

```bash
# Clone repo
git clone https://github.com/orathore93-hue/stars-cli.git
cd stars-cli

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

- **Issues**: [GitHub Issues](https://github.com/orathore93-hue/stars-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/orathore93-hue/stars-cli/discussions)
- **Email**: orathore93@gmail.com

## 🌟 Star History

If STARS helps you during incidents, consider giving it a star! ⭐

---

**Built with ❤️ by SREs, for SREs**

*"Humor setting: 90%. Let's monitor this cluster."* - TARS

---

## 🔍 Search Keywords

**Kubernetes Monitoring** | **SRE Tools** | **Incident Management** | **On-Call Engineering** | **Kubernetes Troubleshooting** | **AI-Powered Diagnostics** | **Cluster Monitoring** | **DevOps Automation** | **Kubernetes CLI** | **Site Reliability Engineering** | **MTTR Reduction** | **Incident Response** | **Kubernetes Security** | **RBAC Enforcement** | **CrashLoop Debugging** | **Blast Radius Analysis** | **Real-Time Monitoring** | **Kubernetes Observability** | **Production Kubernetes** | **Cloud Native Tools**

## 🎯 Use Cases

### For Site Reliability Engineers (SREs)
- **Incident Response**: Track incidents with timeline, log actions, generate reports
- **On-Call Management**: Quick triage, blast radius analysis, safe rollbacks
- **Proactive Monitoring**: Real-time alerts, spike detection, health checks
- **Security Auditing**: RBAC enforcement, security scans, compliance checks

### For DevOps Engineers
- **Deployment Safety**: Blast radius analysis before changes
- **Troubleshooting**: AI-powered diagnostics, crashloop fixes
- **Automation**: Auto-remediation, cleanup utilities
- **Documentation**: Auto-generated runbooks, incident reports

### For Platform Engineers
- **Cluster Management**: Multi-cluster support, namespace scanning
- **Resource Optimization**: Capacity planning, cost analysis
- **Security**: RBAC validation, secret scanning, audit logging
- **Observability**: Prometheus integration, custom metrics

## 🏆 Why Choose STARS CLI?

### vs kubectl
- ✅ AI-powered diagnostics
- ✅ Incident management built-in
- ✅ Blast radius analysis
- ✅ Security-first approach
- ✅ Human-friendly output

### vs k9s
- ✅ Incident timeline tracking
- ✅ AI troubleshooting
- ✅ RBAC enforcement
- ✅ Privacy controls
- ✅ Automation features

### vs Custom Scripts
- ✅ Production-ready
- ✅ Security hardened
- ✅ Well documented
- ✅ Active development
- ✅ Community support

## 📈 Performance & Scale

- **Fast**: Parallel queries, caching, optimized API calls
- **Scalable**: Handles large clusters (1000+ pods)
- **Reliable**: Retry logic, error handling, graceful degradation
- **Secure**: Input validation, RBAC checks, audit logging

## 🌟 Community & Support

- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Comprehensive guides and examples
- **Contributing**: Open to contributions (see CONTRIBUTING.md)
- **License**: MIT - Free and open source

## 📚 Documentation

### User Guides
- [SRE Commands Guide](docs/SRE_COMMANDS.md) - Complete command reference
- [Security & Privacy](docs/PRIVACY.md) - Privacy and data handling
- [RBAC Requirements](docs/RBAC_REQUIREMENTS.md) - Required Kubernetes permissions

### Developer Resources
- [Contributing Guidelines](docs/CONTRIBUTING.md) - How to contribute
- [Architecture](docs/ARCHITECTURE.md) - System design and architecture
- [Changelog](CHANGELOG.md) - Version history and changes

### Security Documentation
- [Security Policy](SECURITY.md) - Security features and best practices
- [Incident Response Plan](docs/INCIDENT_RESPONSE.md) - Security incident procedures
- [Production Readiness](docs/PRODUCTION_READINESS.md) - Deployment checklist
- [Next Steps](docs/NEXT_STEPS.md) - Development roadmap

## 🚀 Get Started Now

```bash
pip install stars-cli
stars init
stars health
```

**Start reducing MTTR and improving reliability today!**

---

**Made with ❤️ by SREs, for SREs**

**Star ⭐ this repo if you find it useful!**

