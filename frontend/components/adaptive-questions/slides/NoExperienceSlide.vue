<template>
  <div
    class="no-experience-slide"
    v-motion
    :initial="slideAnimations.slideLeft.value.initial"
    :enter="slideAnimations.slideLeft.value.enter"
    :leave="slideAnimations.slideLeft.value.leave"
  >
    <!-- Content -->
    <div class="content-wrapper">
      <!-- Title -->
      <h3 class="title">
        No Experience with {{ question.title }}?
      </h3>

      <!-- 2 Column Layout -->
      <div class="two-column-layout">
        <!-- Column 1: Card Selection -->
        <div class="column-cards">
          <HbCardSelect
            v-model="selectedOption"
            :options="learningOptions"
            :columns="1"
            option-label="label"
            option-value="value"
          >
            <template #card="{ option }">
              <div class="option-content">
                <!-- Left: Icon -->
                <div class="option-icon">
                  <HbIcon :name="(option as LearningOption).icon" :width="32" :height="32" />
                </div>

                <!-- Middle: Text content -->
                <div class="option-text">
                  <div class="option-label">{{ (option as LearningOption).label }}</div>
                  <div class="option-description">{{ (option as LearningOption).description }}</div>
                </div>

                <!-- Right: Check icon (only shown when selected) -->
                <div v-if="isSelected(option as LearningOption)" class="option-check">
                  <HbIcon name="check-circle" :width="24" :height="24" />
                </div>
              </div>
            </template>
          </HbCardSelect>

          <!-- Platform icons section (shown only for "learn-now" option) -->
         <!-- <div v-if="selectedOption === 'learn-now' && getSelectedPlatforms().length > 0" class="platform-section">
            <p class="platform-text">Curated resources from top platforms</p>
            <div class="platform-icons">
              <HbIcon
                v-for="platform in getSelectedPlatforms()"
                :key="platform"
                :name="platform"
                :width="70"
                :height="70"
                class="platform-icon"
              />
            </div>
          </div>-->
        </div>

        <!-- Column 2: AI Analysis Text -->
        <div v-if="analysis" class="column-text">
          <!-- Opening paragraph -->
          <p class="intro">
            {{ analysis.intro }}
          </p>

          <!-- Key points -->
          <ul class="key-points">
            <li v-for="(point, index) in analysis.key_points" :key="index">
              {{ point }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useSlideAnimations } from '~/composables/animation/useSlideAnimations'
import type { QuestionItem } from '~/composables/analysis/useAnalysisState'
import type { SkillGapAnalysis } from '~/types/adaptive-questions'

interface Props {
  question: QuestionItem
  isActive: boolean
  parsedCv: Record<string, any>
  parsedJd: Record<string, any>
  analysis: SkillGapAnalysis | null  // Pre-loaded data from parent
}

interface LearningOption {
  value: string
  label: string
  description: string
  icon: string
  platforms: string[]  // Array of platform icon names
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'learning-choice', questionId: string, choice: 'learn-now' | 'open-later'): void
}>()

const slideAnimations = useSlideAnimations()

// Selected option (v-model for HbCardSelect)
const selectedOption = ref<string | null>(null)

// Helper to extract recommended level from key points
const getRecommendedLevel = (): string => {
  if (!props.analysis?.key_points) return 'Proficient'

  const points = props.analysis.key_points.join(' ').toLowerCase()

  if (points.includes('advanced')) return 'Advanced'
  if (points.includes('intermediate')) return 'Intermediate'
  if (points.includes('beginner') || points.includes('basic')) return 'Beginner'

  return 'Proficient'
}

// Computed property for dynamic learning options
const learningOptions = computed<LearningOption[]>(() => {
  if (!props.analysis) {
    // Default options when no analysis available
    return [
      {
        value: 'learn-now',
        label: 'I want to learn this now',
        description: 'Get personalized course recommendations and add "Currently Learning" to your resume',
        icon: 'graduation-cap',
        platforms: ['coursera-wordmark', 'udemy-wordmark', 'youtube-wordmark', 'freecodecamp']
      },
      {
        value: 'open-later',
        label: 'Open to learning later',
        description: 'Add "Willing to Learn" to your resume for this skill',
        icon: 'clock',
        platforms: []
      }
    ]
  }

  const isRelatedSkill = props.analysis.case === 'A'

  return [
    {
      value: 'learn-now',
      label: 'I want to learn this now',
      description: isRelatedSkill
        ? `Get advanced tutorials for ${props.analysis.skill_missing} and add to your CV at ${getRecommendedLevel()} level`
        : `Start with basics module and add "Currently Learning" to your resume`,
      icon: 'graduation-cap',
      platforms: isRelatedSkill
        ? ['pluralsight', 'udemy-wordmark']  // Advanced platforms
        : ['coursera-wordmark', 'udemy-wordmark', 'youtube-wordmark', 'freecodecamp']  // Beginner platforms
    },
    {
      value: 'open-later',
      label: 'Open to learning later',
      description: 'Add "Willing to Learn" to your resume for this skill',
      icon: 'clock',
      platforms: []  // No platforms needed
    }
  ]
})

// Check if option is selected
const isSelected = (option: LearningOption) => {
  // Handle both cases: selectedOption could be a string (value) or the whole object
  if (typeof selectedOption.value === 'string') {
    return selectedOption.value === option.value
  }
  if (typeof selectedOption.value === 'object' && selectedOption.value !== null) {
    return (selectedOption.value as any).value === option.value
  }
  return false
}

// Get platforms for the currently selected option
const getSelectedPlatforms = (): string[] => {
  const learnNowOption = learningOptions.value.find(opt => opt.value === 'learn-now')
  return learnNowOption?.platforms || []
}

// Watch for selection changes and emit to parent
watch(selectedOption, (newValue) => {
  if (newValue) {
    emit('learning-choice', props.question.id, newValue as 'learn-now' | 'open-later')
  }
})
</script>

<style scoped>
.no-experience-slide {
  padding: 1.7rem 0.8rem;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

.title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827; /* gray-900 */
  margin-bottom: 0.75rem;
}

/* 2 Column Layout */
.two-column-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  width: 100%;
  max-width: 1000px;
  margin-bottom: 1rem;
}

/* Column 1: Cards */
.column-cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Column 2: Text */
.column-text {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.intro {
  font-size: 0.95rem;
  font-weight: 500;
  color: #374151; /* gray-700 */
  margin-bottom: 1rem;
  line-height: 1.5;
}

.key-points {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.key-points li {
  position: relative;
  padding-left: 1.5rem;
  font-size: 14px;
  color: #4b5563; /* gray-600 */
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

.key-points li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.5em;
  width: 6px;
  height: 6px;
  background-color: var(--primary-400);
  border-radius: 2px;
}

/* Remove box shadow from cards */
.column-cards :deep(.hb-card-select-option) {
  box-shadow: none !important;
}

.option-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
}

.option-icon {
  flex-shrink: 0;
  color: var(--primary-500);
}

.option-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  text-align: left;
}

.option-label {
  font-size: 1rem;
  font-weight: 600;
  color: #111827; /* gray-900 */
  line-height: 1.3;
}

.option-description {
  font-size: 0.875rem;
  color: #6b7280; /* gray-500 */
  line-height: 1.4;
}

.platform-section {
  margin-top: 1.5rem;
  text-align: center;
}

.platform-text {
  font-size: 0.675rem;
  color: #6b7280; /* gray-500 */
  margin-bottom: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.platform-icons {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  justify-content: center;
}

.platform-icon {
  opacity: 0.4;
  filter: grayscale(100%);
  transition: opacity 0.2s ease;
}

.platform-icon:hover {
  opacity: 0.6;
}

.option-check {
  flex-shrink: 0;
  color: var(--primary-500);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  /* Stack columns vertically on mobile */
  .two-column-layout {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  /* On mobile, show text first, then cards */
  .column-text {
    order: 1;
  }

  .column-cards {
    order: 2;
  }
}

@media (max-width: 640px) {
  .title {
    font-size: 1.25rem;
  }

  .intro {
    font-size: 0.875rem;
  }

  .key-points li {
    font-size: 0.8125rem;
  }

  .option-content {
    padding: 0.75rem;
  }

  .option-label {
    font-size: 0.9375rem;
  }

  .option-description {
    font-size: 0.8125rem;
  }
}
</style>
