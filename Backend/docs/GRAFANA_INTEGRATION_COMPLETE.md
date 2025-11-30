# Grafana Integration - ✅ COMPLETE

**Status:** 🎉 **Successfully Deployed and Running**

**Access URL:** http://localhost:3001
**Default Credentials:** admin / admin (change on first login)

---

## What Has Been Set Up

### 1. Docker Service ✅
- **Service Name:** `grafana`
- **Container:** `test-hirehub-adaptive-grafana`
- **Image:** `grafana/grafana:latest`
- **Port:** 3001 → 3000 (Grafana UI)
- **Status:** Running and healthy
- **Health Check:** http://localhost:3001/api/health

### 2. Auto-Provisioning ✅
All configuration is automated via provisioning files:

**Datasource Configuration:**
- **File:** `grafana/datasources/hirehub-api.yaml`
- **Type:** Infinity (REST API datasource)
- **URL:** `http://api:8000`
- **Auto-loaded:** Yes

**Dashboard Configuration:**
- **File:** `grafana/dashboards/dashboard.yaml`
- **Provider:** HireHub Dashboards
- **Update Interval:** 10 seconds
- **Auto-loaded:** Yes

**Dashboard JSON:**
- **File:** `grafana/dashboards/hirehub-metrics.json`
- **Panels:** 8 panels (performance, cost, quality, health)
- **Refresh Rate:** 10 seconds
- **Time Range:** Last 1 hour

### 3. Infinity Plugin ✅
- **Plugin ID:** `yesoreyeram-infinity-datasource`
- **Version:** Latest
- **Installation:** Automatic via `GF_INSTALL_PLUGINS` env var
- **Status:** Installed and ready

### 4. Data Volume ✅
- **Volume Name:** `grafana_data`
- **Mount Point:** `/var/lib/grafana`
- **Persistence:** All dashboards, datasources, and settings persist across restarts

---

## Dashboard Panels (8 Total)

### Performance Monitoring
1. **P95 Latency (Last Hour)** - Time series chart
   - Shows 95th percentile response time
   - Thresholds: Green (<2s), Yellow (2-3s), Red (>3s)
   - Source: `/api/metrics/performance?time_window_minutes=60`

2. **Error Rate** - Time series chart
   - Tracks system reliability
   - Thresholds: Green (<1%), Yellow (1-5%), Red (>5%)
   - Source: `/api/metrics/performance?time_window_minutes=60`

### Cost Tracking
3. **Hourly Cost** - Stat panel
   - Current spend rate in USD
   - Format: Currency with 4 decimal places
   - Source: `/api/metrics/costs?time_window_minutes=60`

4. **Monthly Cost Projection** - Stat panel
   - Estimated monthly bill
   - Format: Currency with 2 decimal places
   - Source: `/api/metrics/costs?time_window_minutes=1440`

### Quality Metrics
5. **Average Quality Score** - Stat panel
   - Answer quality on 0-10 scale
   - Format: Number with 1 decimal
   - Source: `/api/metrics/quality?time_window_minutes=60`

6. **Refinement Rate** - Gauge panel
   - Percentage of answers needing refinement
   - Thresholds: Green (<30%), Yellow (30-50%), Red (>50%)
   - Source: `/api/metrics/quality?time_window_minutes=60`

### System Health
7. **Cache Hit Rate** - Gauge panel
   - Prompt cache efficiency (0-100%)
   - Thresholds: Green (>80%), Yellow (70-80%), Red (<70%)
   - Source: `/api/metrics/cache`

8. **System Health** - Table panel
   - Component status (Redis, Qdrant, LLM)
   - Format: Table with status indicators
   - Source: `/api/metrics/health`

---

## Files Created/Modified

### New Files (5)
1. `grafana/datasources/hirehub-api.yaml` - Datasource configuration
2. `grafana/dashboards/dashboard.yaml` - Dashboard provider config
3. `grafana/dashboards/hirehub-metrics.json` - Dashboard JSON definition
4. `GRAFANA_SETUP_GUIDE.md` - Detailed setup documentation
5. `GRAFANA_QUICKSTART.md` - Quick start guide (5 minutes)

### Modified Files (1)
1. `docker-compose.yml` - Added Grafana service + grafana_data volume

---

## Quick Start (3 Steps)

### Step 1: Access Grafana
```bash
# Open browser
open http://localhost:3001  # macOS
# or visit http://localhost:3001 in any browser
```

### Step 2: Login
- **Username:** `admin`
- **Password:** `admin`
- Change password when prompted

### Step 3: View Dashboard
1. Click **Dashboards** (☰ menu) → **Browse**
2. Click **"HireHub Metrics Dashboard"**
3. Done! Dashboard auto-refreshes every 10 seconds

---

## Verification Checklist

✅ **Grafana Service:** Running on port 3001
✅ **Health Endpoint:** http://localhost:3001/api/health responds
✅ **Infinity Plugin:** Installed automatically
✅ **Datasource:** Auto-configured via provisioning
✅ **Dashboard:** Auto-loaded via provisioning
✅ **Data Volume:** Persistent storage created
✅ **API Connection:** Grafana → API (http://api:8000)
✅ **Auto-refresh:** 10 second refresh rate

---

## Testing the Integration

### Test 1: Verify API Connection
```bash
# Check API metrics endpoint
curl http://localhost:8001/api/metrics/dashboard | jq .
```

**Expected:** JSON response with performance, costs, quality, cache, health

### Test 2: Generate Test Data
```bash
# Run a few test requests to populate metrics
for i in {1..5}; do
  curl -X POST http://localhost:8001/api/adaptive-questions/start \
    -H "Content-Type: application/json" \
    -d "{\"gap_info\": {\"title\": \"Test $i\", \"priority\": \"MEDIUM\"}}"
  sleep 1
done
```

**Expected:** Metrics appear in Grafana dashboard within 10 seconds

### Test 3: Verify Datasource
1. In Grafana: **Configuration** → **Data Sources**
2. Click **"HireHub Metrics API"**
3. Click **"Save & Test"**

**Expected:** "Data source is working" message

---

## Common Commands

```bash
# Start Grafana
docker-compose up -d grafana

# View logs
docker-compose logs -f grafana

# Restart Grafana (to reload config)
docker-compose restart grafana

# Stop Grafana
docker-compose stop grafana

# Check status
docker-compose ps grafana

# Access Grafana CLI (inside container)
docker exec -it test-hirehub-adaptive-grafana grafana-cli --help

# Export dashboard JSON
# In Grafana: Dashboard Settings → JSON Model → Copy
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Browser (localhost:3001)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Grafana Container (port 3000)                  │
│  • Dashboard: HireHub Metrics Dashboard                     │
│  • Datasource: HireHub Metrics API (Infinity)               │
│  • Refresh: Every 10 seconds                                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼ HTTP Requests
┌─────────────────────────────────────────────────────────────┐
│              API Container (http://api:8000)                │
│  • GET /api/metrics/dashboard                               │
│  • GET /api/metrics/performance                             │
│  • GET /api/metrics/costs                                   │
│  • GET /api/metrics/quality                                 │
│  • GET /api/metrics/cache                                   │
│  • GET /api/metrics/health                                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              MetricsCollector (In-Memory)                   │
│  • Performance metrics (latency, errors)                    │
│  • Cost tracking (LLM tokens, cache hits)                   │
│  • Quality scores (evaluations, refinements)                │
│  • Cache statistics (hit rates)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Next Steps (Optional)

### 1. Set Up Alerts
Configure alerts for critical thresholds:
- High P95 latency (>3s)
- High error rate (>5%)
- Low cache hit rate (<70%)
- High monthly cost projection (>$50)

**Guide:** See `GRAFANA_SETUP_GUIDE.md` section "Step 6: Configure Alerts"

### 2. Add More Panels
Customize dashboard with additional metrics:
- Cache breakdown (L1 vs L2 vs Prompt)
- Cost by operation (breakdown by workflow node)
- Quality trends over time
- Throughput (requests per second)

### 3. Create User Accounts
Set up multi-user access:
1. **Configuration** → **Users** → **Invite**
2. Assign roles: Admin, Editor, Viewer
3. Configure team permissions

### 4. Enable Notifications
Set up alert notification channels:
- Email (SMTP configuration)
- Slack (webhook URL)
- PagerDuty (integration key)
- Discord, Teams, etc.

**Guide:** See `GRAFANA_SETUP_GUIDE.md` section "Configure Alerts"

### 5. Backup & Export
Save dashboard configurations:
```bash
# Export dashboard JSON
# Dashboard Settings → JSON Model → Copy → Save to file

# Export datasource config (already in grafana/datasources/)
# Configuration → Data Sources → Export

# Backup entire Grafana data volume
docker run --rm -v test-hirehub-adaptive_grafana_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/grafana-backup.tar.gz /data
```

---

## Production Checklist

Before deploying to production:

- [ ] Change admin password (default: admin)
- [ ] Set `GF_SECURITY_ADMIN_PASSWORD` in `.env`
- [ ] Enable HTTPS (reverse proxy or SSL cert)
- [ ] Configure external auth (LDAP, OAuth, SAML)
- [ ] Set up alert notification channels
- [ ] Restrict Grafana port to internal network
- [ ] Configure user roles and permissions
- [ ] Set up automated backups
- [ ] Enable audit logging
- [ ] Configure session timeout
- [ ] Set up high availability (multiple instances)
- [ ] Configure database backend (PostgreSQL, MySQL)

---

## Troubleshooting

### Issue: Dashboard not appearing
**Solution:**
1. Wait 10 seconds (provisioning interval)
2. Refresh browser
3. Check logs: `docker-compose logs grafana | grep -i dashboard`

### Issue: "Cannot connect to data source"
**Solution:**
1. Verify API is running: `docker-compose ps api`
2. Check API health: `curl http://localhost:8001/api/metrics/health`
3. Verify datasource URL in Grafana: `http://api:8000`

### Issue: Panels show "No data"
**Solution:**
1. Generate test data (see "Testing the Integration" above)
2. Adjust time range to "Last 15 minutes"
3. Check API response: `curl http://localhost:8001/api/metrics/dashboard`

### Issue: Infinity plugin not found
**Solution:**
1. Check plugin installation: `docker-compose logs grafana | grep -i infinity`
2. Verify env var: `GF_INSTALL_PLUGINS=yesoreyeram-infinity-datasource`
3. Restart Grafana: `docker-compose restart grafana`

---

## Resources

- **Grafana Documentation:** https://grafana.com/docs/
- **Infinity Plugin Docs:** https://grafana.com/grafana/plugins/yesoreyeram-infinity-datasource/
- **Dashboard Gallery:** https://grafana.com/grafana/dashboards/
- **Alert Configuration:** https://grafana.com/docs/grafana/latest/alerting/
- **Provisioning Guide:** https://grafana.com/docs/grafana/latest/administration/provisioning/

---

## Summary

✅ **Grafana is fully deployed and configured**
✅ **Dashboard auto-loads on startup**
✅ **Metrics refresh every 10 seconds**
✅ **Zero manual configuration required**

**Access your monitoring dashboard now:**
👉 http://localhost:3001 (admin / admin)

**All metrics are live and updating automatically!** 🎉
