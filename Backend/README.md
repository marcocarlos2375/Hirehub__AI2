# HireHubAI Backend

AI-powered job application optimization system that analyzes CV/resume compatibility with job descriptions using LLMs and semantic embeddings.

## Features

- **Document Parsing**: Extract structured data from job descriptions and resumes (multilingual)
- **Compatibility Scoring**: Hybrid approach using vector embeddings + rule-based scoring
- **Smart Questions**: RAG-enhanced personalized questions to uncover hidden experience
- **Resume Rewriting**: Generate ATS-optimized resumes with insights from user answers
- **Voice Support**: Whisper-powered audio transcription for voice answers

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for Qdrant vector database)
- Google Gemini API key
- OpenAI API key

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Running Locally

```bash
# Start Qdrant vector database
docker-compose up qdrant -d

# Run API server (development mode with auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at: http://localhost:8000
API documentation (Swagger): http://localhost:8000/docs

### Running with Docker Compose

```bash
# Start all services (API + Qdrant)
docker-compose up

# API available at http://localhost:8001
# Qdrant dashboard at http://localhost:6333/dashboard
```

## Project Structure

```
Backend/
├── app/                    # Core FastAPI application
│   ├── main.py            # API endpoints
│   └── config.py          # Prompt templates
├── core/                   # Business logic utilities
│   ├── embeddings.py      # Semantic similarity & embedding cache
│   ├── cache.py           # Two-tier caching (in-memory + Redis)
│   ├── vector_store.py    # Qdrant RAG integration
│   └── text_processing.py # Text utilities
├── formats/                # Data format handlers
│   └── toon.py            # TOON format (40-50% token reduction)
├── tests/
│   ├── integration/       # Integration tests
│   ├── unit/              # Unit tests
│   └── debug/             # Debug scripts
├── scripts/                # Benchmarks & standalone tools
├── data/
│   ├── samples/           # Sample data files
│   └── outputs/           # Generated outputs
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker image configuration
└── docker-compose.yml     # Docker Compose services
```

## API Endpoints

### Document Parsing
- `POST /api/parse` - Parse job description
- `POST /api/parse-cv` - Parse resume/CV

### Analysis
- `POST /api/calculate-score` - Calculate compatibility score (Phase 3)
- `POST /api/generate-questions` - Generate personalized questions (Phase 4)

### User Interaction
- `POST /api/transcribe-audio` - Transcribe voice answers (Whisper)
- `POST /api/submit-answers` - Analyze answers and update CV

### Resume Optimization
- `POST /api/rewrite-resume` - Generate optimized resume (Phase 5)

### Benchmarking
- `POST /benchmark/gemini` - Benchmark Gemini 2.0 Flash Lite
- `POST /benchmark/gpt35` - Benchmark GPT-3.5-Turbo
- `POST /benchmark/compare` - Compare all models

## Running Tests

```bash
# Integration tests
python tests/integration/test_complete_pipeline.py
python tests/integration/test_good_match_scoring.py

# Unit tests
python tests/unit/test_optimizations.py
python tests/unit/test_multilanguage_soft_skills.py

# Debug scripts
python tests/debug/debug_scoring_details.py
```

## Performance Optimizations

1. **TOON Format**: 40-50% token reduction vs JSON
2. **Hybrid Scoring**: Category scores via embeddings/rules (instant) vs Gemini (~4s saved)
3. **Embedding Cache**: Two-tier (in-memory + Redis) for 90%+ speedup on cache hits
4. **Batch Embeddings**: Parallel generation (3-4x faster)
5. **HTTP/2**: Persistent connections (30-50% faster API calls)
6. **Compressed Prompts**: Minimal prompts for Gemini (~60% smaller)

## Supported Languages

- English
- French
- German
- Spanish

All parsing, scoring, and question generation support multiple languages.

## Technology Stack

- **Framework**: FastAPI
- **LLMs**: Google Gemini (2.5 Flash-Lite, 2.0 Flash-Exp), OpenAI (GPT-3.5-Turbo, GPT-4o-Mini, Whisper)
- **Embeddings**: Google text-embedding-004
- **Vector DB**: Qdrant
- **Cache**: In-memory LRU + Redis (optional)
- **Format**: TOON (custom token-optimized format)

## Environment Variables

See `.env.example` for required and optional environment variables.

**Required:**
- `GEMINI_API_KEY` - Google Gemini API key
- `OPENAI_API_KEY` - OpenAI API key

**Optional:**
- `REDIS_URL` - Redis URL for embedding cache (falls back to in-memory if not set)

## Development

### Adding New Endpoints

1. Define Pydantic models in `app/main.py`
2. Add endpoint with `@app.post()` decorator
3. Generate prompt using `app/config.py` functions
4. Call LLM API and parse response

### Adding New Prompts

All prompts are centralized in `app/config.py`. Follow existing patterns:
- Use TOON format for inputs
- Include language parameter
- Provide examples and validation rules

### Debugging

Debug scripts are available in `tests/debug/`:
- `debug_scoring_details.py` - Debug domain/industry scoring
- `debug_embedding_similarity.py` - See actual similarity scores
- `debug_industry_extraction.py` - Test AI industry extraction

## License

[Your License Here]

## Support

For issues and questions, please refer to the main project documentation.
