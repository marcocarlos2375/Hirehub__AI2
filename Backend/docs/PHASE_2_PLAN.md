# Phase 2: Systematic Infrastructure (Weeks 3-6)

**Goal**: Build robust infrastructure to support scalable, production-ready adaptive question workflows.

**Status**: Ready to begin (Phase 1 Complete - All 5 Quick Wins ✅)

---

## Overview

Phase 2 focuses on transforming the Quick Wins into a production-grade system with:
- Async/await throughout the stack
- Distributed state management
- Batch processing capabilities
- Advanced caching strategies
- Comprehensive monitoring

**Expected Impact**:
- 40-50% further performance improvement
- Multi-server deployment support
- Better error handling and recovery
- Real-time performance metrics
- Foundation for 100+ concurrent users

---

## Phase 2.1: Async Node Conversion (Week 3 - Days 1-3)

**Goal**: Convert synchronous workflow nodes to async/await for true concurrency.

**Current State**:
- LangGraph nodes are synchronous functions
- RAG searches use `asyncio.to_thread()` as workaround
- API endpoints are async but nodes block event loop

**Target State**:
- All nodes use async/await natively
- True concurrent I/O operations
- No thread pool overhead

**Implementation Tasks**:

1. **Convert Deep Dive Prompts Node**
   ```python
   # BEFORE
   def generate_deep_dive_prompts_node(state: AdaptiveAnswerState) -> AdaptiveAnswerState:
       llm = get_llm("fast")
       result = chain.invoke(...)  # Synchronous

   # AFTER
   async def generate_deep_dive_prompts_node(state: AdaptiveAnswerState) -> AdaptiveAnswerState:
       llm = get_async_llm("fast")
       result = await chain.ainvoke(...)  # Asynchronous
   ```

2. **Convert Quality Evaluation Node**
   - Use async LLM calls
   - Parallel evaluation of multiple criteria

3. **Convert Answer Generation Node**
   - Async prompt execution
   - Stream responses for real-time feedback

4. **Convert RAG Search Node**
   - Replace `asyncio.to_thread()` with native async Qdrant client
   - Already parallelized (Quick Win #3), just need native async

5. **Update Workflow Orchestration**
   - LangGraph supports async nodes
   - Update `run_async()` to use async nodes
   - Keep `run_sync()` for backward compatibility

**Expected Impact**:
- 30-40% faster node execution
- Better CPU utilization
- Reduced thread pool contention

**Files to Modify**:
- `core/answer_flow_nodes.py` - Convert all nodes to async
- `core/langchain_config.py` - Add async LLM getters
- `core/vector_store.py` - Add async Qdrant methods
- `core/adaptive_question_graph.py` - Update workflow to use async nodes

---

## Phase 2.2: Distributed State Management (Week 3 - Days 4-7)

**Goal**: Replace file-based snapshots with Redis for multi-server deployments.

**Current State** (Quick Win #5):
- State snapshots saved to local filesystem
- Works for single-server deployments
- Not suitable for load-balanced multi-server setups

**Target State**:
- State stored in Redis with TTL
- Shared across all API instances
- Automatic cleanup of expired sessions

**Implementation Tasks**:

1. **Create Redis State Backend**
   ```python
   # core/state_persistence_redis.py
   class RedisStateBackend:
       def __init__(self, redis_url: str):
           self.redis = redis.from_url(redis_url)

       async def save_state(self, session_id: str, state: dict, ttl: int = 3600):
           key = f"session:{session_id}"
           await self.redis.setex(key, ttl, json.dumps(state))

       async def load_state(self, session_id: str) -> Optional[dict]:
           key = f"session:{session_id}"
           data = await self.redis.get(key)
           return json.loads(data) if data else None
   ```

2. **Update LangGraph Checkpointer**
   - LangGraph supports custom checkpointers
   - Create `RedisCheckpointer` class extending `BaseCheckpointSaver`
   - Replace `MemorySaver()` with `RedisCheckpointer()`

3. **Migration Path**
   - Keep file-based snapshots as fallback
   - Use Redis if `REDIS_STATE_URL` is configured
   - Gradual migration strategy

4. **Add State Expiration**
   - Default TTL: 24 hours
   - Configurable per session
   - Automatic cleanup by Redis

**Expected Impact**:
- Multi-server deployments supported
- Session resumption works across servers
- Automatic state cleanup (no disk bloat)
- Foundation for horizontal scaling

**Files to Create**:
- `core/state_persistence_redis.py` - Redis state backend
- `core/redis_checkpointer.py` - LangGraph Redis checkpointer

**Files to Modify**:
- `core/adaptive_question_graph.py` - Use Redis checkpointer
- `.env.example` - Add REDIS_STATE_URL config
- `docker-compose.yml` - Add Redis service for state

---

## Phase 2.3: Batch Question Generation API (Week 4 - Days 1-3)

**Goal**: Generate questions for all gaps in a single API call instead of one-by-one.

**Current State**:
- Frontend calls `/api/adaptive-questions/start` for each question
- Each call: 2-3s (RAG search + LLM generation)
- 10 questions = 20-30s total (sequential)

**Target State**:
- Single API call generates all questions
- Parallel LLM calls for different gaps
- 10 questions in 3-5s (parallelized)

**Implementation Tasks**:

1. **Create Batch Endpoint**
   ```python
   @app.post("/api/adaptive-questions/batch-start")
   async def batch_start_questions(request: BatchStartRequest):
       gaps = request.gaps  # All critical + important gaps

       # Generate questions in parallel
       async def generate_for_gap(gap):
           return await generate_question_for_gap(gap, request.parsed_cv, request.parsed_jd)

       results = await asyncio.gather(*[generate_for_gap(g) for g in gaps])

       return BatchQuestionResponse(questions=results)
   ```

2. **Optimize Parallel Generation**
   - Share embedding calculations across gaps
   - Batch RAG searches (Quick Win #3 already parallelized)
   - Shared prompt context

3. **Add Request Batching**
   - Group similar gaps for shared context
   - Reduce redundant embeddings

**Expected Impact**:
- 10 questions: 20-30s → 3-5s (6x faster)
- Reduced API roundtrips
- Better resource utilization

**Files to Create**:
- `app/batch_endpoints.py` - Batch question generation

**Files to Modify**:
- `app/main.py` - Add batch endpoint
- `core/answer_flow_nodes.py` - Extract reusable generation logic

---

## Phase 2.4: Advanced Prompt Caching (Week 4 - Days 4-7)

**Goal**: Maximize Gemini prompt caching for 50% cost reduction and faster responses.

**Current State** (Partial):
- Basic prompt caching in `core/gemini_cache.py`
- Used for question generation
- Not optimized for cache hit rate

**Target State**:
- Structured prompts for maximum cache hits
- Shared system prompts across all questions
- Cache hit rate: 80%+

**Implementation Tasks**:

1. **Analyze Cache Patterns**
   - Log all prompt cache hits/misses
   - Identify common prompt prefixes
   - Optimize for Gemini's caching rules

2. **Restructure Prompts**
   ```python
   # BEFORE
   prompt = f"System: {instructions}\n\nCV: {cv}\n\nJD: {jd}\n\nGenerate..."

   # AFTER (cacheable system prompt)
   system_prompt = f"System: {instructions}"  # Cached across requests
   user_prompt = f"CV: {cv}\n\nJD: {jd}\n\nGenerate..."  # Variable
   ```

3. **Implement Cache Warming**
   - Pre-cache common system prompts on startup
   - Refresh before TTL expiration

4. **Add Cache Monitoring**
   - Track cache hit rate per endpoint
   - Alert on low cache utilization

**Expected Impact**:
- 50% cost reduction on LLM calls
- 20-30% faster response times
- Better cost predictability

**Files to Modify**:
- `core/gemini_cache.py` - Enhanced caching logic
- `app/config.py` - Restructure prompts for caching
- `core/monitoring.py` - Add cache metrics

---

## Phase 2.5: Monitoring & Metrics (Week 5-6)

**Goal**: Add comprehensive monitoring for performance tracking and debugging.

**Current State**:
- Basic timing logs in responses
- Cache stats via `/api/cache/stats`
- No aggregated metrics

**Target State**:
- Real-time performance dashboards
- Request tracing
- Error tracking
- Performance alerts

**Implementation Tasks**:

1. **Add Prometheus Metrics**
   ```python
   from prometheus_client import Counter, Histogram

   request_count = Counter('api_requests_total', 'Total API requests', ['endpoint', 'status'])
   request_duration = Histogram('api_request_duration_seconds', 'Request duration', ['endpoint'])

   @app.middleware("http")
   async def metrics_middleware(request, call_next):
       start = time.time()
       response = await call_next(request)
       duration = time.time() - start

       request_count.labels(endpoint=request.url.path, status=response.status_code).inc()
       request_duration.labels(endpoint=request.url.path).observe(duration)

       return response
   ```

2. **Add Request Tracing**
   - Generate trace_id for each request
   - Log trace_id in all operations
   - Correlate logs across nodes

3. **Add Performance Alerts**
   - Alert on P95 latency > threshold
   - Alert on error rate > 5%
   - Alert on cache hit rate < 70%

4. **Create Monitoring Dashboard**
   - Grafana dashboard for metrics
   - Real-time request tracking
   - Error rate trending

**Expected Impact**:
- Faster debugging
- Performance regression detection
- Capacity planning data

**Files to Create**:
- `core/monitoring.py` - Metrics collection
- `core/tracing.py` - Request tracing
- `docker-compose.yml` - Add Prometheus + Grafana

---

## Phase 2 Success Metrics

**Performance**:
- ✅ Session time: 6-9s → 4-5s (40-50% faster)
- ✅ Batch generation: 20-30s → 3-5s (6x faster)
- ✅ Cache hit rate: 70% → 85%+ (Gemini + embedding)
- ✅ P95 latency: <8s for full session

**Infrastructure**:
- ✅ Multi-server deployments supported
- ✅ State shared via Redis
- ✅ Async nodes throughout
- ✅ Real-time metrics

**Cost**:
- ✅ 50% reduction in LLM costs (prompt caching)
- ✅ 30% reduction in compute costs (async efficiency)

---

## Implementation Priority

**Week 3**:
1. Day 1-3: Async node conversion (Phase 2.1)
2. Day 4-7: Distributed state with Redis (Phase 2.2)

**Week 4**:
1. Day 1-3: Batch question generation API (Phase 2.3)
2. Day 4-7: Advanced prompt caching (Phase 2.4)

**Week 5-6**:
1. Monitoring & metrics (Phase 2.5)
2. Testing and optimization
3. Documentation updates

---

## Risks and Mitigations

**Risk 1**: Async conversion breaks existing code
- **Mitigation**: Keep sync versions, gradual migration, extensive testing

**Risk 2**: Redis dependency adds complexity
- **Mitigation**: Fallback to file-based persistence if Redis unavailable

**Risk 3**: Prompt caching rules change (Gemini)
- **Mitigation**: Monitor cache hit rate, adapt prompt structure

**Risk 4**: Performance regressions during refactoring
- **Mitigation**: Benchmark each change, keep rollback plan

---

## Ready to Begin!

Phase 1 laid the foundation with Quick Wins. Phase 2 will build production-grade infrastructure on top of that foundation.

**First Task**: Phase 2.1 - Convert nodes to async/await

Ready to proceed? 🚀
