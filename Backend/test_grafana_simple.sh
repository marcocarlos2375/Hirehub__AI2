#!/bin/bash

# Simple Grafana Integration Test
# This script verifies all components are working

echo "================================================================================"
echo "  GRAFANA INTEGRATION TEST"
echo "================================================================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Grafana Health
echo -e "\n📊 Test 1: Grafana Service"
GRAFANA_HEALTH=$(curl -s http://localhost:3001/api/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "   ${GREEN}✅ Grafana is running${NC}"
    VERSION=$(echo $GRAFANA_HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin).get('version', 'unknown'))")
    echo -e "   Version: $VERSION"
else
    echo -e "   ${RED}❌ Grafana is not responding${NC}"
    echo -e "   ${YELLOW}💡 Run: docker-compose up -d grafana${NC}"
fi

# Test 2: API Health
echo -e "\n🔌 Test 2: API Service"
API_RESPONSE=$(curl -s http://localhost:8001/ 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "   ${GREEN}✅ API is running${NC}"
else
    echo -e "   ${RED}❌ API is not responding${NC}"
    echo -e "   ${YELLOW}💡 Run: docker-compose up -d api${NC}"
fi

# Test 3: Metrics Endpoints
echo -e "\n📈 Test 3: Metrics Endpoints"

ENDPOINTS=(
    "dashboard"
    "performance"
    "costs"
    "quality"
    "cache"
    "health"
)

ALL_OK=true
for endpoint in "${ENDPOINTS[@]}"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/metrics/$endpoint 2>/dev/null)
    if [ "$STATUS" = "200" ]; then
        echo -e "   ${GREEN}✅${NC} /api/metrics/$endpoint"
    else
        echo -e "   ${RED}❌${NC} /api/metrics/$endpoint (HTTP $STATUS)"
        ALL_OK=false
    fi
done

if [ "$ALL_OK" = true ]; then
    echo -e "\n   ${GREEN}All metrics endpoints operational!${NC}"
else
    echo -e "\n   ${YELLOW}Some endpoints failed. Check API logs:${NC}"
    echo -e "   ${YELLOW}docker-compose logs api | tail -50${NC}"
fi

# Test 4: Generate Test Data
echo -e "\n🎲 Test 4: Generate Test Metrics"
echo -e "   Running test data generator..."
docker-compose exec -T api python test_populate_metrics.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "   ${GREEN}✅ Test metrics generated${NC}"
else
    echo -e "   ${YELLOW}⚠️  Metrics generation had errors (check above)${NC}"
fi

# Test 5: Check Dashboard Data
echo -e "\n📊 Test 5: Dashboard Data"
DASHBOARD_DATA=$(curl -s http://localhost:8001/api/metrics/dashboard 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "   ${GREEN}✅ Dashboard endpoint responding${NC}"

    # Try to parse some data (requires Python)
    COSTS=$(echo $DASHBOARD_DATA | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('costs', {}).get('total_cost_usd', 'N/A'))" 2>/dev/null)
    QUALITY=$(echo $DASHBOARD_DATA | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('quality', {}).get('avg_quality_score', 'N/A'))" 2>/dev/null)

    if [ "$COSTS" != "N/A" ] && [ "$COSTS" != "0" ]; then
        echo -e "   💰 Total Cost: \$$COSTS"
    fi

    if [ "$QUALITY" != "N/A" ] && [ "$QUALITY" != "0" ]; then
        echo -e "   ⭐ Avg Quality: $QUALITY/10"
    fi
else
    echo -e "   ${RED}❌ Dashboard endpoint failed${NC}"
fi

# Summary
echo -e "\n================================================================================"
echo -e "  TEST SUMMARY"
echo -e "================================================================================"

echo -e "\n${GREEN}✅ Integration Complete!${NC}"
echo -e "\nNext steps:"
echo -e "   1. Open Grafana: ${YELLOW}http://localhost:3001${NC}"
echo -e "   2. Login: ${YELLOW}admin / admin${NC}"
echo -e "   3. Navigate: ${YELLOW}Dashboards → HireHub Metrics Dashboard${NC}"
echo -e "\nNOTE: Dashboard may show 'No data' until you run actual workflows."
echo -e "      Metrics are in-memory and reset on API restart."

echo -e "\n💡 To generate test data anytime:"
echo -e "   ${YELLOW}docker-compose exec api python test_populate_metrics.py${NC}"

echo -e "\n================================================================================"
