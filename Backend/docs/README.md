# Backend Documentation

This folder contains all project documentation, implementation guides, and planning documents.

## Documentation Categories

### Adaptive Questions System
Documentation for the LangGraph-based adaptive questions workflow:

- **`ADAPTIVE_QUESTIONS_README.md`** - Main guide for the adaptive questions system
- **`ADAPTIVE_QUESTIONS_API_TESTING.md`** - API testing guide and examples
- **`PHASE_2_PLAN.md`** - Phase 2 implementation plan (async nodes, distributed state)
- **`PHASE_2_COMPLETE_SUMMARY.md`** - Phase 2 completion summary
- **`PHASE_3_PLAN.md`** - Phase 3 implementation plan (UX improvements, scaling)
- **`COMPLETE_IMPLEMENTATION_SUMMARY.md`** - Overall implementation summary

### Grafana Metrics & Monitoring
Documentation for the Grafana metrics dashboard integration:

- **`GRAFANA_QUICKSTART.md`** - Quick start guide for Grafana setup
- **`GRAFANA_SETUP_GUIDE.md`** - Comprehensive setup guide
- **`GRAFANA_INTEGRATION_COMPLETE.md`** - Integration completion summary
- **`GRAFANA_TESTING_SUMMARY.md`** - Testing summary and results
- **`GRAFANA_FIX_SOLUTION.md`** - Troubleshooting guide and solutions

### Performance & Optimization
Documentation for caching and performance strategies:

- **`CACHING_STRATEGY.md`** - Caching architecture and implementation
  - Two-tier embedding cache (Redis + in-memory)
  - Gemini prompt caching
  - Result caching strategies

### Integration Guides
Third-party service integrations:

- **`PARAKEET_SETUP.md`** - Self-hosted GPU speech-to-text setup
- **`PERPLEXICA_TESTING.md`** - Perplexica search integration testing

## Quick Navigation

### Getting Started
1. Read `ADAPTIVE_QUESTIONS_README.md` for the main workflow
2. Read `GRAFANA_QUICKSTART.md` for metrics monitoring
3. Read `CACHING_STRATEGY.md` for performance optimization

### Implementation Details
- **Phases:** `PHASE_2_PLAN.md`, `PHASE_3_PLAN.md`
- **Summaries:** `COMPLETE_IMPLEMENTATION_SUMMARY.md`

### Troubleshooting
- **Grafana Issues:** `GRAFANA_FIX_SOLUTION.md`
- **API Testing:** `ADAPTIVE_QUESTIONS_API_TESTING.md`

## Related Documentation

- **Main README:** `../README.md` (if exists)
- **Test Scripts:** `../test-scripts/README.md`
- **Root Project Docs:** `../../docs/` (parent project documentation)

## Documentation Standards

All documentation in this folder follows these conventions:
- Markdown format (`.md`)
- Clear headings and section organization
- Code examples where applicable
- Troubleshooting sections
- Last updated dates (where relevant)
