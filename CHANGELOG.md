# TARS CLI Changelog

## [Staging] - 2026-02-19

### 🎯 Major SRE Features Added

#### 1. Real-Time Alert Monitoring
```bash
tars alert --threshold-cpu 80 --threshold-memory 85 --interval 30
```
- Custom CPU/Memory thresholds
- Configurable check intervals
- Real-time notifications for pod issues
- Tracks restart counts and pod states

#### 2. Incident Runbook Generation
```bash
tars runbook <pod-name>
```
- Auto-generates incident response runbooks
- Includes diagnostic steps
- Provides remediation procedures
- Saves to file for team sharing
- Covers CrashLoopBackOff, OOMKilled, Pending scenarios

#### 3. Cluster Snapshot
```bash
tars snapshot
```
- Complete cluster state capture
- Saves pods, events, deployments, nodes
- Timestamped for historical analysis
- Perfect for post-mortems and audits
- Generates summary report

#### 4. Multi-Cluster Comparison
```bash
tars diff <context1> <context2>
```
- Compare two Kubernetes contexts
- Side-by-side metrics comparison
- Shows differences in pods, deployments, nodes
- Essential for multi-cluster SREs

### 🐛 Bug Fixes

- Fixed kubectl client naming conflict (CoreV1Api error)
- Updated Gemini model from `gemini-1.5-flash` to `gemini-2.0-flash`
- Resolved import shadowing issue

### 📚 Documentation

- Comprehensive README with real-world SRE scenarios
- Quick Reference Card for on-call engineers
- Command reference table
- Security best practices
- Installation and setup guide

### 🎨 Improvements

- Enhanced error messages
- Better progress indicators
- Improved table formatting
- More actionable recommendations

## Why These Features Matter for SREs

### Reduced MTTR (Mean Time To Recovery)
- `tars triage` + `tars diagnose` + `tars autofix` = Faster incident resolution
- Pre-generated runbooks eliminate decision paralysis
- AI-powered analysis provides immediate insights

### Better Documentation
- Automatic snapshot capture during incidents
- Runbooks generated on-demand
- Incident reports with AI analysis
- Historical data for post-mortems

### Proactive Monitoring
- Custom alerting prevents incidents
- Real-time spike detection
- Predictive analysis with `tars forecast`

### Multi-Cluster Management
- Compare production vs staging
- Unified monitoring across regions
- Context switching with health checks

## Next Steps

- [ ] Integration with PagerDuty/Slack
- [ ] Custom alert webhooks
- [ ] Historical trend analysis
- [ ] Cost optimization recommendations
- [ ] Automated rollback on failures

---

**Total Commands**: 54+
**Focus**: SRE & On-Call Engineers
**Philosophy**: Reduce toil, increase reliability
