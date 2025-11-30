# Grafana "No Data" Issue - Root Cause & Solution

## ✅ What's Working

1. **Grafana** - Running perfectly on http://localhost:3001
2. **Dashboard** - Imported and configured with 6 panels
3. **Metrics API** - All 6 endpoints responding correctly
4. **Datasource** - Connected to API successfully

**Dashboard URL:** http://localhost:3001/d/4d99bc15-6a7d-4396-9d23-ef7d7b3e92c0/hirehub-metrics-dashboard

---

## ❌ Root Cause: Instrumented Nodes Not Integrated

The dashboard shows "No data" because:

**The workflow is NOT using the instrumented nodes from Phase 3.2**

When workflows run (like your resume rewrite pipeline), they use the standard nodes which DON'T call `metrics_collector.record_*()` methods. Only the **instrumented** versions track metrics.

---

## 🎯 Solution: Integrate Instrumented Workflow Nodes

You have two options:

### Option 1: Quick Test (See Data Immediately)

Create a test endpoint that uses metrics directly:

```python
# Add to app/main.py

@app.post("/api/test-metrics")
async def test_metrics():
    """Generate test metrics for Grafana testing."""
    from core.metrics_collector import get_metrics_collector
    import random

    collector = get_metrics_collector()

    # Generate some test metrics
    for i in range(10):
        # Performance
        collector.record_performance(
            operation="test_operation",
            duration_ms=random.uniform(500, 2000),
            metadata={"test": True}
        )

        # Costs
        collector.record_llm_cost(
            operation="test_llm_call",
            input_tokens=random.randint(1000, 3000),
            output_tokens=random.randint(500, 1500),
            cache_hit=random.choice([True, False]),
            metadata={"test": True}
        )

        # Quality
        collector.record_quality(
            question_id=f"test-q-{i}",
            gap_priority="CRITICAL",
            quality_score=random.randint(5, 9),
            refinement_count=random.randint(0, 2),
            metadata={"test": True}
        )

    return {"message": "Test metrics generated", "count": 10}
```

Then call it:
```bash
curl -X POST http://localhost:8001/api/test-metrics
```

Refresh Grafana - you'll see data!

### Option 2: Production Fix (Integrate Instrumented Nodes)

This is the proper solution for your actual workflows.

**Step 1: Check Current Workflow**

```bash
# See what's being used now
grep -n "from core.answer_flow" core/adaptive_question_graph.py
```

**Step 2: Update Imports**

Change from:
```python
from core.answer_flow_nodes import (
    generate_deep_dive_prompts_node,
    evaluate_quality_node,
    refine_answer_node,
    # ... etc
)
```

To:
```python
from core.answer_flow_nodes_instrumented import (
    generate_deep_dive_prompts_node_instrumented,
    evaluate_quality_node_instrumented,
    refine_answer_node_instrumented,
    # ... etc
)
```

**Step 3: Update Node References in Workflow**

Change:
```python
workflow.add_node("generate_deep_dive", generate_deep_dive_prompts_node)
```

To:
```python
workflow.add_node("generate_deep_dive", generate_deep_dive_prompts_node_instrumented)
```

**Step 4: Restart API**

```bash
docker-compose restart api
```

Now when you run workflows, metrics will automatically populate!

---

## 📊 Available Instrumented Nodes

These nodes are in `core/answer_flow_nodes_instrumented.py`:

1. `generate_deep_dive_prompts_node_instrumented`
2. `evaluate_quality_node_instrumented`
3. `refine_answer_node_instrumented`
4. `search_learning_resources_node_instrumented`
5. `generate_learning_plan_node_instrumented`

Each one automatically tracks:
- Performance (latency)
- Costs (LLM tokens)
- Quality (scores, refinement rates)

---

## 🔍 Verification

After implementing Option 1 or Option 2:

**1. Generate Metrics:**
```bash
# Option 1: Call test endpoint
curl -X POST http://localhost:8001/api/test-metrics

# Option 2: Run your actual pipeline
# (it will now generate metrics automatically)
```

**2. Check Metrics API:**
```bash
curl http://localhost:8001/api/metrics/dashboard | python3 -m json.tool | head -40
```

**3. Open Grafana:**
http://localhost:3001/d/4d99bc15-6a7d-4396-9d23-ef7d7b3e92c0/hirehub-metrics-dashboard

**4. You Should See:**
- P95 Latency: ~500-2000ms
- Hourly Cost: $0.05-0.15
- Quality Score: 5-9/10
- Cache Hit Rate: 0-100%

---

## 🎯 Quick Fix (Right Now)

Want to see it working immediately? Here's the fastest path:

**1. Create test endpoint** (1 minute):

```bash
cat >> app/main.py << 'EOF'

@app.post("/api/test-metrics")
async def test_metrics():
    from core.metrics_collector import get_metrics_collector
    import random
    collector = get_metrics_collector()
    for i in range(20):
        collector.record_performance("test", random.uniform(500, 2000), {})
        collector.record_llm_cost("test", random.randint(1000, 3000), random.randint(500, 1500), random.choice([True, False]), {})
        collector.record_quality(f"test-{i}", "CRITICAL", random.randint(5, 9), random.randint(0, 2), {})
    return {"message": "Metrics generated"}
EOF
```

**2. Restart API:**
```bash
docker-compose restart api
```

**3. Generate metrics:**
```bash
sleep 5
curl -X POST http://localhost:8001/api/test-metrics
```

**4. Check Grafana:**
http://localhost:3001/d/4d99bc15-6a7d-4396-9d23-ef7d7b3e92c0/hirehub-metrics-dashboard

You'll see data within 10 seconds (auto-refresh)!

---

## 📋 Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Grafana Service | ✅ Working | Running on port 3001 |
| Metrics API | ✅ Working | 6 endpoints operational |
| Dashboard | ✅ Working | Imported and configured |
| Datasource | ✅ Working | Connected to API |
| **Metrics Data** | ❌ Missing | **Instrumented nodes not integrated** |

**The ONLY thing missing:** Workflows need to use instrumented nodes to generate metrics.

**Quick test:** Add `/api/test-metrics` endpoint above and call it.

**Production fix:** Update `core/adaptive_question_graph.py` to use instrumented nodes.

---

## 🚀 After Fix

Once instrumented nodes are integrated, your dashboard will show:

1. **P95 Latency** - Response times for each workflow step
2. **Hourly Cost** - Real-time LLM cost tracking
3. **Quality Score** - Average evaluation scores
4. **Monthly Projection** - Estimated monthly costs
5. **Cache Hit Rate** - Prompt cache effectiveness
6. **System Health** - Component status

All updating automatically every 10 seconds! 🎉

---

## 📞 Need Help?

If you want me to:
1. ✅ Add the test endpoint for you
2. ✅ Update the workflow to use instrumented nodes
3. ✅ Verify everything is working

Just let me know which option you prefer!
