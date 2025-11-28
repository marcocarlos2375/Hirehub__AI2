<template>
  <div class="question-slider pt-1">
    <!-- Dots at top (show when multiple slides) -->
    <div v-if="showDots" class="dots">
      <button
        v-for="i in totalSlides"
        :key="i"
        :class="{ active: currentSlide === i - 1 }"
        @click="goToSlide(i - 1)"
      />
    </div>

    <!-- Slider Container -->
    <div class="slider-container">
      <div class="slider-track" :style="{ transform: `translateX(-${currentSlide * 100}%)` }">
        <!-- Slide 0: Original Question -->
        <div class="slide">
          <div class="slide-content">
            <OriginalQuestionSlide
              :question="question"
              :question-index="questionIndex"
              :is-active="currentSlide === 0"
              :parsed-cv="parsedCv"
              :parsed-jd="parsedJd"
              :language="language"
              @need-help="handleNeedHelp"
              @navigate="$emit('navigate', $event)"
              @submit-all="$emit('submit-all')"
            />
          </div>
        </div>

        <!-- Slide 1: No Experience (only shown in NO_EXPERIENCE state) -->
        <div v-if="showNoExperienceSlide" class="slide">
          <div class="slide-content">
            <NoExperienceSlide
              :question="question"
              :is-active="currentSlide === 1"
              @learning-choice="handleLearningChoice"
            />
          </div>
        </div>

        <!-- Slide 2 (or 1): Refinement OR Feedback Submitted (only shown after evaluation) -->
        <div v-if="hasEvaluation || showFeedbackSubmittedSlide" class="slide">
          <div class="slide-content">
            <!-- Show FeedbackSubmittedSlide when in feedback_submitted state -->
            <FeedbackSubmittedSlide
              v-if="showFeedbackSubmittedSlide"
              :formatted-answer="questionsStore.getImprovedResponse(question.id)"
              :loading="evaluatingQuestion"
              :is-active="currentSlide === 1"
              @continue="handleFeedbackContinue"
            />
            <!-- Show RefinementSlide when in feedback state -->
            <RefinementSlide
              v-else
              :question="question"
              :evaluation="evaluation"
              :is-active="currentSlide === 1"
              @submit-refinement="handleRefinementSubmit"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { QuestionSliderProps, QuestionSliderEmits } from '~/types/component-props'
import { QUESTION_STEP_STATES } from '~/types/constants'
import { useQuestionsStore } from '~/stores/questions/useQuestionsStore'

import OriginalQuestionSlide from '../adaptive-questions/OriginalQuestionSlide.vue'
import RefinementSlide from '../adaptive-questions/RefinementSlide.vue'
import NoExperienceSlide from '../adaptive-questions/NoExperienceSlide.vue'
import FeedbackSubmittedSlide from '../adaptive-questions/FeedbackSubmittedSlide.vue'

const props = withDefaults(defineProps<QuestionSliderProps>(), {
  language: 'english'
})

const emit = defineEmits<QuestionSliderEmits>()

const questionsStore = useQuestionsStore()

// Current slide index for this question
const currentSlide = ref(questionsStore.getCurrentSlide(props.question.id))

// Get evaluation from store
const evaluation = computed(() => {
  return questionsStore.getEvaluationById(props.question.id)
})

// Detect if answer has been evaluated (for conditional slides/dots)
const hasEvaluation = computed(() => {
  return questionsStore.getEvaluationById(props.question.id) !== undefined
})

// Show no experience slide when user selected 'no experience'
const showNoExperienceSlide = computed(() => {
  const state = questionsStore.getQuestionState(props.question.id)
  return state === QUESTION_STEP_STATES.NO_EXPERIENCE
})

// Show feedback submitted slide when in feedback_submitted state
const showFeedbackSubmittedSlide = computed(() => {
  const state = questionsStore.getQuestionState(props.question.id)
  return state === QUESTION_STEP_STATES.FEEDBACK_SUBMITTED
})

// Check if question is being evaluated
const evaluatingQuestion = computed(() => {
  return questionsStore.evaluatingQuestionId === props.question.id
})

// Total slides to show
const totalSlides = computed(() => {
  // If in NO_EXPERIENCE state, show 2 slides (original + no experience)
  if (showNoExperienceSlide.value) return 2

  // Normal flow: 1 or 2 slides (original + optional refinement)
  return hasEvaluation.value ? 2 : 1
})

// Show dots when we have multiple slides
const showDots = computed(() => {
  return totalSlides.value > 1
})

// Watch for evaluation changes to trigger slide transition
watch(() => evaluation.value, (newEvaluation, oldEvaluation) => {
  // If evaluation was just set and it's not acceptable, slide to refinement
  if (newEvaluation && !oldEvaluation && !newEvaluation.is_acceptable) {
    // Switch to feedback state
    questionsStore.setQuestionState(props.question.id, QUESTION_STEP_STATES.FEEDBACK)

    // Slide to Slide 2 (refinement)
    currentSlide.value = 1
    questionsStore.setCurrentSlide(props.question.id, 1)
    handleSlideChange(1)
  }
}, { immediate: false })

// Watch store's current slide (for external changes)
watch(() => questionsStore.getCurrentSlide(props.question.id), (newSlide) => {
  if (newSlide !== currentSlide.value) {
    currentSlide.value = newSlide
  }
})

// Simple slide navigation
const goToSlide = (index: number) => {
  // Prevent sliding to slide 1 ONLY if no evaluation AND not in NO_EXPERIENCE state
  if (index === 1 && !hasEvaluation.value && !showNoExperienceSlide.value) {
    return
  }

  currentSlide.value = index
  questionsStore.setCurrentSlide(props.question.id, index)
  handleSlideChange(index)
}

// Handle slide change
const handleSlideChange = (slideIndex: number) => {
  emit('slide-changed', props.question.id, slideIndex)
  // State updates for header visibility now handled by HbStepper :showHeader prop
}

// Handle refinement submission
const handleRefinementSubmit = (questionId: string, refinementData: Record<string, any>) => {
  // Emit event to parent - parent will handle state change
  emit('refinement-submitted', questionId, refinementData)

  // Set state to feedback_submitted (parent will update with formatted answer)
  questionsStore.setQuestionState(questionId, QUESTION_STEP_STATES.FEEDBACK_SUBMITTED)
}

// Handle continue button click from FeedbackSubmittedSlide
const handleFeedbackContinue = () => {
  const questionId = props.question.id

  // Return to initial state
  questionsStore.setQuestionState(questionId, QUESTION_STEP_STATES.INITIAL)

  // Navigate back to slide 0
  currentSlide.value = 0
  questionsStore.setCurrentSlide(questionId, 0)
  handleSlideChange(0)
}

// Handle "I have no experience" button click
const handleNeedHelp = () => {
  // Set NO_EXPERIENCE state for this question
  questionsStore.setQuestionState(props.question.id, QUESTION_STEP_STATES.NO_EXPERIENCE)

  // Navigate to slide 1 (NoExperienceSlide)
  currentSlide.value = 1
  questionsStore.setCurrentSlide(props.question.id, 1)
  handleSlideChange(1)
}

// Handle learning choice from NoExperienceSlide
const handleLearningChoice = (questionId: string, choice: 'learn-now' | 'open-later') => {
  // Emit to parent (QuestionsResult.vue or analyze.vue)
  emit('learning-choice', questionId, choice)
}
</script>

<style scoped lang="scss">
.question-slider {
  width: 100%;
  position: relative;
}

.slider-container {
  overflow: hidden;
  width: 100%;
  position: relative;
}

.slider-track {
  display: flex;
  width: 100%;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide {
  flex-shrink: 0;
  width: 100%;
  min-width: 100%;
  box-sizing: border-box;
}

.slide-content {
  width: 100%;
  height: 100%;
}

.dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 0 0 12px 0;

  button {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #d1d5db;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    padding: 0;

    &:hover {
      background: #9ca3af;
    }

    &.active {
      background: var(--primary-500);
      transform: scale(1.2);
    }
  }
}
</style>
