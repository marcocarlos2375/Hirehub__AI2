# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered job application optimization system (HireHubAI) that analyzes CV/resume compatibility with job descriptions using LLMs and semantic embeddings. The system uses a multi-phase pipeline to parse documents, calculate compatibility scores, generate personalized questions, and rewrite resumes to improve job match rates.

**Key Technologies:**
- Backend: Python, FastAPI, Google Gemini API, OpenAI API, LangGraph (workflow orchestration)
- Frontend: Nuxt 3 (Vue 3), TypeScript, Tailwind CSS, Vitest (testing)
- Database: PostgreSQL (user data), Qdrant (vector DB for RAG)
- Search: SearXNG (self-hosted meta-search for learning resources)
- Speech-to-Text: NVIDIA Parakeet v3 (self-hosted GPU service) + OpenAI Whisper (fallback)
- Optimization: TOON format for token reduction, embedding caching, prompt caching

## Development Commands

### Backend (FastAPI API Server)

```bash
# Navigate to Backend directory
cd Backend

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run API server locally (development)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run with Docker Compose (includes Qdrant vector DB + Parakeet)
docker-compose up

# Run specific services
docker-compose up api          # Just the API (without Parakeet GPU service)
docker-compose up parakeet     # Just the Parakeet speech-to-text service

# API will be available at http://localhost:8001
# PostgreSQL database at localhost:5433
# Qdrant dashboard at http://localhost:6333/dashboard
# SearXNG at http://localhost:8888
# Parakeet API at http://localhost:8002
```

### Parakeet Speech-to-Text Service (Optional GPU Service)

The project includes a self-hosted NVIDIA Parakeet v3 speech-to-text service for 95% cost savings vs OpenAI Whisper API.

**Requirements:**
- NVIDIA GPU with 3+ GB VRAM
- NVIDIA Container Runtime
- CUDA 12.1+

**Setup:**
```bash
# See Backend/parakeet-service/README.md for full setup instructions

# Enable in Backend/.env
USE_PARAKEET=true
PARAKEET_URL=http://parakeet:8002

# Start service
cd Backend
docker-compose up -d parakeet
```

**Features:**
- 10x faster than Whisper API (0.12s for 2-min audio)
- 25 language support (EN, FR, DE, ES, IT, PT, etc.)
- Automatic language detection
- Falls back to OpenAI Whisper if unavailable

**Note:** If you don't have a GPU or don't start Parakeet, the system automatically uses OpenAI Whisper API as a fallback.
```

### Frontend (Nuxt 3 Application)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
# Frontend will be available at http://localhost:3000

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm run test              # Watch mode
npm run test:run          # Run once
npm run test:ui           # Visual UI (http://localhost:51204)
npm run test:coverage     # Generate coverage report

# Type checking (run this after making edits)
npx nuxi typecheck        # Check TypeScript types across entire app

# View UI component library
# Visit http://localhost:3000/ui-test
```

**IMPORTANT:** Always run `npx nuxi typecheck` after making edits to Vue components or TypeScript files to catch type errors early. This helps maintain type safety and prevents runtime errors.

### Running Tests

Tests are organized in `Backend/tests/` with unit, integration, and debug folders. Additional test scripts exist in the project root for quick prototyping.

```bash
# Navigate to Backend directory
cd Backend

# Integration tests (full pipeline)
python tests/integration/test_complete_pipeline.py
python tests/integration/test_good_match_scoring.py
python tests/integration/test_detailed_gap_analysis.py
python tests/integration/test_phase4.py
python tests/integration/test_resume_rewrite_integration.py

# Unit tests (specific components)
python tests/unit/test_optimizations.py
python tests/unit/test_web_dev_matching.py
python tests/unit/test_database_management_matching.py
python tests/unit/test_multilanguage_soft_skills.py
python tests/unit/test_cross_language_skills.py
python tests/unit/test_resume_rewrite.py

# Debug tests (for troubleshooting)
python tests/debug/debug_scoring_details.py
python tests/debug/debug_industry_matching.py
python tests/debug/debug_embedding_similarity.py

# Root-level test scripts (rapid prototyping)
# These test specific features quickly without full test structure
python test_sophia_healthtrack.py          # Test with specific resume
python test_domain_finder.py               # Test domain finder feature
python test_parsing_cache.py               # Test parsing cache
python test_prompt_caching.py              # Test prompt caching
python test_redis_cache_sharing.py         # Test Redis cache

# Benchmark tests (via Docker)
docker-compose run benchmark               # Benchmark TOON format
docker-compose run benchmark-json          # Benchmark JSON format
```

## Environment Variables

The project requires API keys in `Backend/.env`:

**Required:**
- `GEMINI_API_KEY` - Google Gemini API key (required for all LLM operations)
- `OPENAI_API_KEY` - OpenAI API key (required for Whisper transcription fallback)

**Optional:**
- `REDIS_URL` - Redis URL for embedding cache (e.g., `redis://localhost:6379/0`)
  - If not set, falls back to in-memory cache
  - Redis enables cache sharing across multiple API instances
- `USE_PARAKEET` - Enable self-hosted Parakeet speech-to-text (`true`/`false`)
  - Defaults to `false` (uses OpenAI Whisper)
- `PARAKEET_URL` - Parakeet service URL (default: `http://parakeet:8002`)
- `SEARXNG_URL` - SearXNG instance URL (default: `http://searxng:8080`)
  - Used for learning resource discovery in adaptive questions
- `DATABASE_URL` - PostgreSQL connection string
  - Format: `postgresql://hirehub:hirehub_password@localhost:5433/hirehub`
  - Used for storing learning plans and user data

**Example `.env` file:**
```env
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
REDIS_URL=redis://localhost:6379/0
USE_PARAKEET=false
PARAKEET_URL=http://parakeet:8002
SEARXNG_URL=http://searxng:8080
DATABASE_URL=postgresql://hirehub:hirehub_password@localhost:5433/hirehub
```

## Architecture

### System Pipeline (5 Phases)

The application follows a multi-phase pipeline architecture (see `docs/pipeline.md` for full example):

1. **Phase 1-2: Document Parsing**
   - Parse job description → structured JSON
   - Parse CV/resume → structured JSON
   - Uses Gemini 2.5 Flash-Lite with optimized prompts

2. **Phase 3: Compatibility Scoring (Hybrid Approach)**
   - **Vector Embeddings:** Calculate semantic similarity using Google's text-embedding-004
   - **Rule-based Scoring:** Calculate category scores (hard skills, soft skills, experience, domain, industry, role, portfolio, location)
   - **AI Gap Analysis:** Use Gemini to identify gaps, strengths, and application viability
   - **Output:** Overall score (0-100), category breakdowns, detailed gaps, strengths

3. **Phase 4: Adaptive Questions (LangGraph Workflow)**
   - Generate 5-11 personalized questions based on gaps
   - **Intelligent Flow:** Users select experience level (Yes/No/Willing to Learn)
     - **Yes** → Deep-dive prompts to extract details
     - **No** → Skip question
     - **Willing to Learn** → SearXNG search for learning resources, generate learning plan
   - **LangGraph State Machine:** Orchestrates multi-step workflow with branching logic
   - **Quality Evaluation:** AI scores answer quality (0-10) and provides improvement suggestions
   - **Iterative Refinement:** Up to 2 refinement cycles to improve low-quality answers
   - Use Qdrant vector DB to find similar past experiences (RAG)
   - Support text or voice answers (Parakeet/Whisper transcription)
   - Extract "hidden experience" not in original CV
   - Save learning plans to PostgreSQL for future reference

5. **Phase 5: Resume Rewriting**
   - Incorporate insights from user answers
   - Optimize for ATS keywords from job description
   - Generate both sample.json format (HTML, camelCase) and parsed format (plain text, snake_case)
   - Add new projects, skills, and enhance existing descriptions

### Backend Architecture

**Core API Endpoints (`Backend/app/main.py`):**

*Document Processing:*
- `POST /api/parse` - Parse job description (Phase 1)
- `POST /api/parse-cv` - Parse resume/CV (Phase 2)
- `POST /api/calculate-score` - Calculate compatibility score (Phase 3)

*Adaptive Questions Workflow (LangGraph):*
- `POST /api/adaptive-questions/start` - Start adaptive question flow (select Yes/No/Willing to Learn)
- `POST /api/adaptive-questions/submit-inputs` - Submit deep-dive answers or refinement data
- `POST /api/adaptive-questions/refine-answer` - Refine answer based on quality feedback
- `POST /api/adaptive-questions/get-learning-resources` - Get learning resources from SearXNG
- `POST /api/adaptive-questions/save-learning-plan` - Save learning plan to PostgreSQL
- `POST /api/adaptive-questions/get-learning-plans` - Retrieve saved learning plans

*Legacy Question Flow (being phased out):*
- `POST /api/generate-questions` - Generate personalized questions (Phase 4)
- `POST /api/submit-answers` - Analyze answers and update CV (Phase 4)

*Audio & Resume Generation:*
- `POST /api/transcribe-audio` - Transcribe voice answers (uses Parakeet or Whisper)
- `POST /api/rewrite-resume` - Generate optimized resume (Phase 5)

*Additional Features:*
- `POST /api/find-domain` - Find career domains based on CV/interests
- `POST /api/generate-cover-letter` - Generate cover letter from CV + job
- `POST /api/generate-job-search-queries` - Generate job search queries

*Monitoring:*
- `GET /api/cache/stats` - Get embedding cache statistics
- `GET /api/prompt-cache/stats` - Get prompt cache statistics (Gemini)

**Key Modules:**
- `app/main.py` - FastAPI application with all endpoints
- `app/config.py` - Centralized prompt templates for all phases
- `core/adaptive_question_graph.py` - LangGraph workflow for adaptive questions (state machine)
- `core/answer_flow_nodes.py` - LangGraph nodes (deep-dive, search, evaluate, refine)
- `core/answer_flow_state.py` - LangGraph state definition
- `core/searxng_client.py` - SearXNG search client for learning resources
- `core/search_query_builder.py` - Intelligent search query generation
- `core/resource_matcher.py` - Learning resource matching and ranking
- `core/embeddings.py` - Semantic similarity with caching (2-tier: in-memory + Redis)
- `core/cache.py` - Embedding cache management (Redis or in-memory)
- `core/gemini_cache.py` - Gemini prompt caching (context caching for repeated prompts)
- `core/vector_store.py` - RAG vector database (Qdrant) for question generation
- `core/text_processing.py` - Text normalization utilities
- `core/langchain_config.py` - LangChain/LangGraph configuration
- `formats/toon.py` - TOON format conversion for 40-50% token reduction
- `parakeet-service/` - Self-hosted GPU speech-to-text microservice

**Performance Optimizations:**
1. **TOON Format:** Custom compressed format reducing tokens by 40-50% vs JSON (see `docs/TOON_FORMAT_EXPLAINED.md`)
2. **Hybrid Scoring:** Category scores calculated via embeddings/rules (instant) rather than asking Gemini (~4s saved)
3. **Embedding Cache:** Two-tier caching (in-memory + Redis) for 90%+ speedup on cache hits
4. **Prompt Cache:** Gemini context caching for repeated system prompts (50% cost reduction, faster responses)
5. **Batch Embeddings:** Parallel embedding generation (3-4x faster)
6. **HTTP/2:** Persistent HTTP/2 client with connection pooling (30-50% faster API calls)
7. **Compressed Prompts:** Minimal prompts for Gemini (~60% smaller for gap analysis)
8. **Parakeet STT:** Self-hosted GPU transcription (10x faster, 95% cheaper than Whisper API)

### Frontend Architecture (Nuxt 3)

**State Management:**
- **Pinia Store** (`stores/useQuestionsStore.ts`) - Centralized state for questions workflow
  - Manages all question answers, evaluations, refinement data
  - Replaces Map-based local state with type-safe store
  - 15 getters, 19 actions for comprehensive state management
  - Supports both legacy and adaptive workflows

**Pages:**
- `pages/index.vue` - Landing page with job/CV input
- `pages/analyze.vue` - Multi-phase analysis interface with sidebar navigation
- `pages/domain-finder.vue` - Career domain finder standalone page
- `pages/ui-test.vue` - HireHub UI Components showcase/test page

**Composables (Vue Composition API):**
- `useAnalysisState.ts` - Global state management for analysis pipeline
- `useJobParser.ts` - Job description parsing
- `useCVParser.ts` - Resume/CV parsing
- `useScoreCalculator.ts` - Compatibility scoring
- `useAdaptiveQuestions.ts` - Adaptive questions workflow (LangGraph integration)
- `useQuestionGenerator.ts` - Legacy question generation (being phased out)
- `useVoiceRecorder.ts` - Audio recording for voice answers
- `useAudioTranscriber.ts` - Audio transcription (Parakeet/Whisper)
- `useAnswerSubmitter.ts` - Legacy answer analysis (being phased out)
- `useResumeRewriter.ts` - Resume rewriting
- `useDomainFinder.ts` - Career domain finder
- `useCoverLetterGenerator.ts` - Cover letter generation
- `useJobSearchQueryGenerator.ts` - Job search query generation
- `useSampleResumes.ts` - Sample resume data

**Components:**

*Application Components:*
- Results display: `JobParsingResult.vue`, `CVParsingResult.vue`, `ScoreResult.vue`, `QuestionsResult.vue`, `ResumeRewriteResult.vue`, `CoverLetterResult.vue`, `DomainFinderResult.vue`
- Adaptive Questions: `AdaptiveQuestionFlow.vue` - Main adaptive workflow UI, `AnswerQualityDisplay.vue` - Quality feedback display
- UI elements: `ProgressIndicator.vue`, `LoadingSpinner.vue`, `WaitingMessage.vue`, `AnalysisSidebar.vue`
- Input: `QuestionCard.vue`, `AnswerInput.vue` (with voice recording)
- Modals: `JobSearchQueriesModal.vue`
- Cards: `GapCard.vue` - Gap analysis display card

*HireHub UI Component Library (51 components in `components/base/`):*
- **Auto-imported with `Hb` prefix** - Use `<HbButton>`, `<HbModal>`, etc. without imports
- **Form Components (10):** HbInput, HbCheckbox, HbRadio, HbToggle, HbSelect, HbRange, HbDatepicker, HbDateInput, HbDateMonthYear, HbSingleCheckbox
- **UI Components (21):** HbButton, HbBadge, HbSpinner, HbIconSpinner, HbCard, HbCardSelect, HbModal, HbModalFullscreen, HbSidebar, HbBreadcrumbs, HbPagination, HbTabs, HbStepper, HbProgressBar, HbSegmentedProgress, HbSemicircleProgress, HbNotification, HbTooltip, HbPulsingIcon, HbPills, HbTagPills
- **Data Display (9):** HbTable, HbTableActions, HbAvatar, HbImg, HbVideo, HbFile, HbFileImage, HbIcon, HbCounter
- **Rich Content (7):** HbWysiwyg, HbImageEditor, HbProfilePicture, HbColor, HbColorPicker, HbColorPalette, HbColorPaletteLocked
- **Miscellaneous (4):** HbSlider, HbSnake, LanguageBar, SpellErrorMark
- **Design System:** CSS variables (`assets/css/var.css`), typography (Gabarito, Outfit, Wix Madefor Text), 51 SVG icons (`assets/icons/`)
- **Full TypeScript support** via `types/components.d.ts` and `types/globals.d.ts`
- See `frontend/HIREHUB_UI_INTEGRATION.md` for detailed documentation

### Data Flow

1. **User Input:** Job description + Resume (text or file upload)
2. **Parsing:** Both documents parsed to structured JSON (multilingual support)
3. **Scoring:** Hybrid approach (embeddings + rules + AI gaps)
4. **Adaptive Questions:** RAG-enhanced personalized questions based on gaps
   - User selects experience level for each question (Yes/No/Willing to Learn)
   - **LangGraph Workflow branches based on selection:**
     - **Yes** → Generate deep-dive prompts → User provides answers → Evaluate quality → Refine if needed
     - **No** → Skip to next question
     - **Willing to Learn** → Search SearXNG for resources → Generate learning plan → Save to PostgreSQL
5. **Analysis:** Extract hidden experience from answers, update CV, recalculate score
6. **Rewrite:** Generate optimized resume with ATS keywords + learned skills

### LangGraph Workflow Architecture

The adaptive questions system uses **LangGraph** for stateful workflow orchestration:

**State Machine Flow:**
```
START
  ↓
[Experience Check: Yes/No/Willing to Learn]
  ↓
  ┌────────────┬──────────────┬─────────────────┐
  ↓            ↓              ↓
YES          NO         WILLING_TO_LEARN
  ↓            ↓              ↓
DEEP_DIVE     END      SEARCH_RESOURCES
  ↓                           ↓
GENERATE_ANSWER      GENERATE_LEARNING_PLAN
  ↓                           ↓
EVALUATE_QUALITY           SAVE_PLAN
  ↓                           ↓
Quality >= 7?                END
  ↓
Yes → END
No → REFINE (max 2 iterations) → EVALUATE
```

**Key Components:**
- **State:** `AdaptiveAnswerState` - Tracks question, user inputs, quality scores, learning resources
- **Nodes:** `generate_deep_dive_prompts_node`, `search_learning_resources_node`, `evaluate_quality_node`, `refine_answer_node`
- **Routing:** Conditional edges based on experience level and quality score
- **Persistence:** MemorySaver for state checkpointing

**Benefits:**
- ✅ Complex multi-step workflows with branching logic
- ✅ State persistence across API calls
- ✅ Easy to visualize and debug workflow
- ✅ Supports human-in-the-loop interactions

### Frontend Testing Setup

The frontend uses **Vitest** for unit and integration testing:

**Test Structure:**
- `frontend/tests/unit/` - Composable unit tests
- `frontend/tests/integration/` - Full workflow integration tests
- `frontend/tests/setup.ts` - Test configuration and mocks

**Key Test Scenarios:**
1. **Refinement Flow** - Tests poor answer → quality evaluation → refinement → improved answer
2. **Max Iterations** - Ensures max 2 refinement cycles
3. **Context Preservation** - Verifies question context maintained across iterations
4. **API Mocking** - Uses `vi.mocked($fetch)` for isolated testing

See `frontend/TESTING_README.md` for detailed testing guide.

### Multi-language Support

The system supports English, French, German, and Spanish:
- All API endpoints accept `language` parameter
- Prompts in `shared_config.py` include language-specific instructions
- Soft skills matching uses language-specific stop words
- Output text (responsibilities, descriptions) translated to target language

### Scoring Methodology

**Category Weights:**
- Hard Skills: 30%
- Experience Level: 15%
- Industry Match: 15% (AI-extracted industries from company names)
- Role Similarity: 10% (AI-categorized job roles)
- Soft Skills: 10%
- Domain Expertise: 10%
- Portfolio Quality: 7%
- Location/Logistics: 3%

**Gap Categorization:**
- **Critical:** Deal-breakers (-8% to -20% impact) - e.g., missing primary tech stack, wrong experience level
- **Important:** Required but compensatable (-3% to -8%) - e.g., missing specific tools
- **Nice-to-have:** Bonuses (-1% to -3%) - e.g., "plus" skills
- **Logistical:** Non-technical barriers (variable) - e.g., location mismatch

## Common Development Patterns

### Adding New Prompt Templates

All prompts live in `Backend/app/config.py`. Follow existing patterns:
- Use TOON format for inputs to reduce tokens
- Include language parameter with language-specific instructions
- Provide clear examples and validation rules
- Use adaptive requirements based on score/quality

### Testing Scoring Changes

When modifying scoring logic, run these tests to ensure quality:
1. **Good Match Validation:** `python tests/integration/test_good_match_scoring.py` - Verifies good matches score 65%+
2. **Domain-Specific Tests:** `python tests/unit/test_web_dev_matching.py`, `test_database_management_matching.py` - Tests specific skill domains
3. **End-to-End Pipeline:** `python tests/integration/test_complete_pipeline.py` - Full pipeline validation
4. **Performance Check:** `python tests/unit/test_optimizations.py` - Ensures optimizations are maintained
5. **Multi-language:** `python tests/unit/test_multilanguage_soft_skills.py`, `test_cross_language_skills.py` - Tests language support

### Frontend State Management

The frontend uses composables for state management:
- Import `useAnalysisState()` to access/modify global analysis state
- Steps track: pending → loading → completed/error
- Each phase stores its results in the shared state
- Use `selectedStepId` to control which phase is displayed

### Using HireHub UI Components

All HireHub UI components are auto-imported with the `Hb` prefix:

```vue
<template>
  <!-- No imports needed - use components directly -->
  <HbButton variant="primary" @click="handleClick">Submit</HbButton>
  <HbModal v-model="showModal" title="Confirmation">
    <p>Are you sure?</p>
  </HbModal>
  <HbInput v-model="email" placeholder="Email" />
  <HbSpinner size="md" v-if="loading" />
</template>

<script setup lang="ts">
// Optional: Import types for TypeScript support
import type { HbButtonProps } from '~/types/components'

const showModal = ref(false)
const email = ref('')
const loading = ref(false)
</script>
```

**Component Variants:**
- **HbButton:** 11 variants (primary, secondary, outline, ghost, danger, etc.), 3 sizes, loading states
- **HbBadge:** 7 variants (primary, secondary, success, warning, danger, info, default)
- **HbModal:** 10 size variants (sm → 7xl)
- **HbSpinner:** 5 sizes (xs, sm, md, lg, xl)

See `frontend/HIREHUB_UI_INTEGRATION.md` and test page at http://localhost:3000/ui-test for examples.

### Adding New API Endpoints

1. Define Pydantic models for request/response in `app/main.py`
2. Add endpoint function with `@app.post()` decorator
3. Generate prompt using `app/config.py` functions
4. Call Gemini/OpenAI API with appropriate model and config
5. Parse response and return structured data
6. Create corresponding frontend composable in `frontend/composables/`

## Project Structure

```
Backend/
├── app/                    # Core FastAPI application
│   ├── main.py            # API endpoints (all phases + adaptive questions)
│   └── config.py          # Centralized prompt templates
├── core/                   # Business logic utilities
│   ├── adaptive_question_graph.py  # LangGraph workflow orchestration
│   ├── answer_flow_nodes.py       # LangGraph workflow nodes
│   ├── answer_flow_state.py       # LangGraph state definition
│   ├── searxng_client.py          # SearXNG search integration
│   ├── search_query_builder.py    # Search query generation
│   ├── resource_matcher.py        # Learning resource matching
│   ├── langchain_config.py        # LangChain/LangGraph setup
│   ├── embeddings.py              # Semantic similarity with caching
│   ├── cache.py                   # Embedding cache (Redis/in-memory)
│   ├── gemini_cache.py            # Gemini prompt caching
│   ├── vector_store.py            # Qdrant RAG for questions
│   └── text_processing.py         # Text normalization
├── formats/                # Data format handlers
│   └── toon.py            # TOON format (token-optimized)
├── parakeet-service/       # GPU speech-to-text microservice
│   ├── app.py             # Flask API for Parakeet
│   ├── Dockerfile         # GPU-enabled container
│   ├── requirements.txt   # Python dependencies
│   └── README.md          # Setup and usage guide
├── tests/                  # Test suite
│   ├── integration/       # Full pipeline tests
│   ├── unit/              # Component tests
│   └── debug/             # Debug/troubleshooting scripts
├── scripts/                # Benchmarking tools
│   ├── benchmark_toon.py  # TOON format benchmark
│   └── benchmark_json.py  # JSON format comparison
├── data/
│   ├── samples/           # Sample CVs and job descriptions
│   └── outputs/           # Generated JSON outputs
└── docker-compose.yml      # Multi-service orchestration (DB, Qdrant, SearXNG, API, Parakeet)

frontend/
├── pages/
│   ├── index.vue          # Landing page
│   ├── analyze.vue        # Main analysis interface
│   ├── domain-finder.vue  # Career domain finder
│   ├── ui-test.vue        # HireHub UI Components showcase
│   └── skeleton.vue       # UI skeleton/loading states
├── components/
│   ├── base/              # HireHub UI Components (51 components, auto-imported with Hb prefix)
│   ├── adaptive-questions/  # Adaptive questions workflow components
│   ├── results/           # Result display components
│   ├── modals/            # Modal components
│   ├── learning/          # Learning resource components
│   └── cards/             # Card components (GapCard, etc.)
├── composables/           # Composition API composables
│   ├── useAdaptiveQuestions.ts     # LangGraph workflow client
│   └── ...                # Other composables
├── assets/
│   ├── css/
│   │   ├── var.css        # HireHub UI CSS variables (design tokens)
│   │   └── main.css       # HireHub UI base styles
│   └── icons/             # 51 SVG icons for HbIcon component
├── types/
│   ├── components.d.ts    # HireHub UI component type definitions
│   ├── globals.d.ts       # Global TypeScript types
│   └── adaptive-questions.ts  # Adaptive questions types
├── tests/                 # Test suite
│   ├── setup.ts           # Test configuration
│   ├── unit/              # Composable unit tests
│   └── integration/       # Workflow integration tests
├── stores/
│   └── useQuestionsStore.ts  # Pinia store for questions workflow
├── vitest.config.ts       # Vitest configuration
├── TESTING_README.md      # Testing documentation
├── HIREHUB_UI_INTEGRATION.md  # HireHub UI Components integration guide
└── utils/                 # Frontend utilities

docs/                       # Documentation
├── pipeline.md            # Full pipeline example with data
├── TOON_FORMAT_EXPLAINED.md  # TOON format guide
└── TOON_IMPROVEMENTS.md   # TOON optimization notes

hirehub-ui-components/     # Original UI component library source
├── README.md              # Component library documentation
├── MIGRATION_GUIDE.md     # Migration guide from original library
└── INDEX.md               # Component catalog and reference

Root-level test scripts:   # Quick prototyping tests
├── test_*.py              # Various feature tests
└── debug_*.py             # Debug scripts
```

## Debugging and Monitoring

### Cache Statistics

Monitor cache performance to optimize system efficiency:

```bash
# Embedding cache stats (Redis or in-memory)
curl http://localhost:8001/api/cache/stats

# Gemini prompt cache stats
curl http://localhost:8001/api/prompt-cache/stats
```

### Parakeet Service Health

```bash
# Check Parakeet service status
curl http://localhost:8002/health

# View Parakeet logs
docker-compose logs -f parakeet

# Monitor GPU usage
nvidia-smi
# or continuously: watch -n 1 nvidia-smi
```

### SearXNG Service Health

```bash
# Check SearXNG status
curl http://localhost:8888/healthz

# View SearXNG logs
docker-compose logs -f searxng

# Test search functionality
curl "http://localhost:8888/search?q=Python+tutorial&format=json"
```

### Common Debugging Scenarios

1. **Slow scoring/parsing:**
   - Check cache hit rates via `/api/cache/stats`
   - Verify Redis connection if configured
   - Check Gemini prompt cache usage

2. **Transcription issues:**
   - Check Parakeet health: `curl http://localhost:8002/health`
   - View logs: `docker-compose logs parakeet`
   - Verify GPU availability: `nvidia-smi`
   - System falls back to OpenAI Whisper if Parakeet fails

3. **Inconsistent scoring:**
   - Use debug tests in `Backend/tests/debug/`
   - Run `debug_scoring_details.py` to see score breakdowns
   - Check `debug_embedding_similarity.py` for similarity issues

4. **TOON parsing errors:**
   - Check LLM array count validation (parser auto-fixes common errors)
   - Verify `{skill,priority}` format in hard_skills arrays
   - See `docs/TOON_FORMAT_EXPLAINED.md` for format rules

5. **Adaptive questions workflow issues:**
   - Check LangGraph state persistence (workflow uses MemorySaver)
   - Verify SearXNG is running for "Willing to Learn" flow
   - Check PostgreSQL connection for learning plan storage
   - Review quality evaluation thresholds (score >= 7 is acceptable)
   - Max 2 refinement iterations before accepting answer

6. **Frontend tests failing:**
   - Run `npm run test:ui` to visually debug in browser
   - Check mock responses in `frontend/tests/setup.ts`
   - Verify API endpoint URLs match backend routes
   - See `frontend/TESTING_README.md` for troubleshooting

7. **TypeScript errors after editing components:**
   - Always run `npx nuxi typecheck` after editing Vue/TypeScript files
   - Check type definitions in `types/components.d.ts` and `types/globals.d.ts`
   - Ensure component props match type interfaces

8. **HireHub UI Components not appearing:**
   - Verify `components/base/` directory contains all components
   - Check `nuxt.config.ts` has correct component auto-import configuration
   - Ensure CSS files are imported in `nuxt.config.ts` css array
   - View test page at http://localhost:3000/ui-test to verify integration

## Important Notes

- **Token Optimization:** Always use TOON format for CV/JD in prompts (see `formats/toon.py` and `docs/TOON_FORMAT_EXPLAINED.md`)
  - TOON reduces tokens by 40-50% vs JSON
  - Parser automatically fixes LLM counting errors in array brackets
- **Caching Strategy:**
  - **Embedding Cache:** Two-tier (in-memory + Redis optional) - clear when testing similarity changes
  - **Prompt Cache:** Gemini context caching for repeated system prompts - check stats via `/api/prompt-cache/stats`
- **RAG Context:** Questions improve over time as users submit answers (stored in Qdrant vector DB)
- **Gemini Models:**
  - Use `gemini-2.5-flash-lite` for speed (parsing, questions)
  - Use `gemini-2.0-flash-exp` for quality (gap analysis, rewriting)
- **Speech-to-Text:**
  - Parakeet (self-hosted GPU) is 10x faster and 95% cheaper
  - Automatically falls back to OpenAI Whisper if Parakeet unavailable
- **LangGraph Workflow:**
  - Adaptive questions use stateful workflows with branching logic
  - State persisted via MemorySaver (in-memory checkpointing)
  - Quality threshold: score >= 7 is acceptable, otherwise refine (max 2 iterations)
  - "Willing to Learn" flow requires SearXNG and PostgreSQL
- **Learning Resources:**
  - SearXNG provides privacy-focused meta-search for learning resources
  - PostgreSQL stores user learning plans for future reference
  - Resources matched using semantic similarity and recency ranking
- **Migration Path:**
  - Legacy `/api/generate-questions` and `/api/submit-answers` being phased out
  - New endpoints under `/api/adaptive-questions/*` use LangGraph workflow
  - Both systems currently coexist for backward compatibility
- **HireHub UI Components:**
  - 51 components auto-imported with `Hb` prefix (no manual imports needed)
  - Complete design system with CSS variables, typography, and icons
  - Full TypeScript support via `types/components.d.ts`
  - See `frontend/HIREHUB_UI_INTEGRATION.md` for integration details
  - Test page at http://localhost:3000/ui-test shows all components
- **Testing:**
  - Frontend tests use Vitest with mocked API calls
  - Backend tests organized by type (unit/integration/debug)
  - Root-level `test_*.py` files are for rapid prototyping
  - Always run `npx nuxi typecheck` after editing Vue/TypeScript files
- **Error Handling:** All API endpoints include try/except with HTTPException
- **Validation:** Input validation on both frontend and backend (min 50 chars for job/CV)
