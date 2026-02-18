# T.A.R.S 🤖

**Technical Assistance & Reliability System**

AI-powered Kubernetes cluster monitoring and troubleshooting tool for on-call engineers.

```
████████╗     █████╗     ██████╗     ███████╗
╚══██╔══╝    ██╔══██╗    ██╔══██╗    ██╔════╝
   ██║       ███████║    ██████╔╝    ███████╗
   ██║   ██  ██╔══██║    ██╔══██╗    ╚════██║
   ██║   ██  ██║  ██║    ██║  ██║    ███████║
   ╚═╝   ╚═  ╚═╝  ╚═╝    ╚═╝  ╚═╝    ╚══════╝
```

## Features

- 🔍 **Real-time Monitoring** - Watch pods, detect crashes, OOM kills, and pending states
- 🧠 **AI-Powered Analysis** - Gemini integration for intelligent troubleshooting
- 🚨 **Incident Triage** - Quick overview of cluster issues
- 📊 **Resource Spike Detection** - Monitor CPU/memory anomalies
- ☁️ **Multi-Cloud Support** - Works with GKE, EKS, and any Kubernetes cluster
- 🎯 **On-Call Toolkit** - Built for incident response

## Installation

### From PyPI (coming soon)
```bash
pip install tars-cli
```

### From GitHub
```bash
pip install git+https://github.com/orathore93-hue/tars-cli.git
```

### From Source
```bash
git clone https://github.com/orathore93-hue/tars-cli.git
cd tars-cli
pip install -e .
```

## Quick Start

```bash
# Check cluster health
tars health

# Quick incident overview
tars triage

# Real-time pod monitoring
tars watch

# Monitor resource spikes
tars spike

# Get help
tars --help
```

## Configuration

Set your Gemini API key:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

Get a free API key at: https://makersuite.google.com/app/apikey

## Requirements

- Python 3.8+
- kubectl configured with cluster access
- Gemini API key (free tier available)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Author

Created by Omer Rathore

---

*"Humor setting: 90%. Let's do this."* - T.A.R.S
