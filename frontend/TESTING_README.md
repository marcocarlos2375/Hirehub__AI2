# Vitest Testing Setup for Frontend

## Overview
This project now has Vitest configured for testing the adaptive questions refinement flow.

## What's Installed

- **vitest** - Modern testing framework for Vite/Nuxt projects
- **@vue/test-utils** - Official Vue.js testing utilities
- **@vitest/ui** - Visual test UI interface
- **happy-dom** - Fast DOM implementation for testing

## Project Structure

```
frontend/
├── tests/
│   ├── setup.ts                                    # Test configuration
│   ├── unit/
│   │   └── composables/
│   │       └── useAdaptiveQuestions.spec.ts       # Composable unit tests
│   └── integration/
│       └── refinement-flow.spec.ts                # Full refinement flow tests
├── vitest.config.ts                               # Vitest configuration
└── package.json                                   # Updated with test scripts
```

## Running Tests

### Run All Tests Once
```bash
cd frontend
npm run test:run
```

### Run Tests in Watch Mode
```bash
npm run test
```

### Run Tests with UI
```bash
npm run test:ui
```
Opens a browser with visual test interface at http://localhost:51204

### Generate Coverage Report
```bash
npm run test:coverage
```
Creates coverage report in `coverage/` directory

## What's Being Tested

### Unit Tests (`tests/unit/composables/useAdaptiveQuestions.spec.ts`)

Tests individual composable functions:

1. **evaluateAnswer()**
   - ✅ Calls API with correct parameters
   - ✅ Returns proper evaluation structure
   - ✅ Handles API errors gracefully

2. **refineAnswer()**
   - ✅ Passes all required context fields
   - ✅ Sends question_text, question_data, gap_info
   - ✅ Includes generated_answer and quality_issues
   - ✅ Handles refinement failures

3. **startAdaptiveQuestion()**
   - ✅ Initiates adaptive workflow correctly
   - ✅ Passes experience level (yes/no/willing_to_learn)

### Integration Tests (`tests/integration/refinement-flow.spec.ts`)

Tests complete refinement workflow:

1. **Full Refinement Cycle**
   ```typescript
   Poor Answer (score 4)
      ↓
   Submit Refinement Data
      ↓
   Improved Answer (score 8+)
   ```

   - ✅ Poor answer gets score < 7
   - ✅ Shows improvement suggestions
   - ✅ Refinement increases score
   - ✅ Refined answer contains added details

2. **Max Iteration Limit**
   - ✅ Allows up to 2 refinement iterations
   - ✅ Accepts answer after max iterations
   - ✅ Tracks iteration count correctly

3. **Context Preservation**
   - ✅ Question context preserved across iterations
   - ✅ Gap info maintained through refinement
   - ✅ Previous answer and issues passed correctly

4. **Error Handling**
   - ✅ Handles 422 validation errors
   - ✅ Handles network failures
   - ✅ Provides meaningful error messages

## Test Scenarios

### Scenario 1: Successful Refinement
```
1. User submits: "I built a chatbot"
2. System evaluates: Score 4/10 (too vague)
3. System suggests: Add metrics, technical details, timeline
4. User refines with: "50 users, 87% satisfaction, Python + OpenAI API"
5. System re-evaluates: Score 8/10 (acceptable)
6. Answer accepted ✅
```

### Scenario 2: Max Iterations
```
1. First answer: Score 4/10
2. First refinement: Score 5/10 (still not acceptable)
3. Second refinement: Score 6/10 (accepted due to max iterations) ✅
```

### Scenario 3: Error Handling
```
1. API returns 422 error (missing question_text)
2. Test verifies error is thrown
3. User sees meaningful error message ✅
```

## Mocking Strategy

Tests use `vi.mocked($fetch)` to mock API calls:

```typescript
vi.mocked($fetch).mockResolvedValueOnce({
  quality_score: 8,
  refined_answer: "Improved answer..."
})
```

This allows testing without needing the backend running.

## Key Assertions

### Quality Evaluation
```typescript
expect(evaluation.quality_score).toBeLessThan(7)
expect(evaluation.is_acceptable).toBe(false)
expect(evaluation.improvement_suggestions.length).toBeGreaterThan(0)
```

### Refinement Success
```typescript
expect(refined.quality_score).toBeGreaterThanOrEqual(7)
expect(refined.refined_answer).toContain('50 users')
expect(refined.iteration).toBe(1)
```

### Context Preservation
```typescript
expect($fetch).toHaveBeenCalledWith(
  '/api/adaptive-questions/refine-answer',
  expect.objectContaining({
    body: expect.objectContaining({
      question_text: 'Expected question',
      question_data: { /* expected data */ },
      gap_info: { /* expected gap */ }
    })
  })
)
```

## Troubleshooting

### Tests Not Running
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Import Errors
Check that `vitest.config.ts` has correct path aliases:
```typescript
resolve: {
  alias: {
    '~': fileURLToPath(new URL('./', import.meta.url))
  }
}
```

### Mock Not Working
Ensure `tests/setup.ts` is loaded:
```typescript
// vitest.config.ts
test: {
  setupFiles: ['./tests/setup.ts']
}
```

## Next Steps

### Add More Tests
- Component tests for `QuestionsResult.vue`
- Component tests for `AnswerQualityDisplay.vue`
- E2E tests with Playwright (optional)

### Add Coverage Threshold
```typescript
// vitest.config.ts
test: {
  coverage: {
    statements: 80,
    branches: 80,
    functions: 80,
    lines: 80
  }
}
```

### CI/CD Integration
```yaml
# .github/workflows/test.yml
- name: Run tests
  run: npm run test:run
```

## Benefits

✅ **Fast Feedback** - Tests run in milliseconds
✅ **Confidence** - Verify refinement flow works correctly
✅ **Regression Prevention** - Catch bugs before production
✅ **Documentation** - Tests serve as usage examples
✅ **Refactoring Safety** - Make changes confidently

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
