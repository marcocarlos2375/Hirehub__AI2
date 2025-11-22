# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered job application optimization system (HireHubAI) that analyzes CV/resume compatibility with job descriptions using LLMs and semantic embeddings. The system uses a multi-phase pipeline to parse documents, calculate compatibility scores, generate personalized questions, and rewrite resumes to improve job match rates.

**Key Technologies:**
- Backend: Python, FastAPI, Google Gemini API, OpenAI API
- Frontend: Nuxt 3 (Vue 3), TypeScript, Tailwind CSS
- Vector DB: Qdrant (for RAG-based question generation)
- Optimization: TOON format for token reduction, embedding caching

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

# Run with Docker Compose (includes Qdrant vector DB)
docker-compose up

# API will be available at http://localhost:8001
# Qdrant dashboard at http://localhost:6333/dashboard
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
```

### Running Tests

```bash
cd Backend

# Test complete pipeline
python test_complete_pipeline.py

# Test scoring optimizations
python test_optimizations.py

# Test specific features
python test_good_match_scoring.py
python test_detailed_gap_analysis.py
python test_resume_rewrite.py
python test_resume_rewrite_integration.py
```

## Environment Variables

The project requires API keys in `Backend/.env`:
- `GEMINI_API_KEY` - Google Gemini API key (required)
- `OPENAI_API_KEY` - OpenAI API key (required for Whisper transcription)
- `REDIS_URL` - Redis URL for embedding cache (optional, falls back to in-memory)

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

3. **Phase 4: Smart Questions (RAG-Enhanced)**
   - Generate 5-11 personalized questions based on gaps
   - Use Qdrant vector DB to find similar past experiences (RAG)
   - Support text or voice answers (Whisper transcription)
   - Extract "hidden experience" not in original CV

4. **Phase 5: Resume Rewriting**
   - Incorporate insights from user answers
   - Optimize for ATS keywords from job description
   - Generate both sample.json format (HTML, camelCase) and parsed format (plain text, snake_case)
   - Add new projects, skills, and enhance existing descriptions

### Backend Architecture

**Core API Endpoints (`Backend/app/main.py`):**
- `POST /api/parse` - Parse job description
- `POST /api/parse-cv` - Parse resume/CV
- `POST /api/calculate-score` - Calculate compatibility score (Phase 3)
- `POST /api/generate-questions` - Generate personalized questions (Phase 4)
- `POST /api/transcribe-audio` - Transcribe voice answers (Whisper)
- `POST /api/submit-answers` - Analyze answers and update CV
- `POST /api/rewrite-resume` - Generate optimized resume (Phase 5)

**Key Modules:**
- `app/main.py` - FastAPI application with all endpoints
- `app/config.py` - Centralized prompt templates for all phases
- `core/embeddings.py` - Semantic similarity with caching (2-tier: in-memory + Redis)
- `core/cache.py` - Embedding cache management
- `core/vector_store.py` - RAG vector database for question generation
- `core/text_processing.py` - Text normalization utilities
- `formats/toon.py` - TOON format conversion for 40-50% token reduction

**Performance Optimizations:**
1. **TOON Format:** Custom compressed format reducing tokens by 40-50% vs JSON
2. **Hybrid Scoring:** Category scores calculated via embeddings/rules (instant) rather than asking Gemini (~4s saved)
3. **Embedding Cache:** Two-tier caching (in-memory + Redis) for 90%+ speedup on cache hits
4. **Batch Embeddings:** Parallel embedding generation (3-4x faster)
5. **HTTP/2:** Persistent HTTP/2 client with connection pooling (30-50% faster API calls)
6. **Compressed Prompts:** Minimal prompts for Gemini (~60% smaller for gap analysis)

### Frontend Architecture (Nuxt 3)

**Pages:**
- `pages/index.vue` - Landing page with job/CV input
- `pages/analyze.vue` - Multi-phase analysis interface with sidebar navigation

**Composables (Vue Composition API):**
- `useAnalysisState.ts` - Global state management for analysis pipeline
- `useJobParser.ts` - Job description parsing
- `useCVParser.ts` - Resume/CV parsing
- `useScoreCalculator.ts` - Compatibility scoring
- `useQuestionGenerator.ts` - Question generation
- `useVoiceRecorder.ts` - Audio recording for voice answers
- `useAudioTranscriber.ts` - Whisper transcription
- `useAnswerSubmitter.ts` - Answer analysis
- `useResumeRewriter.ts` - Resume rewriting

**Components:**
- Results display: `JobParsingResult.vue`, `CVParsingResult.vue`, `ScoreResult.vue`, `QuestionsResult.vue`, `ResumeRewriteResult.vue`
- UI elements: `ProgressIndicator.vue`, `LoadingSpinner.vue`, `WaitingMessage.vue`, `AnalysisSidebar.vue`
- Input: `QuestionCard.vue`, `AnswerInput.vue` (with voice recording)

### Data Flow

1. **User Input:** Job description + Resume (text or file upload)
2. **Parsing:** Both documents parsed to structured JSON (multilingual support)
3. **Scoring:** Hybrid approach (embeddings + rules + AI gaps)
4. **Questions:** RAG-enhanced personalized questions based on gaps
5. **Answers:** User provides text/voice answers
6. **Analysis:** Extract hidden experience, update CV, recalculate score
7. **Rewrite:** Generate optimized resume with ATS keywords

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

When modifying scoring logic:
1. Run `python tests/integration/test_good_match_scoring.py` to verify good matches score 65%+
2. Run `python tests/unit/test_web_dev_matching.py` for domain-specific tests
3. Run `python tests/integration/test_complete_pipeline.py` for end-to-end validation
4. Check `python tests/unit/test_optimizations.py` to ensure performance improvements maintained

### Frontend State Management

The frontend uses composables for state management:
- Import `useAnalysisState()` to access/modify global analysis state
- Steps track: pending → loading → completed/error
- Each phase stores its results in the shared state
- Use `selectedStepId` to control which phase is displayed

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
│   ├── main.py            # API endpoints
│   └── config.py          # Prompt templates
├── core/                   # Business logic utilities
│   ├── embeddings.py      # Semantic similarity
│   ├── cache.py           # Embedding cache
│   ├── vector_store.py    # Qdrant RAG
│   └── text_processing.py # Text utilities
├── formats/                # Data format handlers
│   └── toon.py            # TOON format
├── tests/
│   ├── integration/       # Integration tests
│   ├── unit/              # Unit tests
│   └── debug/             # Debug scripts
├── scripts/                # Benchmarks
│   ├── benchmark_toon.py
│   └── benchmark_json.py
└── data/
    ├── samples/           # Sample data
    └── outputs/           # JSON outputs
```

## Important Notes

- **Token Optimization:** Always use TOON format for CV/JD in prompts (see `formats/toon.py`)
- **Caching:** Embeddings are cached - clear cache when testing similarity changes
- **RAG Context:** Questions improve over time as more users submit answers (stored in Qdrant)
- **Gemini Models:** Use `gemini-2.5-flash-lite` for speed, `gemini-2.0-flash-exp` for quality
- **Error Handling:** All API endpoints include try/except with HTTPException
- **Validation:** Input validation on both frontend and backend (min 50 chars for job/CV)
