 HireHub AI Pipeline - Simple Explanation

  Let me explain how the complete pipeline works step-by-step:

  📄 Step 1: Extract Text from Resume

  Tool: PyMuPDF (for PDFs) or python-docx (for Word docs)
  - User uploads CV/Resume (PDF or DOCX)
  - Extract raw text from the document
  - Location: backend/app/main.py (file upload handling)

  🧠 Step 2: Parse Resume with Gemini

  Endpoint: /api/parse-cv
  AI Model: Google Gemini 2.0 Flash-Exp
  - Send raw resume text to Gemini with structured prompt
  - Extract:
    - Personal info (name, email, phone, location, LinkedIn, GitHub)
    - Professional summary
    - Skills (technical, tools, soft skills)
    - Work experience with achievements
    - Education
    - Projects
    - Certifications
    - Languages
    - intership
    - publication
  - Output: Structured JSON (see /tmp/cv_result.json)
  - Time: ~4-7 seconds

  📋 Step 3: Parse Job Description with Gemini

  Endpoint: /api/parse-jd
  AI Model: Google Gemini 2.0 Flash-Exp
  - User provides job description text
  - Send to Gemini with structured prompt
  - Extract:
    - Company name & position title
    - Location, work mode, salary range
    - Required experience level
    - Hard skills (with priority: critical/important/nice)
    - Soft skills
    - Responsibilities
    - Tech stack
    - Domain expertise
    - Implicit requirements (things not explicitly stated)
    - Company culture signals
    - ATS keywords
  - Output: Structured JSON (see example above)
  - Time: ~4-5 seconds

  🎯 Step 4: Calculate Compatibility Score

  Endpoint: /api/calculate-score
  AI Model: Google Gemini 2.0 Flash-Exp
  - Compare parsed CV vs parsed JD
  - Gemini analyzes:
    - Skills match (technical & soft)
    - Experience level alignment
    - Domain expertise overlap
    - Responsibilities alignment
  - Output:
    - Overall compatibility score (0-100)
    - Score breakdown by category
    - Gaps (what's missing)
    - Strengths (what matches well)
  - Time: ~8-10 seconds (currently disabled for performance)

  ❓ Step 5: Generate Smart Questions

  Endpoint: /api/generate-questions
  AI Model: Google Gemini 2.0 Flash-Exp
  Vector DB: Qdrant (for RAG - Retrieval Augmented Generation)
  - Based on gaps identified, generate 5-8 questions
  - Questions help uncover "hidden experience"
  - Each question has:
    - The question text
    - Why it's being asked
    - Suggested answer template
  - Uses RAG: Searches Qdrant for similar past experiences
  - Output: Array of question objects
  - Time: ~1.8 seconds

  🔄 Step 6: Optimize CV Based on Answers

  Endpoint: /api/optimize-cv
  AI Model: Google Gemini 2.0 Flash-Exp
  - User answers the smart questions
  - Gemini takes:
    - Original parsed CV
    - Job description requirements
    - User's answers to questions
  - Regenerates CV sections to:
    - Incorporate hidden experience from answers
    - Align better with job requirements
    - Add relevant keywords
    - Strengthen weak areas
  - Output: Optimized CV JSON structure
  - Time: ~6-8 seconds

  💼 Step 7: Generate Cover Letter

  Endpoint: /api/generate-cover-letter
  AI Model: Google Gemini 2.0 Flash-Exp
  - Takes optimized CV + job description + user answers
  - Generates personalized cover letter with:
    - Strong opening paragraph
    - 2-3 body paragraphs highlighting relevant experience
    - Closing paragraph
    - Professional tone matching company culture
  - Output: Plain text cover letter
  - Time: ~5-7 seconds

  🎤 Bonus: Voice Transcription

  Endpoint: /api/transcribe
  AI Model: OpenAI Whisper API
  - User can record audio answers instead of typing
  - Supports French, English, German, Spanish
  - Transcribes audio to text
  - Output: Transcribed text
  - Cost: ~$0.006/minute

  ---
  📊 Complete Flow Diagram:

  ┌─────────────────┐
  │  User uploads   │
  │  CV + Job Desc  │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Extract text    │
  │ (PyMuPDF/docx)  │
  └────────┬────────┘
           │
           ├──────────────────┬──────────────────┐
           ▼                  ▼
  ┌─────────────────┐  ┌─────────────────┐
  │  Parse CV       │  │  Parse JD       │
  │  (Gemini API)   │  │  (Gemini API)   │
  │  ~6s            │  │  ~4s            │
  └────────┬────────┘  └────────┬────────┘
           │                    │
           └──────────┬─────────┘
                      ▼
           ┌─────────────────┐
           │ Calculate Score │  (Optional - disabled)
           │  (Gemini API)   │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ Generate Qs     │
           │ (Gemini + RAG)  │
           │  ~1.8s          │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ User answers    │
           │ (Text or Voice) │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ Optimize CV     │
           │  (Gemini API)   │
           │  ~7s            │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ Generate Cover  │
           │  (Gemini API)   │
           │  ~6s            │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ Download final  │
           │ CV + Cover PDF  │
           └─────────────────┘

  🔑 Key Technologies:

  1. Google Gemini 2.0 Flash-Exp - All AI text generation & parsing
  2. Qdrant Vector DB - Stores CV/JD embeddings for RAG
  3. Redis - Caches API responses for speed
  4. Sentence Transformers - Creates embeddings for semantic search
  5. OpenAI Whisper API - Voice transcription
  6. FastAPI - All endpoints are standalone

  ⚡ Performance:

  - Total time (without scoring): ~25-30 seconds
  - With caching: Follow-up requests ~0.25s per endpoint
  - Bottleneck: Gemini API calls (sequential)