# Adaptive Questions System - Testing Guide

## 🎯 Overview

The Adaptive Questions system is now fully integrated into the HireHubAI platform. This guide provides comprehensive testing procedures for all three workflow paths.

## 📋 Prerequisites

### Backend Requirements
1. **Start the services:**
   ```bash
   cd Backend
   docker-compose up -d
   ```

2. **Verify services are running:**
   ```bash
   # Check API
   curl http://localhost:8001/health

   # Check Qdrant (vector DB)
   curl http://localhost:6333/health
   ```

3. **Seed learning resources (if not already done):**
   ```bash
   docker-compose exec api python scripts/seed_resources.py
   ```

### Frontend Requirements
1. **Start the development server:**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Access the application:**
   - Open: http://localhost:3000

## 🧪 Test Scenarios

### Test 1: Deep Dive Path (User HAS Experience) ⭐

**Objective:** Test the intelligent question-answer flow with quality evaluation and refinement.

#### Steps:
1. **Upload Test Data:**
   - Navigate to http://localhost:3000
   - Use sample resume: `Backend/data/samples/cv_web_dev.txt`
   - Use sample job: `Backend/data/samples/jd_senior_web_dev.txt`
   - Language: English
   - Click "Analyze Compatibility"

2. **Wait for Analysis:**
   - Phase 1-2: Parsing (5-10s)
   - Phase 3: Scoring (8-12s)
   - Phase 4: Question generation (3-5s)
   - Navigate to "Smart Questions" tab

3. **Enable Adaptive Mode:**
   - Look for the toggle switch at the top right
   - Toggle from "Traditional Mode" to "Adaptive Mode"
   - You should see the info box explaining the three paths

4. **For the first Critical question:**
   - Click "Yes, I have experience" (green button)
   - **Deep Dive Form appears** with 4-6 questions

5. **Scenario A: Weak Answers (Testing Refinement)**
   Fill in VAGUE responses:
   ```
   Context: Work
   Duration: A few months
   Tools: Basic stuff
   Achievement: Made some functions
   Metrics: (leave empty)
   ```
   - Click "Generate Professional Answer"
   - **Expected:** Quality score 3-5/10 (red/amber badge)
   - You should see issues like "Too vague", "Missing metrics"
   - Click "Refine Answer"

6. **Add More Details:**
   ```
   Duration Detail: 6 months on production system
   Specific Tools: AWS Lambda, API Gateway, DynamoDB
   Metrics: Reduced API response time by 30%
   ```
   - Click "Refine Answer"
   - **Expected:** Quality score 7-9/10 (blue/green badge)
   - Answer should be much more professional

7. **Accept the Answer:**
   - Click "Accept Answer"
   - **Expected:** "Workflow Complete!" message with final answer

#### Expected Results:
- ✅ Deep dive prompts generated (3-5 seconds)
- ✅ Weak answer gets low quality score with suggestions
- ✅ Refinement improves quality score
- ✅ Final answer is professional and ready for resume
- ✅ Total time: 10-15 seconds for full flow

---

### Test 2: Deep Dive Path (Strong Answers - No Refinement) 🚀

**Objective:** Test that strong answers pass quality check immediately.

#### Steps:
1. Follow steps 1-4 from Test 1
2. Click "Yes, I have experience"
3. **Fill in STRONG responses:**
   ```
   Context: Professional work - E-commerce platform at TechCorp
   Duration: 18 months across 3 major projects (Oct 2022 - Mar 2024)
   Tools: AWS Lambda (Python 3.9), API Gateway, DynamoDB, Step Functions, CloudWatch
   Achievement: Architected serverless order processing system handling 50,000 orders daily.
                Built real-time inventory sync with Lambda + DynamoDB Streams.
   Metrics: Reduced infrastructure costs by 40% ($15K/month savings),
            improved API response time from 2000ms to 300ms (85% improvement),
            achieved 99.9% uptime
   ```

4. Click "Generate Professional Answer"

#### Expected Results:
- ✅ Quality score: 8-10/10 (green badge)
- ✅ Answer immediately marked as acceptable
- ✅ No refinement needed - direct to completion
- ✅ Professional answer includes all specifics and metrics
- ✅ Total time: 5-7 seconds

---

### Test 3: Learning Resources Path (No Experience) 📚

**Objective:** Test resource search, filtering, selection, and learning plan creation.

#### Steps:
1. Follow steps 1-4 from Test 1
2. Click "No, I don't have experience" (red button)

3. **Learning Resources Display appears:**
   - **Expected:** 5+ resources related to the gap
   - Each resource shows: type, provider, duration, difficulty, cost, rating

4. **Test Filters:**
   - Filter by Type: Select "Courses"
   - Filter by Difficulty: Select "Beginner"
   - Filter by Cost: Select "Free Only"
   - **Expected:** List updates in real-time

5. **Select Resources:**
   - Check 2-3 resources (checkboxes appear on cards)
   - **Expected:** Timeline preview appears below
   - **Expected:** "X resources selected" summary shows

6. **Review Timeline:**
   - Visual timeline with color-coded steps
   - Each step shows: start day, duration, end day
   - Progress bars indicate relative duration
   - **Expected:** Total duration calculated correctly

7. **Save Learning Plan:**
   - Click "Save Learning Plan"
   - **Expected:** Success message
   - **Expected:** "Workflow Complete!" with plan ID

#### Expected Results:
- ✅ Resources loaded (2-4 seconds)
- ✅ Filters work correctly
- ✅ Multi-select works
- ✅ Timeline updates dynamically
- ✅ Plan saved successfully
- ✅ Resume addition suggestion provided

---

### Test 4: Learning Path (Willing to Learn) 💡

**Objective:** Test the "willing to learn" option.

#### Steps:
1. Follow steps 1-4 from Test 1
2. Click "Willing to learn" (blue button)
3. Same as Test 3 (both "no" and "willing to learn" route to resources)

#### Expected Results:
- ✅ Same as Test 3
- ✅ Resume addition: "Currently expanding [skill] expertise through hands-on learning (X-day program)"

---

### Test 5: Multiple Questions Flow 🔄

**Objective:** Test handling multiple questions with different choices.

#### Steps:
1. Complete Phase 1-3 as usual
2. In Adaptive Mode:
   - Question 1: Choose "Yes" → Complete deep dive with strong answers
   - Question 2: Choose "No" → Select 2 learning resources
   - Question 3: Choose "Willing to Learn" → Select 3 learning resources
   - Question 4: Choose "Yes" → Complete deep dive with weak answers → Refine

#### Expected Results:
- ✅ Each question maintains independent state
- ✅ All workflows complete successfully
- ✅ Results are stored separately per question
- ✅ "Submit All Answers" appears when all complete

---

### Test 6: Mode Toggle During Session 🔀

**Objective:** Test switching between traditional and adaptive modes.

#### Steps:
1. Complete Phase 1-3
2. Start with Traditional Mode:
   - Answer 1-2 questions with text/voice
3. Toggle to Adaptive Mode:
   - **Expected:** See adaptive interface for remaining questions
4. Complete remaining questions in adaptive mode

#### Expected Results:
- ✅ Toggle works without errors
- ✅ Existing answers preserved
- ✅ Mode switch is seamless

---

## 🔍 Component-Level Testing

### ExperienceCheckModal
```typescript
// Test props
:gap-title="AWS Lambda"
:gap-description="Serverless computing..."

// Expected UI:
- Beautiful modal with gradient header
- 3 large, color-coded buttons (green/red/blue)
- Each button shows what happens next
- Close button works
```

### DeepDiveForm
```typescript
// Test dynamic rendering
- Text inputs render correctly
- Textareas have proper rows
- Selects show all options
- Multiselects allow multiple choices
- Number inputs validate

// Test validation
- Required fields show errors
- Form submission blocked if invalid
- Error messages clear on input
```

### AnswerQualityDisplay
```typescript
// Test quality scores
Score 9-10: Green badge, "Excellent Quality!"
Score 7-8:  Blue badge, "Good Quality"
Score 5-6:  Amber badge, "Needs Improvement"
Score 1-4:  Red badge, "Requires Refinement"

// Test features
- Copy to clipboard works
- Refinement button appears when score < 7
- Accept button always visible
```

### LearningResourcesDisplay
```typescript
// Test resource display
- All 115+ providers recognized
- Filters work independently
- Selection state persists
- Timeline updates on selection change

// Test resource card
- Type badge colors (course=purple, project=green, cert=blue)
- Difficulty colors (beginner=green, intermediate=yellow, advanced=red)
- Cost colors (free=green, paid=orange, freemium=blue)
```

### LearningTimeline
```typescript
// Test timeline visualization
- Vertical timeline with connected dots
- Color-coded by resource type
- Progress bars show relative duration
- Summary stats at bottom

// Test calculations
- Total days = max(end_day)
- Each step: start_day → end_day
- No gaps or overlaps
```

---

## 📊 Performance Benchmarks

Based on backend tests (`test_complete_pipeline.py`):

| Metric | Weak Flow | Strong Flow | Savings |
|--------|-----------|-------------|---------|
| Question Generation | ~2.5s | ~2.5s | - |
| Answer Generation | ~3.5s | ~3.5s | - |
| Quality Evaluation | ~1.0s | ~1.0s | - |
| Refinement | ~2.5s | N/A | - |
| **Total** | **~9.5s** | **~7.0s** | **26%** |

**Key Insights:**
- Strong answers complete 26% faster (no refinement loop)
- Quality evaluation is consistent (~1s)
- Resource search: 2-4s for 115+ platform database

---

## 🐛 Common Issues & Solutions

### Issue 1: Modal Doesn't Appear
**Solution:** Check console for errors. Verify all components imported correctly.

### Issue 2: Timeline Not Updating
**Solution:** Ensure `v-model` is bound to `selectedResourceIds` in LearningResourcesDisplay.

### Issue 3: Quality Score Always Low
**Solution:** Check backend logs. Ensure LangGraph workflow is executing. Verify LLM API keys are set.

### Issue 4: Resources Not Loading
**Solution:**
```bash
# Verify Qdrant is running
curl http://localhost:6333/health

# Re-seed if needed
docker-compose exec api python scripts/seed_resources.py
```

### Issue 5: Filters Not Working
**Solution:** Check browser console. Verify computed properties in LearningResourcesDisplay.vue.

---

## 🎨 UI/UX Verification

### Visual Checklist:
- [ ] Modal appears with smooth fade-in
- [ ] Buttons have hover effects
- [ ] Quality badges are color-coded correctly
- [ ] Timeline has smooth animations
- [ ] Progress bars fill correctly
- [ ] Cards have hover shadows
- [ ] Toggle switch animates smoothly
- [ ] Copy success toast appears/disappears
- [ ] All icons render correctly
- [ ] Responsive on mobile (320px+)

### Accessibility Checklist:
- [ ] All buttons have clear labels
- [ ] Form fields have proper labels
- [ ] Error messages are readable
- [ ] Color contrast meets WCAG AA
- [ ] Keyboard navigation works
- [ ] Screen reader compatible

---

## 📝 Testing Notes Template

Use this template when reporting test results:

```markdown
### Test Session: [Date]

**Tester:** [Name]
**Environment:**
- Browser: Chrome 121 / Firefox 122 / Safari 17
- OS: macOS / Windows / Linux
- Backend: Docker / Local

**Tests Completed:**
- [ ] Test 1: Deep Dive (Weak → Strong)
- [ ] Test 2: Deep Dive (Strong)
- [ ] Test 3: Learning Resources
- [ ] Test 4: Willing to Learn
- [ ] Test 5: Multiple Questions
- [ ] Test 6: Mode Toggle

**Issues Found:**
1. [Description] - Severity: High/Medium/Low
2. ...

**Performance:**
- Question Generation: X.Xs
- Answer Generation: X.Xs
- Resource Loading: X.Xs

**Notes:**
[Any additional observations]
```

---

## 🚀 Quick Start Test (1 minute)

For rapid verification that everything works:

1. **Start services:** `docker-compose up -d` (Backend)
2. **Start frontend:** `npm run dev` (Frontend)
3. **Upload sample data** (any CV + JD)
4. **Navigate to Smart Questions**
5. **Toggle Adaptive Mode ON**
6. **Pick first question:**
   - Click "Yes, I have experience"
   - Fill strong answers (use Test 2 example)
   - Verify quality score 8-10/10
   - Accept answer
7. **Done!** If this works, system is operational.

---

## 📚 Additional Resources

- **Backend API Docs:** `/Users/carlosid/PycharmProjects/test/Backend/ADAPTIVE_QUESTIONS_README.md`
- **Type Definitions:** `/Users/carlosid/PycharmProjects/test/frontend/types/adaptive-questions.ts`
- **Component Source:** `/Users/carlosid/PycharmProjects/test/frontend/components/`
- **Pipeline Test:** `/Users/carlosid/PycharmProjects/test/Backend/test_complete_pipeline.py`

---

## ✅ Success Criteria

The system is working correctly if:

1. ✅ All three paths (Yes/No/Willing) work without errors
2. ✅ Quality scores are reasonable (weak: 3-5, strong: 8-10)
3. ✅ Refinement improves scores
4. ✅ Resources load and filters work
5. ✅ Timeline updates correctly
6. ✅ Plans save successfully
7. ✅ Mode toggle is seamless
8. ✅ Performance is within benchmarks
9. ✅ UI is smooth and responsive
10. ✅ No console errors

---

**Last Updated:** 2025-01-24
**Version:** 1.0
**Status:** ✅ Ready for Testing
