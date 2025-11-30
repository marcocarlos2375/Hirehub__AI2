# Grafana Monitoring - Quick Start Guide

**Estimated Setup Time:** 5 minutes

---

## Step 1: Start Grafana

```bash
# Navigate to Backend directory
cd Backend

# Start Grafana service (will auto-configure with provisioning files)
docker-compose up -d grafana

# Wait for Grafana to start (30 seconds)
docker-compose logs -f grafana
# Look for: "HTTP Server Listen" message
```

---

## Step 2: Access Grafana

1. **Open browser:** http://localhost:3001
2. **Login:**
   - Username: `admin`
   - Password: `admin`
   - (You'll be prompted to change password on first login)

---

## Step 3: Verify Dashboard

The dashboard should be **auto-loaded** via provisioning:

1. Click **Dashboards** (☰ menu) → **Browse**
2. Look for: **"HireHub Metrics Dashboard"**
3. Click to open

**If dashboard doesn't appear:**
- Wait 10 seconds (provisioning runs every 10s)
- Refresh browser
- Check logs: `docker-compose logs grafana`

---

## What You'll See

### Dashboard Panels (8 total):

**Performance Monitoring:**
- ✅ **P95 Latency** - Response time tracking (line chart)
  - Green: < 2s
  - Yellow: 2-3s
  - Red: > 3s

- ✅ **Error Rate** - System reliability (line chart)
  - Green: < 1%
  - Yellow: 1-5%
  - Red: > 5%

**Cost Tracking:**
- ✅ **Hourly Cost** - Current spend rate (stat)
- ✅ **Monthly Cost Projection** - Estimated monthly bill (stat)

**Quality Metrics:**
- ✅ **Average Quality Score** - Answer quality (0-10 scale)
- ✅ **Refinement Rate** - % of answers needing refinement
  - Green: < 30%
  - Yellow: 30-50%
  - Red: > 50%

**System Health:**
- ✅ **Cache Hit Rate** - Prompt cache efficiency (gauge)
  - Green: > 80%
  - Yellow: 70-80%
  - Red: < 70%

- ✅ **System Health** - Component status table (Redis, Qdrant, LLM)

---

## Dashboard Controls

**Auto-refresh:** 10 seconds (top-right dropdown)
**Time range:** Last 1 hour (top-right)
**Customize:** Click panel title → Edit to modify queries

---

## Verify Data Flow

Test that metrics are flowing:

```bash
# 1. Check API metrics endpoint
curl http://localhost:8001/api/metrics/dashboard

# 2. Check Grafana datasource
# In Grafana: Configuration → Data Sources → HireHub Metrics API → "Save & Test"
# Should show: "Data source is working"

# 3. Trigger some activity
curl -X POST http://localhost:8001/api/adaptive-questions/start \
  -H "Content-Type: application/json" \
  -d '{
    "gap_info": {"title": "Docker", "priority": "CRITICAL"},
    "question_id": "test-1",
    "session_id": "test-session"
  }'

# 4. Watch dashboard update (within 10 seconds)
```

---

## Troubleshooting

### Issue: Dashboard is blank / no data

**Solution:**
1. Verify API is running: `docker-compose ps api`
2. Check API metrics: `curl http://localhost:8001/api/metrics/health`
3. Verify Infinity plugin installed:
   - Grafana → Configuration → Plugins → Search "Infinity"
   - Should show: "yesoreyeram-infinity-datasource"

### Issue: "Cannot connect to data source"

**Solution:**
1. Check datasource URL in Grafana:
   - Configuration → Data Sources → HireHub Metrics API
   - URL should be: `http://api:8000`
   - Click "Save & Test"
2. Verify API container name: `docker ps | grep api`
3. Check network: `docker network inspect test-hirehub-adaptive_default`

### Issue: Panels show "No data"

**Solution:**
1. Generate some metrics data:
   ```bash
   # Run a few test requests to populate metrics
   for i in {1..5}; do
     curl -X POST http://localhost:8001/api/adaptive-questions/start \
       -H "Content-Type: application/json" \
       -d "{\"gap_info\": {\"title\": \"Test $i\", \"priority\": \"MEDIUM\"}}"
     sleep 1
   done
   ```
2. Refresh dashboard (top-right circular arrow)
3. Adjust time range to "Last 15 minutes"

---

## Next Steps

### 1. Set Up Alerts (Optional)

Configure alerts to get notified when metrics exceed thresholds:

1. Click panel title → **Edit**
2. Go to **Alert** tab
3. Create alert rule:
   ```
   Name: High P95 Latency
   Condition: WHEN avg() OF query(A, 5m, now) IS ABOVE 3000
   ```
4. Configure notification channel:
   - **Alerting** → **Notification channels**
   - Add: Email, Slack, PagerDuty, etc.

### 2. Customize Dashboard

Add more panels for specific metrics:
- **Cache breakdown** - L1 vs L2 vs Prompt cache hit rates
- **Cost by operation** - Cost breakdown by workflow node
- **Quality trends** - Quality score over time
- **Resource usage** - Memory, CPU (requires node exporter)

### 3. Export Dashboard

Save dashboard configuration:
1. Dashboard settings (⚙️) → **JSON Model**
2. Copy JSON
3. Save to: `grafana/dashboards/hirehub-metrics-custom.json`
4. Commit to version control

---

## Production Checklist

Before deploying to production:

- [ ] Change Grafana admin password (default: `admin`)
- [ ] Set `GF_SECURITY_ADMIN_PASSWORD` in `.env` or docker-compose.yml
- [ ] Enable HTTPS for Grafana (reverse proxy or SSL cert)
- [ ] Configure external notification channels (email, Slack)
- [ ] Set up backup for `grafana_data` volume
- [ ] Restrict Grafana port (3001) to internal network only
- [ ] Enable Grafana authentication (LDAP, OAuth, etc.)
- [ ] Set up user roles and permissions
- [ ] Configure retention policies for metrics data
- [ ] Test alert notifications

---

## Useful Commands

```bash
# Start Grafana
docker-compose up -d grafana

# Stop Grafana
docker-compose stop grafana

# View logs
docker-compose logs -f grafana

# Restart Grafana (to reload config)
docker-compose restart grafana

# Reset Grafana (CAUTION: deletes all dashboards/settings)
docker-compose down -v grafana
docker volume rm test-hirehub-adaptive_grafana_data
docker-compose up -d grafana

# Check Grafana health
curl http://localhost:3001/api/health

# Export dashboard as PDF (requires image renderer plugin)
# Configuration → Plugins → Install "Image Renderer"
```

---

## Resources

- **Grafana Docs:** https://grafana.com/docs/
- **Infinity Plugin:** https://grafana.com/grafana/plugins/yesoreyeram-infinity-datasource/
- **Dashboard Examples:** https://grafana.com/grafana/dashboards/
- **Alert Configuration:** https://grafana.com/docs/grafana/latest/alerting/

---

**You're all set!** 🎉

Your HireHub monitoring dashboard is now running at **http://localhost:3001**

All metrics will auto-refresh every 10 seconds with zero code changes required.
