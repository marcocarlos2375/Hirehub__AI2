<template>
  <div
    class="original-question-slide"
    v-motion
    :initial="slideAnimations.slideRight.value.initial"
    :enter="slideAnimations.slideRight.value.enter"
    :leave="slideAnimations.slideRight.value.leave"
  >
    <!-- Show Question Context (always visible when not in adaptive flow) -->
    <QuestionContextCard
      v-if="!hasAdaptiveFlow"
      :question="question"
      variant="full"
      :show-impact="true"
      :show-context-why="true"
      :show-examples="true"
      :show-previous="questionIndex > 0"
      :show-next="showNext"
      :is-last-question="isLastQuestion"
      :all-answered="allAnswered"
      @need-help="$emit('need-help', question)"
      @navigate="$emit('navigate', $event)"
      @submit-all="$emit('submit-all')"
    />

    <!-- Adaptive Flow (shown inline after modal choice) -->
    <div v-if="hasAdaptiveFlow" class="ml-4 pl-4 border-l-4 border-indigo-300">
      <AdaptiveQuestionFlow
        :question-id="question.id"
        :question-text="question.question_text"
        :question-data="question"
        :gap-info="{ title: question.title, description: question.context_why }"
        :user-id="userId"
        :parsed-cv="parsedCv"
        :parsed-jd="parsedJd"
        :language="language"
        :initial-experience-level="adaptiveExperienceLevel"
        @complete="(state) => $emit('adaptive-complete', question.id, state)"
        @cancel="() => $emit('adaptive-cancel', question.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { OriginalQuestionSlideProps, OriginalQuestionSlideEmits } from '~/types/component-props'
import { useQuestionsStore } from '~/stores/questions/useQuestionsStore'
import { useSlideAnimations } from '~/composables/animation/useSlideAnimations'

const props = withDefaults(defineProps<OriginalQuestionSlideProps>(), {
  language: 'english',
  totalQuestions: 0,
  allAnswered: false
})

const emit = defineEmits<OriginalQuestionSlideEmits>()

const questionsStore = useQuestionsStore()
const slideAnimations = useSlideAnimations()

// Get user ID (simplified - adjust based on your auth system)
const userId = computed(() => {
  // You may need to adjust this based on your auth system
  return 'default-user-id'
})

// Check if question has active adaptive flow
const hasAdaptiveFlow = computed(() => {
  return questionsStore.hasActiveAdaptiveFlow(props.question.id)
})

// Check if question has evaluation
const hasEvaluation = computed(() => {
  return questionsStore.getEvaluationById(props.question.id) !== undefined
})

// Get adaptive experience level
const adaptiveExperienceLevel = computed(() => {
  return questionsStore.getAdaptiveExperienceLevel(props.question.id)
})

// Navigation helpers
const showNext = computed(() => {
  return props.questionIndex < (props.totalQuestions - 1)
})

const isLastQuestion = computed(() => {
  return props.questionIndex === (props.totalQuestions - 1)
})
</script>

<style scoped>
.original-question-slide {
  /* GPU acceleration for smooth animations */
  will-change: transform, opacity;
  transform: translateZ(0);
  backface-visibility: hidden;
}
</style>
