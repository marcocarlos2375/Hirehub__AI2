# Quick Refactoring Checklist

## ✅ COMPLETED

- [x] Remove type duplication in `useAdaptiveQuestions.ts`
- [x] Create Pinia store `useQuestionsStore.ts`
- [x] Install Pinia: `npm install @pinia/nuxt pinia`
- [x] Add Pinia to `nuxt.config.ts`
- [x] Update QuestionsResult imports
- [x] Replace local refs with store computed properties
- [x] Update `handleAnswerSubmit` to use store
- [x] Update tab management helpers

## 🚧 IN PROGRESS

### Complete QuestionsResult.vue Refactoring

**Search & Replace Patterns:**

1. **Modal Management:**
```typescript
// Find: currentAdaptiveQuestion.value = question\nshowAdaptiveModal.value = true
// Replace: questionsStore.openAdaptiveModal(question)

// Find: showAdaptiveModal.value = false\ncurrentAdaptiveQuestion.value = null
// Replace: questionsStore.closeAdaptiveModal()
```

2. **Adaptive Flow:**
```typescript
// Find: activeAdaptiveFlows.value.set(
// Replace: questionsStore.startAdaptiveFlow(

// Find: activeAdaptiveFlows.value.delete(
// Replace: questionsStore.completeAdaptiveFlow(
```

3. **Answer Storage:**
```typescript
// Find: answers.value.set(questionId, answer)
// Replace: questionsStore.setAnswer(questionId, answer.answer_text, answer.answer_type, answer.transcription_time)
```

4. **Evaluation:**
```typescript
// Find: answerEvaluations.value.set(
// Replace: questionsStore.setEvaluation(

// Find: answerEvaluations.value.get(
// Replace: questionsStore.getEvaluationById(
```

5. **Refinement:**
```typescript
// Find: refinementData.value.get(
// Replace: questionsStore.getRefinementData(

// Find: refinementData.value.set(
// Replace: questionsStore.setRefinementData(

// Find: refinementData.value.delete(
// Replace: (use questionsStore.acceptAnswer() which deletes internally)
```

6. **Submission:**
```typescript
// Find: isSubmitting.value = true
// Replace: questionsStore.setSubmitting(true)

// Find: hasSubmitted.value = true
// Replace: (handled by questionsStore.setAnswersResult())

// Find: answersResult.value = result
// Replace: questionsStore.setAnswersResult(result)

// Find: Array.from(answers.value.values())
// Replace: questionsStore.answersArray
```

---

## 📋 TODO QUICK LIST

### Phase 3: Toggle & Warnings (2-3 hours)
- [ ] Add `useAdaptiveFlow` ref to `useAnalysisState.ts`
- [ ] Add toggle UI in `analyze.vue` (Settings button in header)
- [ ] Update `QuestionsResult.vue` template with v-if/v-else
- [ ] Add deprecation console.warn() in legacy composables
- [ ] Add yellow banner in legacy mode

### Phase 4: UI Improvements (3-4 hours)
- [ ] Add skeleton loaders during evaluation
- [ ] Add spinner with "Evaluating..." text
- [ ] Add timeout warning (if >10s)
- [ ] Make refinement UI dynamic from suggestions
- [ ] Support textarea/select/number input types
- [ ] Add priority color coding (red/orange/yellow)

### Phase 5: Tests (6-8 hours)
- [ ] Create `tests/unit/components/` directory
- [ ] Write QuestionsResult.spec.ts (200 lines)
- [ ] Write AdaptiveQuestionFlow.spec.ts (200 lines)
- [ ] Write AnswerQualityDisplay.spec.ts (100 lines)
- [ ] Write QuestionCard.spec.ts (80 lines)
- [ ] Write AnswerInput.spec.ts (150 lines)
- [ ] Create `tests/integration/` directory
- [ ] Write question-workflow.spec.ts (150 lines)
- [ ] Write voice-recording.spec.ts (100 lines)
- [ ] Run: `npm run test:run`
- [ ] Aim for 90%+ coverage

### Phase 6: Documentation (2-3 hours)
- [ ] Add JSDoc to all store actions
- [ ] Add JSDoc to key component functions
- [ ] Update CLAUDE.md with Pinia section
- [ ] Update TESTING_README.md with new tests
- [ ] Add state transition diagram

### Phase 7: Minor Fixes (2-3 hours)
- [ ] Enable Pinia persistence (install plugin)
- [ ] Add voice option to refinement dialog
- [ ] Test mixed answer format submission
- [ ] Fix any remaining .value accessors in template

### Final: Testing & Verification
- [ ] Run all tests: `npm run test:run`
- [ ] Manual test: Legacy workflow
- [ ] Manual test: Adaptive workflow
- [ ] Manual test: Mixed workflow
- [ ] Manual test: Voice recording
- [ ] Manual test: Refinement cycles
- [ ] Check no console errors
- [ ] Verify DevTools shows Pinia state
- [ ] Test on different browsers

---

## 🔍 DEBUGGING TIPS

### If tests fail:
1. Check Pinia store is imported correctly
2. Verify computed properties don't use `.value` in template
3. Check all Map operations replaced with store calls
4. Ensure store actions are called (not direct state mutation)

### If UI breaks:
1. Open Vue DevTools → Pinia tab
2. Check state is updating correctly
3. Verify getters return expected values
4. Check computed properties are reactive
5. Look for remaining `.value` accessors in template

### If store doesn't work:
1. Verify `@pinia/nuxt` in `nuxt.config.ts` modules
2. Check store is exported with `defineStore`
3. Verify store is imported in component
4. Check state is accessed via store instance

---

## 📖 REFERENCE

### Store API Quick Reference:

**Getters:**
- `questionsStore.getAnswerById(id)`
- `questionsStore.getEvaluationById(id)`
- `questionsStore.isQuestionAnswered(id)`
- `questionsStore.allQuestionsAnswered(total)`
- `questionsStore.answersArray`
- `questionsStore.getRefinementData(id)`
- `questionsStore.hasRefinementData(id)`
- `questionsStore.getActiveTab(id)`
- `questionsStore.getRefinementIteration(id)`

**Actions:**
- `questionsStore.setAnswer(id, text, type, time?)`
- `questionsStore.setEvaluation(id, evaluation)`
- `questionsStore.startEvaluation(id)`
- `questionsStore.clearEvaluation()`
- `questionsStore.setRefinementData(id, data)`
- `questionsStore.updateRefinementField(id, field, value)`
- `questionsStore.incrementRefinementIteration(id)`
- `questionsStore.acceptAnswer(id)`
- `questionsStore.setActiveTab(id, tab)`
- `questionsStore.startAdaptiveFlow(id, level)`
- `questionsStore.completeAdaptiveFlow(id)`
- `questionsStore.openAdaptiveModal(question)`
- `questionsStore.closeAdaptiveModal()`
- `questionsStore.setSubmitting(bool)`
- `questionsStore.setAnswersResult(result)`
- `questionsStore.clearAnswers()`
- `questionsStore.resetStore()`

---

## ⚡ EFFICIENCY TIPS

1. **Use Find & Replace (Cmd+Shift+F)** in VS Code for bulk changes
2. **Test incrementally** - don't change everything at once
3. **Use Git commits** after each phase for easy rollback
4. **Run tests frequently** to catch regressions early
5. **Use Copilot/ChatGPT** to generate test boilerplate
6. **Check DevTools Pinia tab** to verify state updates

---

## 🎯 SUCCESS METRICS

- **Code Quality:** No duplicate types, centralized state
- **Test Coverage:** 90%+ for components
- **Performance:** No performance degradation
- **Maintainability:** Clear separation of concerns
- **User Experience:** Smooth transitions, loading states
- **Documentation:** Clear, up-to-date docs

---

## 📞 NEED HELP?

- Check `REFACTORING_PROGRESS.md` for detailed implementation examples
- Check `CLAUDE.md` for architecture overview
- Check `TESTING_README.md` for testing guide
- Ask Claude to continue the refactoring from this checklist
