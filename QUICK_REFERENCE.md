# 🚨 TARS Quick Reference Card for On-Call Engineers

## 🔥 Emergency Response (First 60 Seconds)

```bash
tars triage          # What's broken?
tars oncall          # Full dashboard
tars health          # Cluster status
```

## 🔍 Investigation (Next 5 Minutes)

```bash
tars diagnose <pod>  # Deep dive
tars logs <pod>      # AI-summarized logs
tars events          # Recent events
tars timeline        # Last 30 minutes
```

## 🔧 Quick Fixes

```bash
tars autofix         # Auto-remediate (dry-run)
tars restart <pod>   # Restart pod
tars scale <dep> <n> # Scale deployment
tars rollback <dep>  # Rollback
```

## 📊 Monitoring

```bash
tars watch           # Live monitoring
tars spike           # Resource spikes
tars alert           # Custom alerts
tars metrics         # Resource usage
tars resources <ns>  # All resources in namespace
```

## 📈 Prometheus Metrics

```bash
tars prom-check      # Check connection
tars prom-metrics    # Pod metrics
tars prom-alerts     # Active alerts
tars prom-dashboard  # Metrics dashboard
tars prom-query "query" # Custom PromQL
```

## 📝 Documentation

```bash
tars snapshot        # Cluster snapshot
tars runbook <pod>   # Generate runbook
tars incident-report # AI incident report
```

## 🎯 Common Scenarios

### CrashLoopBackOff
```bash
tars crashloop
tars diagnose <pod>
tars logs <pod>
tars autofix
```

### OOMKilled
```bash
tars oom
tars metrics
tars smart-scale <deployment>
```

### High CPU/Memory
```bash
tars spike
tars top
tars scale <deployment> <replicas>
```

### Pending Pods
```bash
tars pending
tars nodes
tars events
```

## 💡 Pro Tips

1. **Start every shift with**: `tars oncall`
2. **During incidents**: `tars triage` → `tars diagnose` → `tars autofix`
3. **For documentation**: `tars snapshot` + `tars incident-report`
4. **Proactive monitoring**: `tars alert --threshold-cpu 80`
5. **Multi-cluster**: `tars diff prod staging`

## 🔗 Keyboard Shortcuts

- `Ctrl+C` - Stop any running command
- `tars god` - Show all power commands
- `tars quote` - Get TARS motivation

## 📞 Escalation Checklist

- [ ] `tars triage` - Identify issue
- [ ] `tars blast <pod>` - Check impact
- [ ] `tars snapshot` - Preserve state
- [ ] `tars incident-report` - Document
- [ ] `tars runbook <pod>` - Share with team

---

**Print this and keep it near your desk!** 🖨️
