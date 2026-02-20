# ✅ Added `stars init` Command

## New Command

```bash
stars init
```

## What It Does

1. **Shows Welcome Screen**
   - STARS ASCII banner
   - STARS robot art
   - Random greeting quote
   - Feature overview
   - Quick start guide

2. **Runs Setup Validation**
   - Checks GEMINI_API_KEY configuration
   - Validates Kubernetes connection
   - Checks Prometheus configuration (optional)
   - Shows setup status

## Usage Examples

### Just typing `stars`
```bash
$ stars
# Shows welcome screen only
```

### Initialize with setup
```bash
$ stars init
# Shows welcome screen + runs setup validation
```

### Get help
```bash
$ stars --help
# Shows all available commands
```

## Welcome Screen Output

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║  ███████╗.████████╗.  █████╗ .  ██████╗ .  ███████╗        ║
║  ██╔════╝.╚══██╔══╝. ██╔══██╗.  ██╔══██╗.  ██╔════╝        ║
║  ███████╗.   ██║   . ███████║.  ██████╔╝.  ███████╗        ║
║  ╚════██║.   ██║   . ██╔══██║.  ██╔══██╗.  ╚════██║        ║
║  ███████║.   ██║   . ██║  ██║.  ██║  ██║.  ███████║        ║
║  ╚══════╝.   ╚═╝   . ╚═╝  ╚═╝.  ╚═╝  ╚═╝.  ╚══════╝        ║
║                                                            ║
║    Site Technical Assistance & Reliability System        ║
╚════════════════════════════════════════════════════════════╝

STARS: Ready to analyze your Kubernetes cluster.
Your companion while you Kubersnaut.

╭─────────────────────────────────────────────────────────────╮
│  What I Do:                                                 │
│  • Monitor Kubernetes clusters (GKE/EKS) in real-time       │
│  • Detect issues: CrashLoops, OOM kills, pending pods       │
│  • AI-powered analysis with Gemini for troubleshooting      │
│  • On-call engineer toolkit for incident response           │
│  • Prevent downtime with proactive monitoring               │
│                                                             │
│  Quick Start:                                               │
│    stars init      - Initialize and setup STARS             │
│    stars health    - Check cluster health                   │
│    stars triage    - Quick incident overview                │
│    stars watch     - Real-time pod monitoring               │
│    stars spike     - Monitor resource spikes                │
╰─────────────────────────────────────────────────────────────╯
```

## Updated Quick Start

The welcome screen now shows:
- `stars init` as the first command (instead of `stars setup`)
- All commands use `stars` prefix (not `tars`)
- STARS branding throughout

## Benefits

1. **Better UX**: Single command to get started
2. **Clear Onboarding**: Welcome + setup in one step
3. **Consistent Branding**: All references use STARS
4. **Easy Discovery**: Just type `stars` to see what it does

## Commit

Pushed to: https://github.com/orathore93-hue/STARS-CLI
Commit: 0b1f5bb
