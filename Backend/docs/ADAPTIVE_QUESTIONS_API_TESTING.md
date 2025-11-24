# Adaptive Questions API - Manual Testing Guide

Complete curl command reference for testing all 6 endpoints of the Adaptive Questions system.

## API Base URL

```bash
API_BASE_URL="http://localhost:8001"
```

## Test Data

```bash
TEST_USER_ID="test_user_$(date +%s)"
```

---

## Test 1: Start Workflow (User Has Experience)

When a user indicates they **have experience** with a skill, the system generates deep dive prompts to extract detailed information.

**Endpoint:** `POST /api/adaptive-questions/start`

**Request:**
```bash
curl -X POST http://localhost:8001/api/adaptive-questions/start \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "test_aws_yes",
    "question_text": "Do you have AWS Lambda experience?",
    "question_data": {},
    "gap_info": {
      "title": "AWS Lambda",
      "description": "Serverless computing with AWS Lambda"
    },
    "user_id": "test_user_001",
    "parsed_cv": {
      "skills": ["Python", "FastAPI"]
    },
    "parsed_jd": {
      "required_skills": ["AWS Lambda", "Python", "Serverless"]
    },
    "experience_check_response": "yes",
    "language": "english"
  }'
```

**Expected Response:**
```json
{
  "question_id": "test_aws_yes",
  "current_step": "deep_dive",
  "deep_dive_prompts": [
    {
      "id": "context",
      "type": "select",
      "question": "Where did you gain this AWS Lambda experience?",
      "options": ["Work", "Side Project", "Online Course", "Bootcamp", "University", "Open Source"],
      "required": true
    },
    {
      "id": "duration",
      "type": "text",
      "question": "How long have you been working with AWS Lambda? (e.g., '6 months, 3 projects')",
      "required": true
    },
    {
      "id": "tools",
      "type": "multiselect",
      "question": "Which AWS services and tools did you use with Lambda?",
      "options": ["API Gateway", "DynamoDB", "S3", "SNS", "SQS", "CloudWatch", "Step Functions"],
      "required": true
    },
    {
      "id": "achievement",
      "type": "textarea",
      "question": "Describe your most significant AWS Lambda achievement or project",
      "required": true
    },
    {
      "id": "metrics",
      "type": "text",
      "question": "What were the measurable results? (e.g., requests/second, cost savings, performance improvement)",
      "required": false
    }
  ]
}
```

**Validation:**
- ✅ `current_step` = "deep_dive"
- ✅ `deep_dive_prompts` contains 4-6 structured questions
- ✅ Each prompt has: id, type, question, required

---

## Test 2: Start Workflow (User Willing to Learn)

When a user indicates they **don't have experience** but are willing to learn, the system returns curated learning resources.

**Endpoint:** `POST /api/adaptive-questions/start`

**Request:**
```bash
curl -X POST http://localhost:8001/api/adaptive-questions/start \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "test_react_no",
    "question_text": "Do you have React experience?",
    "question_data": {},
    "gap_info": {
      "title": "React",
      "description": "Frontend JavaScript framework"
    },
    "user_id": "test_user_001",
    "parsed_cv": {
      "skills": ["HTML", "CSS", "JavaScript"]
    },
    "parsed_jd": {
      "required_skills": ["React", "Redux", "TypeScript"]
    },
    "experience_check_response": "willing_to_learn",
    "language": "english"
  }'
```

**Expected Response:**
```json
{
  "question_id": "test_react_no",
  "current_step": "resources",
  "suggested_resources": [
    {
      "id": "lr-015",
      "title": "React Complete Guide",
      "description": "Master React from basics to advanced...",
      "type": "course",
      "provider": "Udemy",
      "url": "https://www.udemy.com/course/react-complete/",
      "duration_days": 5,
      "difficulty": "beginner",
      "cost": "paid",
      "skills_covered": ["React", "JSX", "Hooks", "Context API", "Redux"],
      "prerequisites": [],
      "completion_certificate": true,
      "rating": 4.7,
      "language": "english",
      "score": 95
    }
  ],
  "timeline": [
    "Day 1-5: React Complete Guide (course)",
    "Day 6-9: Build a Todo App with React (project)",
    "Total: 9 days → Completion: Dec 3, 2025"
  ],
  "resume_addition": "Currently expanding React expertise through hands-on learning (9-day program including React Complete Guide course and practical project development)"
}
```

**Validation:**
- ✅ `current_step` = "resources"
- ✅ `suggested_resources` contains 3-5 learning resources
- ✅ Each resource has: title, type, duration_days, difficulty, score
- ✅ `timeline` shows learning path with dates
- ✅ `resume_addition` provides ready-to-use text

---

## Test 3: Submit Structured Inputs

Submit user's responses to deep dive prompts. System generates a professional answer and evaluates quality (1-10).

**Endpoint:** `POST /api/adaptive-questions/submit-inputs`

**Request:**
```bash
curl -X POST http://localhost:8001/api/adaptive-questions/submit-inputs \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "test_aws_yes",
    "structured_data": {
      "context": "Work",
      "duration": "6 months across 3 projects",
      "tools": ["AWS Lambda", "API Gateway", "DynamoDB", "Python", "CloudWatch"],
      "achievement": "Built a serverless REST API for processing customer data in real-time",
      "metrics": "Handled 5000 requests/minute, reduced infrastructure costs by 60%, improved response time to 200ms"
    }
  }'
```

**Expected Response (Score >= 7):**
```json
{
  "question_id": "test_aws_yes",
  "generated_answer": "Developed serverless REST API using AWS Lambda, API Gateway, and DynamoDB over 6 months across 3 production projects. Architected real-time customer data processing system handling 5000 requests/minute with 200ms average response time. Leveraged CloudWatch for monitoring and optimization. Reduced infrastructure costs by 60% through efficient Lambda function design and auto-scaling configuration.",
  "quality_score": 9,
  "quality_feedback": "Excellent answer with specific technologies, clear metrics, and compelling business impact.",
  "final_answer": true
}
```

**Expected Response (Score < 7 - Needs Refinement):**
```json
{
  "question_id": "test_aws_yes",
  "generated_answer": "Worked with AWS Lambda to build APIs...",
  "quality_score": 5,
  "quality_feedback": "Answer needs improvement. Missing specific metrics and business impact.",
  "improvement_suggestions": [
    "Add specific performance metrics (requests/second, latency)",
    "Quantify business impact (cost savings, efficiency gains)",
    "Mention additional AWS services used (DynamoDB, CloudWatch)"
  ],
  "final_answer": false
}
```

**Validation:**
- ✅ `quality_score` between 1-10
- ✅ If score >= 7: `final_answer` = true
- ✅ If score < 7: `improvement_suggestions` provided
- ✅ `generated_answer` uses professional language and specific technologies

---

## Test 4: Refine Answer

Used when initial answer quality score is below 7. User provides additional details to improve the answer.

**Endpoint:** `POST /api/adaptive-questions/refine-answer`

**Request:**
```bash
curl -X POST http://localhost:8001/api/adaptive-questions/refine-answer \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "test_aws_yes",
    "additional_data": {
      "specific_technologies": "Used Terraform for infrastructure as code, implemented CI/CD with GitHub Actions",
      "business_impact": "Enabled real-time data processing for 50,000 active users, reduced manual processing time from 4 hours to 2 minutes",
      "challenges_overcome": "Optimized cold starts from 3 seconds to 500ms using provisioned concurrency and connection pooling"
    }
  }'
```

**Expected Response:**
```json
{
  "question_id": "test_aws_yes",
  "refined_answer": "Architected and deployed serverless REST API using AWS Lambda, API Gateway, and DynamoDB, leveraging Terraform for infrastructure as code and GitHub Actions for CI/CD automation. Processed real-time customer data for 50,000 active users at 5000 requests/minute with 200ms average response time. Optimized Lambda cold starts from 3s to 500ms through provisioned concurrency and connection pooling. Reduced manual data processing time from 4 hours to 2 minutes and infrastructure costs by 60%, delivering significant operational efficiency gains.",
  "quality_score": 9,
  "quality_feedback": "Excellent improvement! Answer now includes specific technologies, quantified business impact, and technical optimizations.",
  "final_answer": true,
  "improvement_made": true
}
```

**Validation:**
- ✅ `refined_answer` incorporates additional_data
- ✅ `quality_score` improved from previous submission
- ✅ `improvement_made` = true
- ✅ More specific technologies and metrics mentioned

---

## Test 5: Get Learning Resources (On-Demand)

Retrieve learning resources for any skill gap, independent of the workflow. Useful for exploring learning options.

**Endpoint:** `POST /api/adaptive-questions/get-learning-resources`

**Request:**
```bash
curl -X POST http://localhost:8001/api/adaptive-questions/get-learning-resources \
  -H "Content-Type: application/json" \
  -d '{
    "gap": {
      "title": "Docker & Kubernetes",
      "description": "Container orchestration and microservices deployment"
    },
    "user_level": "beginner",
    "max_days": 7,
    "cost_preference": "free",
    "limit": 5
  }'
```

**Expected Response:**
```json
{
  "resources": [
    {
      "id": "lr-003",
      "title": "Docker and Kubernetes Fundamentals",
      "type": "course",
      "provider": "Coursera",
      "duration_days": 7,
      "difficulty": "intermediate",
      "cost": "freemium",
      "skills_covered": ["Docker", "Kubernetes", "Microservices", "CI/CD", "DevOps"],
      "rating": 4.7,
      "score": 92,
      "ranking_breakdown": {
        "difficulty_match": 30,
        "rating": 23,
        "type_diversity": 20,
        "certificate": 15,
        "cost": 4
      }
    }
  ],
  "timeline": [
    "Day 1-7: Docker and Kubernetes Fundamentals (course)",
    "Total: 7 days → Completion: Dec 1, 2025"
  ],
  "total_duration_days": 7
}
```

**Validation:**
- ✅ Returns resources matching filters (user_level, max_days, cost_preference)
- ✅ Resources sorted by score (0-100)
- ✅ Timeline shows completion dates
- ✅ Each resource has ranking_breakdown explaining score

---

## Test 6: Save Learning Plan

Save a user's selected learning resources as a learning plan for tracking progress.

**Endpoint:** `POST /api/adaptive-questions/save-learning-plan`

**Request:**
```bash
curl -X POST http://localhost:8001/api/adaptive-questions/save-learning-plan \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "gap_info": {
      "title": "Python",
      "description": "Python programming fundamentals"
    },
    "selected_resource_ids": ["lr-050", "lr-051", "lr-055"],
    "notes": "Will complete during Q1 2025. Focus on FastAPI and data structures."
  }'
```

**Expected Response:**
```json
{
  "plan_id": "plan-uuid-here",
  "status": "suggested",
  "message": "Learning plan saved successfully",
  "resources_count": 3,
  "total_duration_days": 12
}
```

**Validation:**
- ✅ Returns unique `plan_id`
- ✅ `status` = "suggested" (can be updated to "in_progress" or "completed")
- ✅ `resources_count` matches selected_resource_ids length

---

## Test 7: Get User Learning Plans

Retrieve all learning plans for a specific user, optionally filtered by status.

**Endpoint:** `POST /api/adaptive-questions/get-learning-plans`

**Request:**
```bash
# Get all plans for user
curl -X POST http://localhost:8001/api/adaptive-questions/get-learning-plans \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001"
  }'

# Get only "in_progress" plans
curl -X POST http://localhost:8001/api/adaptive-questions/get-learning-plans \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "status": "in_progress"
  }'
```

**Expected Response:**
```json
{
  "plans": [
    {
      "plan_id": "plan-uuid-1",
      "gap_title": "Python",
      "gap_description": "Python programming fundamentals",
      "status": "suggested",
      "created_at": "2025-11-24T10:30:00Z",
      "notes": "Will complete during Q1 2025. Focus on FastAPI and data structures.",
      "resources": [
        {
          "id": "lr-050",
          "title": "Python for Beginners",
          "type": "course",
          "duration_days": 5
        },
        {
          "id": "lr-051",
          "title": "Build a REST API with FastAPI",
          "type": "project",
          "duration_days": 4
        },
        {
          "id": "lr-055",
          "title": "Python Data Structures",
          "type": "course",
          "duration_days": 3
        }
      ],
      "total_duration_days": 12
    }
  ],
  "total_plans": 1
}
```

**Validation:**
- ✅ Returns all plans for the user
- ✅ Can filter by status: "suggested", "in_progress", "completed"
- ✅ Each plan includes resources array
- ✅ Sorted by created_at (newest first)

---

## Complete Test Workflow Example

Here's a complete workflow combining multiple endpoints:

```bash
# Step 1: Start workflow (user willing to learn React)
curl -X POST http://localhost:8001/api/adaptive-questions/start \
  -H "Content-Type: application/json" \
  -d '{"question_id": "react_gap", "gap_info": {"title": "React"}, "user_id": "user_123", "experience_check_response": "willing_to_learn", "parsed_cv": {}, "parsed_jd": {}, "question_text": "React?", "question_data": {}, "language": "english"}'

# Step 2: Get suggested resources (returns 5 resources)
# Response includes resource IDs like ["lr-015", "lr-020", "lr-025"]

# Step 3: Save selected resources to learning plan
curl -X POST http://localhost:8001/api/adaptive-questions/save-learning-plan \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "gap_info": {"title": "React"}, "selected_resource_ids": ["lr-015", "lr-020"], "notes": "Start with course, then project"}'

# Step 4: View all learning plans
curl -X POST http://localhost:8001/api/adaptive-questions/get-learning-plans \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123"}'
```

---

## Error Handling

All endpoints return standard error responses:

**400 Bad Request:**
```json
{
  "detail": "Validation error: missing required field 'question_id'"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error generating deep dive prompts: LLM API error"
}
```

---

## Quality Scoring Criteria

The system evaluates answer quality (1-10) based on:

| Criteria | Weight | Description |
|----------|--------|-------------|
| **Specificity** | 30% | Technologies/tools mentioned, not vague |
| **Evidence** | 30% | Metrics, results, timeframes |
| **Professional Language** | 20% | Action verbs (Built, Developed), clear |
| **Relevance** | 20% | Addresses the gap, aligns with job requirements |

**Score Ranges:**
- **9-10**: Excellent (detailed, quantified, compelling)
- **7-8**: Good (specific technologies, professional, clear)
- **4-6**: Needs improvement (some details, missing key elements)
- **1-3**: Very weak (too vague, no specifics, no metrics)

---

## Tips for Testing

1. **Use unique user IDs**: Generate unique user_id per test run to avoid conflicts
   ```bash
   TEST_USER_ID="test_user_$(date +%s)"
   ```

2. **Save responses**: Pipe responses to files for inspection
   ```bash
   curl ... > response_test1.json
   ```

3. **Pretty print JSON**: Use `jq` for readable output
   ```bash
   curl ... | jq '.'
   ```

4. **Check API health** before testing:
   ```bash
   curl http://localhost:8001/health
   ```

5. **Monitor logs** during testing:
   ```bash
   docker-compose logs -f api
   ```

---

## Automated Testing

Run the complete automated test suite:

```bash
cd /Users/carlosid/PycharmProjects/test/Backend
python tests/integration/test_adaptive_questions_endpoints.py
```

This runs all 7 tests with colored output, response validation, and a comprehensive summary report.
