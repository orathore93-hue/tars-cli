# STARS SRE Commands - Complete Guide

## 🚨 Incident Management

### Start an Incident
```bash
stars incident start --title "API Gateway Down" --severity critical
```

### Log Actions During Incident
```bash
stars incident log "Restarted api-gateway pods" --resource api-gateway
stars incident log "Checked database connections"
stars incident log "Scaled up to 5 replicas"
```

### Close Incident
```bash
stars incident close "Fixed by restarting pods and scaling up"
```

### List Recent Incidents
```bash
stars incident list
```

**Features:**
- ✅ Timeline tracking
- ✅ Affected resources tracking
- ✅ Duration calculation
- ✅ Saved to `~/.stars/incidents/`
- ✅ Generates incident summary

---

## 💥 Blast Radius Analysis

### Analyze Deployment Impact
```bash
stars blast-radius my-deployment -n production
```

**Shows:**
- Number of pods affected
- Connected services
- Replica count
- Estimated impact (low/medium/high)
- Recommendations for high-impact changes

**Use Before:**
- Rolling updates
- Scaling operations
- Configuration changes
- Deletions

---

## 🔧 Quick Fixes

### Fix CrashLoop Backoff
```bash
# Analyze and suggest fixes
stars fix-crashloop my-pod -n production

# Common fixes detected:
# - OOM issues → Increase memory
# - Connection refused → Check dependencies
# - Permission denied → Check RBAC
# - File not found → Check volume mounts
```

### Clear Evicted Pods
```bash
# Dry run (default)
stars clear-evicted -n production

# Actually delete
stars clear-evicted -n production --apply
```

---

## ⏮️ Safe Rollback

### Rollback Deployment
```bash
# Dry run with blast radius analysis
stars rollback my-deployment -n production

# Execute rollback
stars rollback my-deployment -n production --apply

# Rollback to specific revision
stars rollback my-deployment -n production --revision 3 --apply
```

**Safety Features:**
- ✅ Shows blast radius before rollback
- ✅ Requires confirmation
- ✅ Dry-run by default
- ✅ RBAC permission checks

---

## 📊 On-Call Reports

### Generate Shift Report
```bash
stars oncall-report --hours 8
```

**Includes:**
- Recent incidents
- Pod restarts (coming soon)
- Failed deployments (coming soon)
- Resource alerts (coming soon)

---

## 🔒 Security Scanning

### Quick Security Audit
```bash
# Full scan
stars security-scan -n production

# Quick scan
stars security-scan -n production --quick
```

**Checks:**
- ✅ Privileged containers
- ✅ Host network usage
- ✅ Missing resource limits
- ✅ Security context issues

---

## 🎯 Real-World Workflows

### Incident Response Workflow
```bash
# 1. Start incident
stars incident start --title "High Error Rate" --severity high

# 2. Investigate
stars health -n production
stars diagnose failing-pod -n production

# 3. Log actions
stars incident log "Identified memory leak in api-service"
stars incident log "Restarting pods" --resource api-service

# 4. Fix
stars restart deployment/api-service -n production

# 5. Verify
stars watch -n production

# 6. Close incident
stars incident close "Fixed memory leak, restarted pods, monitoring"
```

### Safe Deployment Workflow
```bash
# 1. Check blast radius
stars blast-radius my-app -n production

# 2. If high impact, proceed carefully
stars scale my-app 10 -n production --dry-run

# 3. Apply change
stars scale my-app 10 -n production

# 4. Monitor
stars watch -n production

# 5. Rollback if needed
stars rollback my-app -n production --apply
```

### Cleanup Workflow
```bash
# 1. Find evicted pods
stars clear-evicted -n production

# 2. Review what will be deleted
# (dry-run shows list)

# 3. Clean up
stars clear-evicted -n production --apply

# 4. Verify
stars pods -n production
```

---

## 🛡️ Security Features

All commands include:

1. **Input Validation**
   - Resource names validated against K8s DNS-1123
   - Namespace validation
   - Command argument sanitization

2. **RBAC Enforcement**
   - Permission checks before destructive operations
   - Clear error messages

3. **Audit Logging**
   - All operations logged to `~/.stars/audit.log`
   - Incident timeline tracking

4. **Dry-Run Mode**
   - Default for destructive operations
   - Must explicitly use `--apply`

5. **Confirmation Prompts**
   - High-impact operations require confirmation
   - Blast radius shown before changes

---

## 📝 Command Reference

| Command | Purpose | Safety |
|---------|---------|--------|
| `incident start` | Start incident tracking | Safe |
| `incident log` | Log incident actions | Safe |
| `incident close` | Close incident | Safe |
| `blast-radius` | Analyze change impact | Safe |
| `fix-crashloop` | Suggest crashloop fixes | Safe |
| `clear-evicted` | Remove evicted pods | Dry-run default |
| `rollback` | Rollback deployment | Dry-run default |
| `oncall-report` | Generate shift report | Safe |
| `security-scan` | Security audit | Safe |

---

## 🎓 Best Practices

1. **Always check blast radius** before major changes
2. **Use dry-run mode** first for destructive operations
3. **Track incidents** for postmortem analysis
4. **Run security scans** regularly
5. **Generate on-call reports** at shift end
6. **Log all actions** during incidents

---

## 🔗 Related Commands

- `stars health` - Cluster health check
- `stars triage` - Quick incident overview
- `stars watch` - Real-time monitoring
- `stars diagnose` - Pod diagnostics
- `stars privacy` - AI consent management

---

## 📚 More Information

- Full documentation: `stars --help`
- Incident files: `~/.stars/incidents/`
- Audit log: `~/.stars/audit.log`
- Privacy policy: `docs/PRIVACY.md`
- RBAC requirements: `docs/RBAC_REQUIREMENTS.md`
