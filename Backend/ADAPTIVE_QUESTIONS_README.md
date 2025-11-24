# Adaptive Question System - Implementation Guide

## Overview

A complete LangChain + LangGraph-based intelligent question answering system that adapts to user experience levels and provides personalized learning paths.

### Problem Solved

The original system couldn't handle users without experience. This new system:
- ✅ Detects if user has experience with a skill
- ✅ **Has Experience**: Generates deep-dive structured prompts → Creates professional answers → Validates quality → Refines if needed
- ✅ **No Experience/Willing to Learn**: Suggests learning resources (courses, projects, certifications) within 10 days → Saves personalized learning plans

## Architecture

```
User Question
    ↓
Experience Check (yes/no/willing_to_learn)
    ↓
┌───────────────┬──────────────────┐
YES             NO / WILLING        │
    ↓              ↓                │
Deep Dive     Learning Resources   │
Prompts       (Semantic Search)    │
    ↓                               │
Generate Answer                     │
    ↓                               │
Quality Check (1-10)                │
    ↓                               │
Score ≥ 7?                          │
  YES → Final Answer                │
  NO  → Refine (max 2x) → Recheck  │
    ↓                               │
└───────────────┴──────────────────┘
         ↓
    Complete
```

## Components Built

### Backend (Python)

#### 1. Database Schema (`migrations/001_learning_resources.sql`)
- **learning_resources** - 100+ curated courses, projects, certifications
- **user_learning_plans** - User's saved learning paths
- **answer_quality_logs** - Quality evaluation tracking
- **user_progress_tracking** - Learning progress monitoring

#### 2. SQLAlchemy Models (`models/learning_resources.py`)
- `LearningResource` - Resource model with validation
- `UserLearningPlan` - Plan model with status tracking
- Complete ORM with serialization methods

#### 3. LangChain Configuration (`core/langchain_config.py`)
- **3 LLM Modes**:
  - `fast` - gemini-2.5-flash-lite (quick operations)
  - `quality` - gemini-2.0-flash-exp (critical analysis)
  - `creative` - gemini-2.5-flash-lite temp=0.3 (answer generation)
- Google Embeddings (text-embedding-004, 768 dims)
- Qdrant vector stores (user_experiences, learning_resources)
- LangSmith tracing (optional)

#### 4. LangGraph Workflow (`core/adaptive_question_graph.py`)
State machine with 5 nodes:

**Node 1: Generate Deep Dive Prompts**
```python
# Generates 4-6 structured questions:
# - Where? (select: Work, Side Project, Course, etc.)
# - Duration? (text: "6 months, 2 projects")
# - Tools? (multiselect: specific technologies)
# - Achievement? (textarea: project description with metrics)
# - Metrics? (text: measurable impact)
```

**Node 2: Search Learning Resources**
```python
# Semantic search in Qdrant vector store
# Filters: duration_days ≤ 10, cost preference
# Returns: Top 5 ranked resources + timeline
```

**Node 3: Generate Professional Answer**
```python
# Creates compelling resume-ready answer from structured inputs
# Uses action verbs, includes technologies, adds metrics
# Example: "Developed a customer support chatbot using OpenAI GPT-3.5..."
```

**Node 4: Evaluate Quality**
```python
# Scores answer 1-10 on:
# - Specificity (not vague, includes tech/tools)
# - Evidence (metrics, results, timeframes)
# - Professional language (action verbs, clear)
# - Relevance (addresses the question/gap)
```

**Node 5: Refine Answer**
```python
# Improves answer based on quality feedback
# Max 2 refinement iterations
# Incorporates user's additional input
```

#### 5. Resource Matcher (`core/resource_matcher.py`)

**Semantic Search**:
```python
matcher = get_resource_matcher()
result = matcher.find_resources(
    gap={'title': 'AWS Lambda', 'description': '...'},
    user_level='intermediate',
    max_days=10,
    cost_preference='any',
    limit=5
)
```

**Ranking Algorithm** (100 points total):
- Difficulty match: 30 points
- Rating (0-5 stars): 25 points
- Type diversity: 20 points (project > course > certification)
- Certificate availability: 15 points
- Cost: 10 points (free > freemium > paid)

**Timeline Generation**:
```
Day 1-3: AWS Lambda Serverless Development (course)
Day 4-8: Build a Serverless REST API (project)
Day 9-10: AWS Solutions Architect Prep (certification)
```

#### 6. API Endpoints (`app/main.py` lines 3022-3427)

**POST /api/adaptive-questions/start**
```json
Request:
{
  "question_id": "q1",
  "question_text": "Do you have experience with AWS Lambda?",
  "question_data": {...},
  "gap_info": {"title": "AWS Lambda Experience", ...},
  "user_id": "user123",
  "parsed_cv": {...},
  "parsed_jd": {...},
  "experience_check_response": "yes"  // or "no", "willing_to_learn"
}

Response (if yes):
{
  "question_id": "q1",
  "current_step": "deep_dive",
  "deep_dive_prompts": [
    {
      "id": "context",
      "type": "select",
      "question": "Where did you gain this experience?",
      "options": ["Work", "Side Project", "Online Course", ...],
      "required": true
    },
    // ... 4-6 more prompts
  ]
}

Response (if no/willing_to_learn):
{
  "question_id": "q1",
  "current_step": "resources",
  "suggested_resources": [
    {
      "id": "lr-001",
      "title": "AWS Lambda Serverless Development",
      "type": "course",
      "provider": "Udemy",
      "url": "https://...",
      "duration_days": 3,
      "difficulty": "intermediate",
      "cost": "paid",
      "skills_covered": ["AWS Lambda", "Serverless", ...],
      "rating": 4.6
    },
    // ... 4 more resources
  ],
  "resume_addition": "Currently expanding AWS Lambda expertise through hands-on learning (10-day program)"
}
```

**POST /api/adaptive-questions/submit-inputs**
```json
Request:
{
  "question_id": "q1",
  "structured_data": {
    "context": "Work",
    "duration": "6 months",
    "tools": ["AWS Lambda", "API Gateway", "DynamoDB"],
    "achievement": "Built a serverless REST API handling 1000 req/sec",
    "metrics": "Reduced infrastructure costs by 60%"
  }
}

Response:
{
  "question_id": "q1",
  "generated_answer": "Developed a serverless REST API using AWS Lambda, API Gateway, and DynamoDB, processing 1000 requests/second while reducing infrastructure costs by 60% over 6 months.",
  "quality_score": 9,
  "quality_strengths": ["Specific technologies", "Quantified metrics", "Professional language"],
  "final_answer": "...",  // if score ≥ 7
  "improvement_suggestions": [...]  // if score < 7
}
```

**POST /api/adaptive-questions/refine-answer**
- Refine answer with additional user input
- Max 2 iterations

**POST /api/adaptive-questions/get-learning-resources**
- Get resources for any gap
- Customize: user_level, max_days, cost_preference, limit

**POST /api/adaptive-questions/save-learning-plan**
- Save user's selected resources
- Track learning progress

**POST /api/adaptive-questions/get-learning-plans**
- Retrieve all user plans
- Filter by status: suggested, in_progress, completed, abandoned

### Frontend (Vue 3 + Nuxt)

#### 1. Composable (`composables/useAdaptiveQuestions.ts`)

```typescript
const {
  startAdaptiveQuestion,
  submitStructuredInputs,
  refineAnswer,
  getLearningResources,
  saveLearningPlan,
  getLearningPlans
} = useAdaptiveQuestions()

// Example: Start workflow
const response = await startAdaptiveQuestion(
  'q1',
  'Do you have AWS Lambda experience?',
  questionData,
  gapInfo,
  'user123',
  parsedCV,
  parsedJD,
  'yes'  // or 'no', 'willing_to_learn'
)

if (response.deep_dive_prompts) {
  // Show structured input form
} else if (response.suggested_resources) {
  // Show learning resources + timeline
}
```

#### 2. Component (`components/LearningResourceCard.vue`)

Displays learning resources with:
- Type badge (course/project/certification)
- Difficulty & cost indicators
- Rating & duration
- Skills covered (chips)
- Certificate indicator
- View resource button
- Add to plan button

## Data Seeding

### Learning Resources Database

**Location**: `Backend/seed_data/learning_resources.json`
**Count**: 100 curated resources

**Categories**:
- **Cloud/DevOps** (15): AWS, Docker, Kubernetes, Terraform, Jenkins, GitHub Actions
- **Backend** (20): Python, Node.js, Go, FastAPI, Django, NestJS, Spring Boot
- **Frontend** (18): React, Vue, Next.js, Angular, Svelte, Tailwind CSS
- **AI/ML** (12): LangChain, OpenAI, TensorFlow, PyTorch, Vector Databases
- **Databases** (10): PostgreSQL, MongoDB, Redis, Elasticsearch, Snowflake
- **Full-Stack** (15): E-commerce, Chat apps, Social media, Video streaming
- **Certifications** (10): AWS SAA, CKA, etc.

**Run Seeding**:
```bash
# After Docker container is ready
docker-compose exec api python3 scripts/seed_resources.py --clear

# Output:
# ✅ Loaded 100 resources from seed_data/learning_resources.json
# 📦 Seeding PostgreSQL database...
# ✅ Successfully seeded 100 resources to PostgreSQL
# 🔍 Seeding Qdrant vector store...
# ✅ Successfully seeded 100 resources to Qdrant
```

## Usage Examples

### Example 1: User with Experience

```typescript
// 1. Start workflow
const response = await startAdaptiveQuestion(
  'q_aws_lambda',
  'Do you have experience with AWS Lambda?',
  questionData,
  gapInfo,
  'user123',
  parsedCV,
  parsedJD,
  'yes'
)

// 2. Show deep dive prompts
response.deep_dive_prompts.forEach(prompt => {
  // Render form field based on prompt.type
  // - text: <input type="text">
  // - textarea: <textarea>
  // - select: <select><option>...</select>
  // - multiselect: <input type="checkbox">
})

// 3. Submit structured data
const answerResponse = await submitStructuredInputs('q_aws_lambda', {
  context: 'Work',
  duration: '1 year',
  tools: ['Lambda', 'API Gateway', 'DynamoDB'],
  achievement: 'Built a microservices architecture',
  metrics: 'Handled 10k req/min'
})

// 4. Check quality
if (answerResponse.final_answer) {
  // Quality ≥ 7, use final_answer
  addToResume(answerResponse.final_answer)
} else {
  // Quality < 7, show improvement suggestions
  showRefinementForm(answerResponse.improvement_suggestions)

  // 5. Refine if needed
  const refined = await refineAnswer('q_aws_lambda', additionalData)
}
```

### Example 2: User Without Experience

```typescript
// 1. Start workflow
const response = await startAdaptiveQuestion(
  'q_aws_lambda',
  'Do you have experience with AWS Lambda?',
  questionData,
  gapInfo,
  'user123',
  parsedCV,
  parsedJD,
  'willing_to_learn'
)

// 2. Display learning resources
response.suggested_resources.forEach(resource => {
  // Render LearningResourceCard component
  <LearningResourceCard
    :resource="resource"
    @add-to-plan="handleAddToPlan"
  />
})

// 3. Save learning plan
const selectedIds = ['lr-001', 'lr-002', 'lr-005']
const plan = await saveLearningPlan(
  'user123',
  gapInfo,
  selectedIds,
  'Will complete during next 2 weeks'
)

// 4. Add resume text
addToResume(response.resume_addition)
// "Currently expanding AWS Lambda expertise through hands-on learning (10-day program)"
```

## Quality Scoring Criteria

### Score 1-3: Very Weak
- Too vague, no specifics
- No technologies mentioned
- No measurable results

### Score 4-6: Needs Improvement
- Some details but missing key elements
- Vague time frames
- Generic descriptions

### Score 7-8: Good ✅
- Specific technologies listed
- Professional language with action verbs
- Clear time frames

### Score 9-10: Excellent ⭐
- Detailed with quantified metrics
- Compelling and professional
- Clear business impact

## Next Steps

1. **Run Database Migration**:
   ```bash
   docker-compose exec api psql $DATABASE_URL < migrations/001_learning_resources.sql
   ```

2. **Seed Learning Resources**:
   ```bash
   docker-compose exec api python3 scripts/seed_resources.py --clear
   ```

3. **Test API Endpoints**:
   ```bash
   # Test start workflow
   curl -X POST http://localhost:8001/api/adaptive-questions/start \
     -H "Content-Type: application/json" \
     -d '{
       "question_id": "test_q1",
       "question_text": "Do you have AWS Lambda experience?",
       "question_data": {},
       "gap_info": {"title": "AWS Lambda", "description": "Serverless computing"},
       "user_id": "test_user",
       "parsed_cv": {},
       "parsed_jd": {},
       "experience_check_response": "yes"
     }'
   ```

4. **Integrate into Frontend**:
   - Use `useAdaptiveQuestions()` composable
   - Display `LearningResourceCard` components
   - Handle workflow state transitions
   - Track user progress

## Performance Considerations

- **Semantic Search**: O(log n) with Qdrant HNSW index
- **Batch Embeddings**: 10 resources at a time to avoid rate limits
- **Caching**: LangChain caches identical prompts
- **Database Indexes**: UUID primary keys, foreign keys on user_id

## Future Enhancements

- [ ] Add progress tracking UI
- [ ] Send reminder notifications
- [ ] Gamification (badges, streaks)
- [ ] Social learning (share plans)
- [ ] Resource reviews/ratings
- [ ] Custom resource uploads
- [ ] AI tutor chat integration
