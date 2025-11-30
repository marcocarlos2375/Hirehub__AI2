# Test Scripts and Utilities

This folder contains various test scripts, utilities, and one-off tools used during development and testing.

## Categories

### Grafana Dashboard Scripts
Scripts for setting up and testing Grafana metrics dashboards:
- `create_final_dashboard.py` - Creates the main working Grafana dashboard
- `create_simple_dashboard.py` - Simple test dashboard
- `create_working_dashboard.py` - Alternative dashboard configuration
- `import_dashboard.py` - Import dashboard via Grafana API
- `populate_grafana_metrics.py` - Generate test metrics data for dashboards
- `test_grafana_metrics.py` - Test metrics API endpoints

### Metrics Testing
Scripts for testing the metrics collection system:
- `test_metrics_collector.py` - Test the metrics collector
- `test_metrics_endpoints.py` - Test metrics API endpoints
- `check_metrics_state.py` - Debug metrics state
- `test_populate_metrics.py` - Populate metrics for testing
- `test_instrumented_nodes.py` - Test instrumented workflow nodes

### Adaptive Questions Testing
Scripts for testing the adaptive questions workflow:
- `test_async_nodes.py` - Test async workflow nodes
- `test_batch_questions.py` - Test batch question processing
- `test_distributed_state.py` - Test distributed state management
- `test_dynamic_quality_threshold.py` - Test dynamic quality thresholds
- `test_evaluate_endpoint.py` - Test quality evaluation endpoint
- `test_refine_endpoint.py` - Test answer refinement endpoint
- `test_refinement_422_fix.py` - Test refinement bug fixes
- `test_state_persistence.py` - Test state persistence
- `test_workflow_debug.py` - Debug workflow issues
- `test_format_answer.py` - Test answer formatting
- `test_example_relevance.py` - Test RAG example relevance
- `test_personalized_examples.py` - Test personalized examples
- `test_parallel_rag_searches.py` - Test parallel RAG searches
- `test_smart_question_skipping.py` - Test smart skip logic
- `test_smart_skip_routing.py` - Test skip routing

### Scoring & Gap Analysis Testing
Scripts for testing compatibility scoring:
- `test_all_gap_types.py` - Test all gap priority types
- `test_perfect_match.py` - Test perfect CV-JD matches
- `test_moderate_match.py` - Test moderate matches
- `test_high_score_all_nice_to_have.py` - Test high scores with nice-to-have gaps

### Performance & Optimization Testing
Scripts for testing performance optimizations:
- `test_lru_cache.py` - Test LRU cache implementation
- `test_prompt_caching.py` - Test Gemini prompt caching

### Integration Testing
End-to-end pipeline tests:
- `test_complete_pipeline.py` - Full pipeline integration test

### Search & Resources Testing
Scripts for testing search integrations:
- `test_searxng_integration.py` - Test SearXNG search
- `test_perplexica_simple.py` - Test Perplexica integration
- `test_multi_domain_providers.py` - Test multi-domain provider support
- `test_provider_recognition_quick.py` - Quick provider recognition test

### Utilities
General utility scripts:
- `clear_cache.py` - Clear embedding/prompt caches

## Usage

Most scripts can be run directly from the Backend directory:

```bash
cd Backend
python test-scripts/test_complete_pipeline.py
```

Or from within the test-scripts directory:

```bash
cd Backend/test-scripts
python test_complete_pipeline.py
```

## Note

These are development/testing scripts and are not part of the production codebase. The main test suite is in `Backend/tests/`.
