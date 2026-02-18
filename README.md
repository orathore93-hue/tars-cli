# T.A.R.S 🤖

<div align="center">

```
████████╗     █████╗     ██████╗     ███████╗
╚══██╔══╝    ██╔══██╗    ██╔══██╗    ██╔════╝
   ██║       ███████║    ██████╔╝    ███████╗
   ██║   ██  ██╔══██║    ██╔══██╗    ╚════██║
   ██║   ██  ██║  ██║    ██║  ██║    ███████║
   ╚═╝   ╚═  ╚═╝  ╚═╝    ╚═╝  ╚═╝    ╚══════╝
```

### **Technical Assistance & Reliability System**

*"Humor setting: 90%. Let's do this."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-compatible-326CE5.svg)](https://kubernetes.io/)
[![AI Powered](https://img.shields.io/badge/AI-Gemini-orange.svg)](https://ai.google.dev/)

**Your sarcastic AI companion for Kubernetes monitoring** 🚀

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Demo](#-demo) • [Contributing](#-contributing)

</div>

---

## 🎬 What Makes T.A.R.S Different?

T.A.R.S isn't just another monitoring tool. It combines:
- 🧠 **AI-Powered Analysis** - Gemini integration for intelligent troubleshooting
- 😏 **Personality** - Sarcastic, witty responses that make debugging less painful
- ⚡ **Real-Time** - Live monitoring with instant spike detection
- 🎯 **On-Call Ready** - Built for 3 AM incidents when you need answers fast
- 🎨 **Beautiful CLI** - Rich terminal UI that doesn't look like 1995


## ✨ Features

<table>
<tr>
<td width="50%">

### 🔍 Smart Monitoring
- Real-time pod health tracking
- Automatic issue detection
- CrashLoop & OOM detection
- Resource spike alerts
- Multi-namespace support

</td>
<td width="50%">

### 🧠 AI-Powered
- Gemini integration
- Intelligent log analysis
- Root cause suggestions
- TARS personality responses
- Context-aware troubleshooting

</td>
</tr>
<tr>
<td width="50%">

### ⚡ Developer Experience
- Beautiful terminal UI
- Color-coded alerts
- Live dashboards
- One-command setup
- Zero config needed

</td>
<td width="50%">

### ☁️ Cloud Native
- GKE support
- EKS support
- Any K8s cluster
- kubectl integration
- Metrics API support

</td>
</tr>
</table>

---

## 🚀 Installation

```bash
pip install git+https://github.com/orathore93-hue/tars-cli.git
```

**That's it.** No complex setup, no YAML hell, no configuration files.

---

## ⚡ Quick Start

### 1️⃣ Get Your Free API Key
```bash
# Visit: https://makersuite.google.com/app/apikey
export GEMINI_API_KEY="your-key-here"
```

### 2️⃣ Verify Setup
```bash
tars setup
```

### 3️⃣ Start Monitoring
```bash
tars health      # Cluster health overview
tars watch       # Live pod monitoring
tars triage      # Incident response mode
tars spike       # Resource spike detection
```

---

## 🎮 Demo

### Health Check
```bash
$ tars health
TARS: Running health diagnostics...

┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric       ┃ Value     ┃ Status ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━┩
│ Nodes        │ 3 total   │ ✓      │
│ Pods Running │ 47/47     │ ✓      │
│ Failed Pods  │ 0         │ ✓      │
└──────────────┴───────────┴────────┘

TARS: Cluster health is optimal. I'd give it a 95% rating.
```

### Spike Detection
```bash
$ tars spike
TARS: Monitoring for spikes...

[14:23:45]
🔥 CPU SPIKE: api-server-7d9f: 2.341 cores
🔥 MEMORY SPIKE: redis-cache-4k2: 1847Mi
```

### AI Analysis
```bash
$ tars analyze
TARS: Analyzing cluster...

╭─ TARS Analysis ─────────────────────────────╮
│ Well, Developer, looks like your api-server    │
│ is having an existential crisis. The pod    │
│ is CrashLooping because it can't find its   │
│ database connection. Check your secrets.    │
│                                              │
│ Recommendation: Verify DB_HOST env var.     │
╰──────────────────────────────────────────────╯
```

---

## 🎯 Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `tars setup` | Verify installation | First-time setup |
| `tars health` | Cluster health check | Daily monitoring |
| `tars watch` | Live pod monitoring | Real-time tracking |
| `tars triage` | Incident overview | On-call response |
| `tars spike` | Resource spike alerts | Performance issues |
| `tars analyze` | AI troubleshooting | Root cause analysis |
| `tars logs <pod>` | AI log analysis | Debugging |
| `tars diagnose <pod>` | Deep pod inspection | Detailed investigation |

---

## 🎨 Why Developers Love T.A.R.S

> *"Finally, a monitoring tool that doesn't make me want to cry at 3 AM"* - Every DevOps Engineer

- **No YAML Configuration** - Just install and run
- **Personality** - Makes debugging actually enjoyable
- **AI-Powered** - Get answers, not just data
- **Beautiful UI** - Terminal output that doesn't hurt your eyes
- **Fast** - Real-time monitoring without lag
- **Free** - Uses Gemini's free tier

---


## 🛠️ Advanced Usage

### Custom Spike Thresholds
```bash
tars spike --cpu-threshold 2.0 --memory-threshold 2000 --interval 5
```

### Monitor Specific Namespace
```bash
tars watch --namespace production
tars triage --namespace staging
```

### AI-Powered Log Analysis
```bash
tars logs my-failing-pod --namespace default
```

---

## 🤝 Contributing

We love contributions! T.A.R.S is built by developers, for developers.

**Ways to contribute:**
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit PRs
- 📖 Improve docs
- ⭐ Star the repo

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 🎭 The TARS Personality

T.A.R.S responds with personality, making debugging less painful:

```
TARS: "This is no time for caution."
TARS: "Humor setting at 90%. Cluster monitoring initiated."
TARS: "All systems operational. Sarcasm levels optimal."
```

T.A.R.S brings wit and intelligence to your terminal.

---

## 📊 Roadmap

- [ ] Slack/Discord notifications
- [ ] Historical metrics tracking
- [ ] Custom alert rules
- [ ] Web dashboard
- [ ] Multi-cluster support
- [ ] Prometheus integration
- [ ] Cost optimization suggestions
- [ ] Auto-remediation actions

---

## 🏆 Built With

- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [Kubernetes Python Client](https://github.com/kubernetes-client/python) - K8s API
- [Google Gemini](https://ai.google.dev/) - AI analysis

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Omer Rathore**
- GitHub: [@orathore93-hue](https://github.com/orathore93-hue)
- Project: [T.A.R.S](https://github.com/orathore93-hue/tars-cli)

---

## ⭐ Show Your Support

If T.A.R.S helped you debug at 3 AM, give it a ⭐!

### 💚 Support Development

T.A.R.S is free and open source. If you find it useful, consider supporting its development:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/omerrathore)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-pink?style=for-the-badge&logo=github)](https://github.com/sponsors/orathore93-hue)

Your support helps:
- 🚀 Add new features
- 🐛 Fix bugs faster
- 📚 Improve documentation
- ☁️ Cover API costs
- ⏰ Dedicate more time to the project

```bash
# Share with your team
git clone https://github.com/orathore93-hue/tars-cli.git
```

---

<div align="center">

**"Monitoring your cluster with intelligence and wit."** - T.A.R.S

Made with 💚 for the DevOps community

</div>
