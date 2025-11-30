# Grafana Monitoring Dashboard Setup Guide

**Purpose:** Visualize metrics from `/api/metrics/*` endpoints using Grafana
**Estimated Setup Time:** 15-30 minutes

---

## Overview

Your backend already exposes 6 metrics endpoints. Grafana will:
1. Query these endpoints every 5-10 seconds
2. Parse JSON responses
3. Display beautiful, real-time dashboards
4. Support custom alerts and annotations

---

## Step 1: Install Grafana

### Option A: Docker (Recommended)

Add Grafana to your existing `docker-compose.yml`:

```yaml
services:
  # ... existing services (api, redis, qdrant, searxng, parakeet) ...

  grafana:
    image: grafana/grafana:latest
    container_name: hirehub_grafana
    ports:
      - "3001:3000"  # Grafana UI at http://localhost:3001
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin  # Change in production!
      - GF_INSTALL_PLUGINS=grafana-infinity-datasource
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - hirehub-network
    depends_on:
      - api

volumes:
  grafana-data:
    driver: local

networks:
  hirehub-network:
    driver: bridge
```

Start Grafana:
```bash
docker-compose up -d grafana
```

### Option B: Local Installation

**macOS:**
```bash
brew install grafana
brew services start grafana
```

**Linux:**
```bash
sudo apt-get install -y grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

**Windows:**
Download from: https://grafana.com/grafana/download

---

## Step 2: Install Infinity Data Source Plugin

The Infinity plugin allows Grafana to query REST APIs (our `/api/metrics/*` endpoints).

### Via Docker (Automatic):
Already included in the docker-compose.yml above via:
```yaml
GF_INSTALL_PLUGINS=grafana-infinity-datasource
```

### Via CLI:
```bash
grafana-cli plugins install yesoreyeram-infinity-datasource
# Restart Grafana
sudo systemctl restart grafana-server  # Linux
brew services restart grafana           # macOS
```

---

## Step 3: Configure Data Source

1. **Open Grafana:**
   - URL: http://localhost:3001 (Docker) or http://localhost:3000 (Local)
   - Login: `admin` / `admin` (change password on first login)

2. **Add Infinity Data Source:**
   - Go to: **Configuration (⚙️) → Data Sources → Add data source**
   - Search for: **Infinity**
   - Click: **Select**

3. **Configure Infinity Data Source:**
   ```
   Name: HireHub Metrics API
   URL: http://api:8000  (Docker) or http://localhost:8001 (Local)
   ```

   If using Docker, the API is accessible at `http://api:8000` from within the Docker network.

   If running locally, use `http://localhost:8001`.

4. **Click:** Save & Test

---

## Step 4: Create Dashboards

### Option A: Import Pre-Built Dashboard (Recommended)

I'll create a JSON dashboard configuration you can import directly.

Save this as `grafana/dashboards/hirehub-metrics.json`:

```json
{
  "dashboard": {
    "title": "HireHub Metrics Dashboard",
    "tags": ["hirehub", "metrics", "performance"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "P95 Latency (Last Hour)",
        "type": "graph",
        "targets": [
          {
            "datasource": "HireHub Metrics API",
            "url": "/api/metrics/performance?time_window_minutes=60",
            "format": "table",
            "parser": "backend",
            "root_selector": "all_operations",
            "columns": [
              {
                "selector": "p95_ms",
                "text": "P95 Latency (ms)",
                "type": "number"
              }
            ]
          }
        ],
        "gridPos": {
          "x": 0,
          "y": 0,
          "w": 12,
          "h": 8
        }
      },
      {
        "id": 2,
        "title": "Hourly Cost",
        "type": "stat",
        "targets": [
          {
            "datasource": "HireHub Metrics API",
            "url": "/api/metrics/costs?time_window_minutes=60",
            "format": "table",
            "parser": "backend",
            "root_selector": "costs",
            "columns": [
              {
                "selector": "total_cost_usd",
                "text": "Cost (USD)",
                "type": "number"
              }
            ]
          }
        ],
        "gridPos": {
          "x": 12,
          "y": 0,
          "w": 6,
          "h": 4
        }
      },
      {
        "id": 3,
        "title": "Cache Hit Rate",
        "type": "gauge",
        "targets": [
          {
            "datasource": "HireHub Metrics API",
            "url": "/api/metrics/cache",
            "format": "table",
            "parser": "backend",
            "root_selector": "cache.prompt_cache",
            "columns": [
              {
                "selector": "hit_rate_percent",
                "text": "Hit Rate %",
                "type": "number"
              }
            ]
          }
        ],
        "gridPos": {
          "x": 18,
          "y": 0,
          "w": 6,
          "h": 4
        }
      },
      {
        "id": 4,
        "title": "Average Quality Score",
        "type": "stat",
        "targets": [
          {
            "datasource": "HireHub Metrics API",
            "url": "/api/metrics/quality?time_window_minutes=60",
            "format": "table",
            "parser": "backend",
            "root_selector": "quality",
            "columns": [
              {
                "selector": "avg_quality_score",
                "text": "Avg Quality",
                "type": "number"
              }
            ]
          }
        ],
        "gridPos": {
          "x": 12,
          "y": 4,
          "w": 6,
          "h": 4
        }
      },
      {
        "id": 5,
        "title": "System Health",
        "type": "table",
        "targets": [
          {
            "datasource": "HireHub Metrics API",
            "url": "/api/metrics/health",
            "format": "table",
            "parser": "backend",
            "root_selector": "health.components"
          }
        ],
        "gridPos": {
          "x": 18,
          "y": 4,
          "w": 6,
          "h": 4
        }
      },
      {
        "id": 6,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "datasource": "HireHub Metrics API",
            "url": "/api/metrics/performance?time_window_minutes=60",
            "format": "table",
            "parser": "backend",
            "root_selector": "all_operations"
          }
        ],
        "gridPos": {
          "x": 0,
          "y": 8,
          "w": 12,
          "h": 8
        }
      },
      {
        "id": 7,
        "title": "Monthly Cost Projection",
        "type": "stat",
        "targets": [
          {
            "datasource": "HireHub Metrics API",
            "url": "/api/metrics/costs?time_window_minutes=1440",
            "format": "table",
            "parser": "backend",
            "root_selector": "costs",
            "columns": [
              {
                "selector": "projected_monthly_cost_usd",
                "text": "Monthly Cost (USD)",
                "type": "number"
              }
            ]
          }
        ],
        "gridPos": {
          "x": 12,
          "y": 8,
          "w": 6,
          "h": 4
        }
      },
      {
        "id": 8,
        "title": "Refinement Rate",
        "type": "gauge",
        "targets": [
          {
            "datasource": "HireHub Metrics API",
            "url": "/api/metrics/quality?time_window_minutes=60",
            "format": "table",
            "parser": "backend",
            "root_selector": "quality",
            "columns": [
              {
                "selector": "refinement_rate_percent",
                "text": "Refinement %",
                "type": "number"
              }
            ]
          }
        ],
        "gridPos": {
          "x": 18,
          "y": 8,
          "w": 6,
          "h": 4
        }
      }
    ],
    "refresh": "10s",
    "time": {
      "from": "now-1h",
      "to": "now"
    }
  }
}
```

**Import Steps:**
1. In Grafana: **Dashboards (☰) → Import**
2. Click: **Upload JSON file**
3. Select: `grafana/dashboards/hirehub-metrics.json`
4. Click: **Load → Import**

### Option B: Manual Dashboard Creation

1. **Create New Dashboard:**
   - Click: **+ → Dashboard**
   - Click: **Add new panel**

2. **Add Performance Panel:**
   - Query:
     ```
     Data Source: HireHub Metrics API
     Type: Infinity
     Parser: Backend
     URL: /api/metrics/performance?time_window_minutes=60
     Format: Table
     ```
   - Visualization: **Time series** or **Stat**
   - Field: `all_operations.p95_ms`

3. **Add Cost Panel:**
   - URL: `/api/metrics/costs?time_window_minutes=60`
   - Field: `costs.total_cost_usd`
   - Visualization: **Stat** with sparkline

4. **Add Cache Hit Rate Panel:**
   - URL: `/api/metrics/cache`
   - Field: `cache.prompt_cache.hit_rate_percent`
   - Visualization: **Gauge** (0-100%)

5. **Add Quality Panel:**
   - URL: `/api/metrics/quality?time_window_minutes=60`
   - Field: `quality.avg_quality_score`
   - Visualization: **Gauge** (0-10)

6. **Add System Health Panel:**
   - URL: `/api/metrics/health`
   - Field: `health.components`
   - Visualization: **Table**

---

## Step 5: Set Up Auto-Refresh

1. Click: **Dashboard settings (⚙️)** (top right)
2. Set: **Auto refresh** → `10s` or `30s`
3. Click: **Save**

Now your dashboard will automatically update every 10-30 seconds!

---

## Step 6: Configure Alerts (Optional)

Grafana can send alerts based on metric thresholds.

1. **Edit Panel** → **Alert** tab
2. **Create Alert Rule:**
   ```
   Name: High P95 Latency
   Condition: WHEN avg() OF query(A, 5m, now) IS ABOVE 3000
   ```
3. **Configure Notification Channel:**
   - Go to: **Alerting → Notification channels**
   - Add: Email, Slack, PagerDuty, etc.

---

## Common Dashboard Panels

### 1. Performance Overview Panel
**Metrics:**
- P50, P95, P99 latency (line chart)
- Average response time (stat)
- Requests per second (graph)

**Query:** `/api/metrics/performance?time_window_minutes=60`

### 2. Cost Tracking Panel
**Metrics:**
- Current hourly cost (stat)
- Daily cost projection (stat)
- Monthly cost projection (stat)
- Cache hit rate impact (gauge)

**Query:** `/api/metrics/costs?time_window_minutes=60`

### 3. Quality Metrics Panel
**Metrics:**
- Average quality score (gauge 0-10)
- Refinement rate % (gauge)
- First-pass acceptance % (gauge)

**Query:** `/api/metrics/quality?time_window_minutes=60`

### 4. Cache Performance Panel
**Metrics:**
- L1 cache hit rate (gauge)
- L2 cache hit rate (gauge)
- Prompt cache hit rate (gauge)

**Query:** `/api/metrics/cache`

### 5. System Health Panel
**Metrics:**
- Redis status (indicator)
- Qdrant status (indicator)
- LLM status (indicator)
- Overall status (stat)

**Query:** `/api/metrics/health`

---

## Advanced: Provisioning (Infrastructure as Code)

To automatically configure Grafana on startup:

### 1. Create Datasource Config:
`grafana/datasources/hirehub-api.yaml`

```yaml
apiVersion: 1

datasources:
  - name: HireHub Metrics API
    type: yesoreyeram-infinity-datasource
    access: proxy
    url: http://api:8000
    isDefault: true
    jsonData:
      url_options:
        method: GET
      headers:
        - name: Content-Type
          value: application/json
```

### 2. Create Dashboard Provisioning:
`grafana/dashboards/dashboard.yaml`

```yaml
apiVersion: 1

providers:
  - name: 'HireHub Dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
```

### 3. Mount in Docker Compose:
```yaml
volumes:
  - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
  - ./grafana/datasources:/etc/grafana/provisioning/datasources
```

Now Grafana will auto-configure on startup!

---

## Troubleshooting

### Issue: "Cannot connect to API"
**Solution:**
- Docker: Use `http://api:8000` (service name)
- Local: Use `http://localhost:8001`
- Check firewall rules

### Issue: "No data in panels"
**Solution:**
- Verify API is running: `curl http://localhost:8001/api/metrics/dashboard`
- Check Grafana logs: `docker-compose logs grafana`
- Verify Infinity plugin installed: Grafana → Plugins → Infinity

### Issue: "Parse error"
**Solution:**
- Ensure JSON path is correct (e.g., `all_operations.p95_ms`)
- Check API response format: `curl http://localhost:8001/api/metrics/performance | jq`

---

## Example Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│                   HireHub Metrics Dashboard                 │
├─────────────────────┬──────────────┬────────────────────────┤
│  P95 Latency (ms)   │ Hourly Cost  │  Cache Hit Rate (%)   │
│  [Line Chart]       │   $0.0045    │      [Gauge 82%]      │
│                     │              │                        │
├─────────────────────┼──────────────┼────────────────────────┤
│  Error Rate (%)     │ Avg Quality  │  Refinement Rate (%)  │
│  [Line Chart]       │   7.8/10     │      [Gauge 28%]      │
│                     │              │                        │
├─────────────────────┴──────────────┴────────────────────────┤
│                    System Health Status                      │
│  Redis: ✅ Healthy  │  Qdrant: ✅ Healthy  │  LLM: ✅ Healthy │
├──────────────────────────────────────────────────────────────┤
│                   Monthly Cost Projection                    │
│                        $32.40                                │
└──────────────────────────────────────────────────────────────┘
```

---

## Quick Start Commands

```bash
# 1. Start Grafana (if using Docker)
docker-compose up -d grafana

# 2. Open Grafana
open http://localhost:3001  # macOS
# or visit http://localhost:3001 in browser

# 3. Login
# Username: admin
# Password: admin (change on first login)

# 4. Add Infinity data source
# Configuration → Data Sources → Add → Infinity
# URL: http://api:8000 (Docker) or http://localhost:8001 (Local)

# 5. Import dashboard
# Dashboards → Import → Upload JSON
# Use the hirehub-metrics.json provided above

# 6. Done! Your dashboard should now display live metrics
```

---

## Next Steps

1. ✅ **Set up Grafana** (15 min)
2. ✅ **Import dashboard** (5 min)
3. ✅ **Configure alerts** (10 min)
4. 📊 **Monitor in real-time**
5. 🔔 **Receive alerts** when thresholds exceeded

---

## Resources

- **Grafana Docs:** https://grafana.com/docs/
- **Infinity Plugin:** https://grafana.com/grafana/plugins/yesoreyeram-infinity-datasource/
- **Dashboard Examples:** https://grafana.com/grafana/dashboards/

---

**Estimated Total Setup Time:** 15-30 minutes
**Complexity:** Low (mostly configuration)
**Benefit:** Real-time visual monitoring with minimal code

Your metrics APIs are already built and working—Grafana just adds the visualization layer on top!
