# Frontend Questions System Refactoring Progress

## ✅ COMPLETED (Phases 1-2 Partial)

### Phase 1: Type Duplication Fixed ✅
**File:** `frontend/composables/useAdaptiveQuestions.ts`

**Changes Made:**
- Removed all duplicate type definitions (DeepDivePromptItem, LearningResourceItem, etc.)
- Imported types from central `~/types/adaptive-questions.ts`
- Updated all function signatures to use imported types
- Reduced code duplication by ~100 lines

**Benefits:**
- ✅ Single source of truth for types
- ✅ Easier maintenance
- ✅ No risk of type drift between files

---

### Phase 2: Pinia Store Created ✅
**File:** `frontend/stores/useQuestionsStore.ts` (NEW - 341 lines)

**Store Architecture:**
```typescript
State:
- answers: Map<string, QuestionAnswer>
- answerEvaluations: Map<string, AnswerEvaluation>
- activeAdaptiveFlows: Map<string, ExperienceLevel>
- refinementData: Map<string, Record<string, string>>
- activeQuestionTab: Map<string, 'original' | 'followup'>
- refinementIterations: Map<string, number>
- isSubmitting, hasSubmitted, answersResult
- evaluatingQuestionId
- showAdaptiveModal, currentAdaptiveQuestion

Getters (15 methods):
- getAnswerById, getEvaluationById
- isQuestionAnswered, allQuestionsAnswered
- getRefinementData, hasRefinementData
- getActiveTab, getRefinementIteration
- isInAdaptiveFlow, getAdaptiveExperienceLevel
- answersArray (converts Map to Array)

Actions (19 methods):
- setAnswer, setEvaluation, startEvaluation, clearEvaluation
- setRefinementData, updateRefinementField, incrementRefinementIteration
- acceptAnswer, setActiveTab
- startAdaptiveFlow, completeAdaptiveFlow
- openAdaptiveModal, closeAdaptiveModal
- setSubmitting, setAnswersResult
- clearAnswers, resetStore, clearQuestionState
```

**Benefits:**
- ✅ Centralized state management
- ✅ Type-safe getters and actions
- ✅ DevTools integration
- ✅ Easier testing
- ✅ State persistence ready (commented out - can enable with @pinia/plugin-persistedstate)

---

### Phase 2: QuestionsResult.vue Partial Refactoring 🔄
**File:** `frontend/components/QuestionsResult.vue`

**Changes Made:**
- ✅ Imported Pinia store
- ✅ Replaced local refs with computed properties from store
- ✅ Updated `handleAnswerSubmit` to use store actions
- ✅ Updated tab management helpers to use store
- ✅ Updated `getAnswerStatus` to use store getter

**Still TODO:**
- ⏳ Update remaining functions:
  - `handleNeedHelp` → use `questionsStore.openAdaptiveModal`
  - `closeAdaptiveModal` → use `questionsStore.closeAdaptiveModal`
  - `handleExperienceSelection` → use `questionsStore.startAdaptiveFlow`
  - `cancelAdaptiveFlow` → use `questionsStore.completeAdaptiveFlow`
  - `handleAdaptiveComplete` → use `questionsStore.setAnswer`
  - `handleAcceptAnswer` → use `questionsStore.acceptAnswer` + `setAnswer`
  - `submitRefinement` → use store getters/actions
  - `submitAllAnswers` → use `questionsStore.setSubmitting`, `setAnswersResult`

---

## 🚧 IN PROGRESS / TODO

### Complete Phase 2: Finish QuestionsResult.vue Refactoring

**Remaining Changes:**

1. **Modal Management:**
```typescript
// BEFORE:
const handleNeedHelp = (question: QuestionItem) => {
  currentAdaptiveQuestion.value = question
  showAdaptiveModal.value = true
}

// AFTER:
const handleNeedHelp = (question: QuestionItem) => {
  questionsStore.openAdaptiveModal(question)
}
```

2. **Adaptive Flow Management:**
```typescript
// BEFORE:
const handleExperienceSelection = (level: ExperienceLevel) => {
  if (!currentAdaptiveQuestion.value) return
  activeAdaptiveFlows.value.set(currentAdaptiveQuestion.value.id, level)
  closeAdaptiveModal()
}

// AFTER:
const handleExperienceSelection = (level: ExperienceLevel) => {
  if (!questionsStore.currentAdaptiveQuestion) return
  questionsStore.startAdaptiveFlow(questionsStore.currentAdaptiveQuestion.id, level)
  questionsStore.closeAdaptiveModal()
}
```

3. **Answer Management:**
```typescript
// BEFORE:
const handleAcceptAnswer = (questionId: string) => {
  const evaluation = answerEvaluations.value.get(questionId)
  if (!evaluation) return

  const answer: QuestionAnswer = {
    question_id: questionId,
    answer_text: evaluation.answer_text,
    answer_type: 'text'
  }
  answers.value.set(questionId, answer)
}

// AFTER:
const handleAcceptAnswer = (questionId: string) => {
  const evaluation = questionsStore.getEvaluationById(questionId)
  if (!evaluation) return

  questionsStore.setAnswer(questionId, evaluation.answer_text, 'text')
  questionsStore.acceptAnswer(questionId) // Clears refinement data
}
```

4. **Refinement Logic:**
```typescript
// BEFORE:
const submitRefinement = async (questionId: string) => {
  const refinement = refinementData.value.get(questionId)
  // ... logic ...
  evaluatingQuestionId.value = questionId
  // ... API call ...
  refinementData.value.delete(questionId)
}

// AFTER:
const submitRefinement = async (questionId: string) => {
  const refinement = questionsStore.getRefinementData(questionId)
  if (!questionsStore.hasRefinementData(questionId)) {
    alert('Please provide at least one additional detail.')
    return
  }

  questionsStore.startEvaluation(questionId)
  // ... API call ...
  questionsStore.incrementRefinementIteration(questionId)
  questionsStore.clearEvaluation()
}
```

5. **Submission Logic:**
```typescript
// BEFORE:
const submitAllAnswers = async () => {
  try {
    isSubmitting.value = true
    const answersArray = Array.from(answers.value.values())
    // ... API call ...
    answersResult.value = result
    hasSubmitted.value = true
  } finally {
    isSubmitting.value = false
  }
}

// AFTER:
const submitAllAnswers = async () => {
  try {
    questionsStore.setSubmitting(true)
    const answersArray = questionsStore.answersArray
    // ... API call ...
    questionsStore.setAnswersResult(result)
    emit('answers-submitted', result, answersArray, result.updated_cv)
  } catch (error: any) {
    alert(error.message || 'Failed to submit answers')
  } finally {
    questionsStore.setSubmitting(false)
  }
}
```

**Estimated Time:** 1-2 hours

---

### Phase 3: Add useAdaptiveFlow Toggle

**Files to Modify:**
1. `frontend/composables/useAnalysisState.ts` - Add toggle state
2. `frontend/pages/analyze.vue` - Add UI toggle
3. `frontend/components/QuestionsResult.vue` - Respect toggle
4. `frontend/composables/useQuestionGenerator.ts` - Add deprecation warning
5. `frontend/composables/useAnswerSubmitter.ts` - Add deprecation warning

**Implementation:**

```typescript
// useAnalysisState.ts
const useAdaptiveFlow = ref(true) // Default to new system

export const useAnalysisState = () => {
  return {
    // ... existing state ...
    useAdaptiveFlow,
    toggleWorkflow: () => {
      useAdaptiveFlow.value = !useAdaptiveFlow.value
    }
  }
}

// QuestionsResult.vue
const { useAdaptiveFlow } = useAnalysisState()

// Show different UI based on toggle
<div v-if="useAdaptiveFlow">
  <!-- Adaptive workflow UI -->
</div>
<div v-else>
  <!-- Legacy workflow UI -->
  <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
    <p class="text-sm text-yellow-700">
      ⚠️ You are using the legacy question workflow.
      <button @click="useAdaptiveFlow = true" class="underline">Switch to new adaptive workflow</button>
    </p>
  </div>
</div>

// useQuestionGenerator.ts
export const useQuestionGenerator = () => {
  const generateQuestions = async (...) => {
    console.warn('[DEPRECATED] useQuestionGenerator is being phased out. Use adaptive questions workflow instead.')
    // ... existing code ...
  }
}
```

**Estimated Time:** 2-3 hours

---

### Phase 4: UI Improvements

#### 4.1 Loading States
**Files:** `QuestionsResult.vue`, `AdaptiveQuestionFlow.vue`, `AnswerQualityDisplay.vue`

```vue
<!-- Add skeleton loaders -->
<div v-if="evaluatingQuestionId === question.id" class="animate-pulse">
  <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
  <div class="h-4 bg-gray-200 rounded w-1/2"></div>
</div>

<!-- Add progress indicators -->
<div class="flex items-center gap-2 text-sm text-gray-600">
  <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
    <!-- spinner icon -->
  </svg>
  Evaluating your answer...
</div>

<!-- Add timeout warnings -->
<div v-if="isEvaluatingTooLong" class="text-amber-600 text-sm">
  Taking longer than usual...
</div>
```

#### 4.2 Dynamic Refinement UI
**File:** `AdaptiveQuestionFlow.vue`

**CURRENT (Hardcoded):**
```vue
<div class="space-y-4">
  <div>
    <label>How long did you work on this?</label>
    <input v-model="refinementInput.duration_detail" />
  </div>
  <div>
    <label>What specific tools did you use?</label>
    <input v-model="refinementInput.specific_tools" />
  </div>
  <div>
    <label>What metrics/results did you achieve?</label>
    <input v-model="refinementInput.metrics" />
  </div>
</div>
```

**NEW (Dynamic):**
```vue
<div class="space-y-4">
  <div v-for="(suggestion, index) in qualityEvaluation.improvement_suggestions" :key="index">
    <label :class="getPriorityClass(suggestion.priority)">
      {{ suggestion.issue }}
    </label>
    <p class="text-sm text-gray-600 mb-2">{{ suggestion.suggestion }}</p>
    <component
      :is="getInputComponent(suggestion.type || 'text')"
      v-model="refinementInput[`suggestion_${index}`]"
      :placeholder="suggestion.help_text"
    />
  </div>
</div>

<script>
const getInputComponent = (type: string) => {
  switch (type) {
    case 'textarea': return 'textarea'
    case 'select': return 'select'
    case 'number': return 'input[type="number"]'
    default: return 'input[type="text"]'
  }
}

const getPriorityClass = (priority: string) => {
  return {
    'critical': 'text-red-700 font-bold',
    'high': 'text-orange-700 font-semibold',
    'medium': 'text-yellow-700'
  }[priority] || 'text-gray-700'
}
</script>
```

**Estimated Time:** 3-4 hours

---

### Phase 5: Comprehensive Testing

#### 5.1 Component Tests (5 files)

**Test Files to Create:**

1. **`tests/unit/components/QuestionsResult.spec.ts`** (~200 lines)
```typescript
describe('QuestionsResult.vue', () => {
  it('displays question statistics correctly', () => {})
  it('handles answer submission', async () => {})
  it('evaluates answer quality', async () => {})
  it('shows refinement prompts when score < 7', () => {})
  it('accepts answer and stores in Pinia', async () => {})
  it('submits all answers when complete', async () => {})
})
```

2. **`tests/unit/components/AdaptiveQuestionFlow.spec.ts`** (~200 lines)
```typescript
describe('AdaptiveQuestionFlow.vue', () => {
  it('shows experience check modal initially', () => {})
  it('routes to deep dive on "yes" selection', async () => {})
  it('routes to learning resources on "willing_to_learn"', async () => {})
  it('handles deep dive form submission', async () => {})
  it('shows quality evaluation after submission', () => {})
  it('allows up to 2 refinement iterations', async () => {})
  it('saves learning plan to PostgreSQL', async () => {})
})
```

3. **`tests/unit/components/AnswerQualityDisplay.spec.ts`** (~100 lines)
```typescript
describe('AnswerQualityDisplay.vue', () => {
  it('renders score badge with correct color', () => {})
  it('displays quality issues', () => {})
  it('displays quality strengths', () => {})
  it('shows improvement suggestions', () => {})
  it('emits refine-answer event', () => {})
  it('emits accept-answer event', () => {})
})
```

4. **`tests/unit/components/QuestionCard.spec.ts`** (~80 lines)
```typescript
describe('QuestionCard.vue', () => {
  it('renders question with priority badge', () => {})
  it('shows examples when expanded', () => {})
  it('emits need-help event on "Zero Experience" click', () => {})
})
```

5. **`tests/unit/components/AnswerInput.spec.ts`** (~150 lines)
```typescript
describe('AnswerInput.vue', () => {
  it('switches between text and voice tabs', () => {})
  it('submits text answer', async () => {})
  it('records and transcribes voice', async () => {})
  it('allows editing transcription', () => {})
  it('shows recording timer', () => {})
})
```

#### 5.2 Integration Tests (2 files)

1. **`tests/integration/question-workflow.spec.ts`** (~150 lines)
```typescript
describe('Question Workflow Integration', () => {
  it('completes full legacy workflow', async () => {
    // Generate → Answer → Submit → Score Update
  })

  it('completes full adaptive workflow', async () => {
    // Experience check → Deep dive → Quality eval → Refine → Accept
  })

  it('handles mixed answers (legacy + adaptive)', async () => {
    // Verify batch submission works with both types
  })
})
```

2. **`tests/integration/voice-recording.spec.ts`** (~100 lines)
```typescript
describe('Voice Recording Integration', () => {
  it('records and transcribes audio', async () => {})
  it('handles microphone permission denial', async () => {})
  it('handles transcription API failure', async () => {})
  it('falls back to OpenAI Whisper when Parakeet unavailable', async () => {})
})
```

**Estimated Time:** 6-8 hours

---

### Phase 6: Documentation

**Files to Update:**
1. `CLAUDE.md` - Add Pinia architecture section
2. `frontend/TESTING_README.md` - Document new tests
3. `frontend/stores/useQuestionsStore.ts` - Add JSDoc to complex actions
4. `frontend/components/QuestionsResult.vue` - Add JSDoc to key functions
5. `frontend/components/AdaptiveQuestionFlow.vue` - Add state transition diagram

**Example JSDoc:**
```typescript
/**
 * Evaluates the quality of a user's answer and stores the evaluation.
 *
 * @param questionId - Unique identifier for the question
 * @param text - User's answer text (plain text or transcribed voice)
 * @param type - Answer type ('text' | 'voice')
 * @param transcriptionTime - Time taken for transcription (optional)
 *
 * @throws {Error} If evaluation API call fails
 *
 * @example
 * await handleAnswerSubmit('q1', 'I built a chatbot...', 'text')
 *
 * @sideEffects
 * - Sets evaluating state
 * - Stores evaluation in Pinia
 * - Initializes refinement data if score < 7
 * - Sets active tab to 'original'
 */
const handleAnswerSubmit = async (...) => { ... }
```

**Estimated Time:** 2-3 hours

---

### Phase 7: Minor Fixes

1. **Tab Persistence** ✅ (Already handled by Pinia store - can enable persistence)
2. **Voice in Refinement** - Add voice recording option to refinement dialog
3. **Answer Storage Consistency** - Verify mixed format submission works

**Estimated Time:** 2-3 hours

---

## 📊 SUMMARY

### Completed:
- ✅ Phase 1: Type duplication fixed (100%)
- ✅ Phase 2: Pinia store created (100%)
- 🔄 Phase 2: QuestionsResult.vue refactored (40%)

### Remaining:
- ⏳ Complete QuestionsResult.vue refactoring (60% - ~1-2 hours)
- ⏳ Phase 3: Toggle & deprecation warnings (~2-3 hours)
- ⏳ Phase 4: UI improvements (~3-4 hours)
- ⏳ Phase 5: Comprehensive tests (~6-8 hours)
- ⏳ Phase 6: Documentation (~2-3 hours)
- ⏳ Phase 7: Minor fixes (~2-3 hours)

### Total Remaining: ~17-23 hours

---

## 🚀 NEXT STEPS

### Immediate (Priority 1 - Complete Today):
1. Finish QuestionsResult.vue Pinia refactoring
2. Test basic functionality works
3. Run existing tests to ensure no regressions

### Short-term (Priority 2 - This Week):
4. Add useAdaptiveFlow toggle
5. Implement dynamic refinement UI
6. Add loading states

### Medium-term (Priority 3 - Next Week):
7. Write comprehensive component tests
8. Write integration tests
9. Update documentation

---

## 🎯 TESTING STRATEGY

After completing refactoring:
1. **Manual Testing:**
   - Test legacy workflow end-to-end
   - Test adaptive workflow end-to-end
   - Test mixed workflow (some legacy, some adaptive)
   - Test voice recording
   - Test refinement cycles

2. **Automated Testing:**
   - Run existing tests: `npm run test:run`
   - Add new component tests
   - Add integration tests
   - Aim for 90%+ coverage

3. **Visual Testing:**
   - Use `npm run test:ui` for debugging
   - Verify all UI states render correctly
   - Check loading states
   - Verify error states

---

## 📝 NOTES

- All Map-based state can now be replaced with Pinia store calls
- Store provides type-safe getters and actions
- DevTools integration available for debugging
- State persistence can be enabled by installing `@pinia/plugin-persistedstate`
- Legacy workflow will be maintained alongside adaptive for backward compatibility
- Clear deprecation warnings will guide users to new system

---

## 🐛 KNOWN ISSUES

1. **Template still uses .value accessors** - Need to update template to use store directly
2. **Some computed properties redundant** - Can access store state directly in template
3. **Mixed answer format handling** - Needs verification that batch submission works

---

## ✅ SUCCESS CRITERIA

- [ ] No type duplication
- [ ] All state managed by Pinia store
- [ ] Clear legacy/adaptive separation with toggle
- [ ] Dynamic refinement UI
- [ ] Loading states throughout
- [ ] 90%+ component test coverage
- [ ] All existing tests pass
- [ ] Documentation updated
- [ ] No breaking changes to existing functionality
