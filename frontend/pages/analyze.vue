<template>
  <div class="min-h-screen py-16 page-with-bg">
    <div class="container mx-auto px-4">
     

      <!-- Card Container -->
      <div>
        <!-- Loading State -->
        <div v-if="isLoading" class="bg-white py-24 px-8 rounded-b-lg max-w-7xl mx-auto flex flex-col items-center justify-center min-h-[400px]">
          <HbSpinner size="xl" />
          <p class="text-gray-600 mt-4 font-medium">Loading...</p>
        </div>

        <!-- Wizard Layout -->
        <div v-else class="layout bg-white rounded-b-lg max-w-7xl mx-auto">
          <!-- Sidebar -->
          <div class="sidebar bg-primary-900 text-white">
            <div class="p-6">
              <div class="flex items-center justify-between mb-6">
                <h2 class="text-lg font-semibold">Job Match Analysis</h2>
              </div>

              <!-- Pipeline Steps Navigation -->
              <nav class="space-y-1 sidebar-nav-scrollable">
                <button
                  v-for="(step, index) in steps"
                  :key="step.id"
                  @click="handleSelectStep(step.id)"
                  class="step-button w-full text-left"
                  :class="{
                    'step-button--active': selectedStepId === step.id,
                    'step-button--disabled': step.status === 'pending'
                  }"
                  :disabled="step.status === 'pending'"
                >
                  <!-- Progress Bar -->
                  <div
                    v-if="step.status === 'loading'"
                    class="step-progress-bar"
                  >
                    <div
                      class="step-progress-fill"
                      :style="{ width: step.progress + '%' }"
                    ></div>
                  </div>

                  <div class="flex items-center gap-3 p-3 rounded-lg transition-all">
                    <!-- Step Number -->
                    <div class="step-number">
                      <span class="relative z-10">{{ index + 1 }}</span>
                    </div>
                    <div class="step-info">
                      <div class="step-title">{{ step.label }}</div>
                      <div class="step-subtitle">
                        {{ step.status === 'loading' ? Math.round(step.progress) + '% Complete' :
                           step.status === 'complete' ? '100% Complete' :
                           step.status === 'error' ? 'Error' : 'Waiting...' }}
                      </div>
                    </div>
                  </div>
                </button>
              </nav>
            </div>
          </div>

          <!-- Main Content Area -->
          <div class="content">
            <!-- Job Parsing Step -->
            <div v-if="selectedStepId === 'job-parsing'" class="content-animated">
              <div class="content">
                <JobParsingResult
                  v-if="parsedJD"
                  :data="parsedJD as any"
                  :time-seconds="jdParseTime || undefined"
                />
                <WaitingMessage
                  v-else-if="getStep('job-parsing')?.status === 'loading'"
                  type="loading"
                  title="Parsing Job Description"
                  message="Analyzing job requirements, extracting skills, responsibilities, and tech stack..."
                />
                <WaitingMessage
                  v-else-if="getStep('job-parsing')?.status === 'error'"
                  type="error"
                  title="Parsing Failed"
                  :message="getStep('job-parsing')?.error || 'An error occurred while parsing the job description'"
                />
                <WaitingMessage
                  v-else
                  type="pending"
                  title="Waiting for Job Description"
                  message="Job description parsing has not started yet."
                />
              </div>
            </div>

            <!-- CV Parsing Step -->
            <div v-if="selectedStepId === 'cv-parsing'" class="content-animated">
              <div class="content">
                <CVParsingResult
                  v-if="parsedCV"
                  :data="parsedCV as any"
                  :time-seconds="cvParseTime || undefined"
                />
                <WaitingMessage
                  v-else-if="getStep('cv-parsing')?.status === 'loading'"
                  type="loading"
                  title="Parsing Resume/CV"
                  message="Extracting skills, experience, education, projects, and achievements..."
                />
                <WaitingMessage
                  v-else-if="getStep('cv-parsing')?.status === 'error'"
                  type="error"
                  title="Parsing Failed"
                  :message="getStep('cv-parsing')?.error || 'An error occurred while parsing the CV'"
                />
                <WaitingMessage
                  v-else
                  type="pending"
                  title="Waiting for CV"
                  message="CV parsing has not started yet."
                />
              </div>
            </div>

            <!-- Score Calculation Step -->
            <div v-if="selectedStepId === 'score-calc'" class="content-animated">
              <div class="content">
                <ScoreResult
                  v-if="scoreResult"
                  :data="scoreResult as any"
                  :time-seconds="scoreCalcTime || undefined"
                />
                <WaitingMessage
                  v-else-if="getStep('score-calc')?.status === 'loading'"
                  type="loading"
                  title="Calculating Compatibility Score"
                  message="Analyzing embeddings, calculating category scores, identifying gaps and strengths..."
                />
                <WaitingMessage
                  v-else-if="getStep('score-calc')?.status === 'error'"
                  type="error"
                  title="Calculation Failed"
                  :message="getStep('score-calc')?.error || 'An error occurred while calculating the score'"
                />
                <WaitingMessage
                  v-else
                  type="pending"
                  title="Waiting for Parsing to Complete"
                  message="Score calculation will begin once both job description and CV are successfully parsed."
                />
              </div>
            </div>

            <!-- Smart Questions Step -->
            <div v-if="selectedStepId === 'smart-questions'" class="content-animated">
              <div class="content">
                <QuestionsResult
                  v-if="questionsResult"
                  :questions-data="questionsResult as any"
                  :parsed-c-v="parsedCV!"
                  :parsed-j-d="parsedJD!"
                  :original-score="scoreResult?.overall_score || 0"
                  :time-seconds="questionsGenTime || 0"
                  :language="selectedLanguage"
                  @answers-submitted="handleAnswersSubmitted"
                />
                <WaitingMessage
                  v-else-if="getStep('smart-questions')?.status === 'loading'"
                  type="loading"
                  title="Generating Smart Questions"
                  message="Using AI and RAG to create personalized questions based on your gaps..."
                />
                <WaitingMessage
                  v-else-if="getStep('smart-questions')?.status === 'error'"
                  type="error"
                  title="Question Generation Failed"
                  :message="getStep('smart-questions')?.error || 'An error occurred while generating questions'"
                />
                <WaitingMessage
                  v-else
                  type="pending"
                  title="Waiting for Score Calculation"
                  message="Smart questions will be generated once compatibility score is calculated."
                />
              </div>
            </div>

            <!-- Resume Rewrite Step -->
            <div v-if="selectedStepId === 'resume-rewrite'" class="content-animated">
              <div class="content">
                <ResumeRewriteResult
                  v-if="rewrittenResume"
                  :sample-format="rewrittenResume.sample_format"
                  :parsed-format="rewrittenResume.parsed_format"
                  :enhancements-made="rewrittenResume.enhancements_made as any"
                  :time-seconds="rewrittenResume.time_seconds || 0"
                />
                <WaitingMessage
                  v-else-if="getStep('resume-rewrite')?.status === 'loading'"
                  type="loading"
                  title="Rewriting Your Resume"
                  message="AI is enhancing your resume with insights from your answers..."
                />
                <WaitingMessage
                  v-else-if="getStep('resume-rewrite')?.status === 'error'"
                  type="error"
                  title="Resume Rewrite Failed"
                  :message="getStep('resume-rewrite')?.error || 'An error occurred while rewriting the resume'"
                />
                <WaitingMessage
                  v-else
                  type="pending"
                  title="Waiting for Answers"
                  message="Your resume will be rewritten once you complete all questions."
                />
              </div>
            </div>

            <!-- Cover Letter Step -->
            <div v-if="selectedStepId === 'cover-letter'" class="content-animated">
              <div class="content">
                <CoverLetterResult
                  v-if="coverLetter"
                  :cover-letter="coverLetter.cover_letter"
                  :word-count="coverLetter.word_count"
                  :time-seconds="coverLetter.time_seconds"
                />
                <WaitingMessage
                  v-else-if="getStep('cover-letter')?.status === 'loading'"
                  type="loading"
                  title="Generating Cover Letter"
                  message="Creating a personalized cover letter based on your rewritten resume..."
                />
                <WaitingMessage
                  v-else-if="getStep('cover-letter')?.status === 'error'"
                  type="error"
                  title="Cover Letter Generation Failed"
                  :message="getStep('cover-letter')?.error || 'An error occurred while generating the cover letter'"
                />
                <WaitingMessage
                  v-else
                  type="pending"
                  title="Waiting for Resume Rewrite"
                  message="Cover letter will be generated once your resume is rewritten."
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ParsedJobResult, ParsedCVResult } from '~/composables/analysis/useAnalysisState'

const router = useRouter()
const {
  inputJD,
  inputCV,
  selectedLanguage,
  parsedJD,
  parsedCV,
  scoreResult,
  questionsResult,
  answersResult,
  rewrittenResume,
  coverLetter,
  jdParseTime,
  cvParseTime,
  scoreCalcTime,
  questionsGenTime,
  steps,
  selectedStepId,
  setParsedJD,
  setParsedCV,
  setScore,
  setQuestions,
  setAnswersResult,
  setRewrittenResume,
  setCoverLetter,
  updateStepProgress,
  reset
} = useAnalysisState()

const { parseJob } = useJobParser()
const { parseCV } = useCVParser()
const { calculateScore } = useScoreCalculator()
const { generateQuestions } = useQuestionGenerator()
const { rewriteResume } = useResumeRewriter()
const { generateCoverLetter } = useCoverLetterGenerator()

const isLoading = ref(false)

// Redirect if no input
onMounted(() => {
  if (!inputJD.value || !inputCV.value) {
    router.push('/')
    return
  }

  // Start parallel processing
  startAnalysis()
})

const getStep = (stepId: string) => {
  return steps.value.find(s => s.id === stepId) || steps.value[0]
}

const handleSelectStep = (stepId: string) => {
  selectedStepId.value = stepId
}

const handleStartNew = () => {
  reset()
  router.push('/')
}

const startAnalysis = async () => {
  // Phase 1: Parse JD and CV in parallel
  const jdPromise = parseJobDescription()
  const cvPromise = parseResume()

  // Wait for both to complete
  const [jdResult, cvResult] = await Promise.all([jdPromise, cvPromise])

  // Phase 2: Calculate score only if both parsing succeeded
  if (jdResult && cvResult) {
    await calculateCompatibilityScore(jdResult, cvResult)
  }
}

const parseJobDescription = async () => {
  try {
    updateStepProgress('job-parsing', 0, 'loading')

    // Simulate progress updates
    const progressInterval = setInterval(() => {
      const currentStep = getStep('job-parsing')
      if (currentStep && currentStep.progress < 90) {
        updateStepProgress('job-parsing', currentStep.progress + 10, 'loading')
      }
    }, 300)

    const result = await parseJob(inputJD.value, selectedLanguage.value)

    clearInterval(progressInterval)

    if (result && result.success && result.data) {
      setParsedJD(result.data as ParsedJobResult, result.time_seconds)
      updateStepProgress('job-parsing', 100, 'complete')
      return result.data as ParsedJobResult
    } else {
      updateStepProgress('job-parsing', 0, 'error', result?.error || 'Parsing failed')
      return null
    }
  } catch (error: any) {
    updateStepProgress('job-parsing', 0, 'error', error.message || 'Parsing failed')
    return null
  }
}

const parseResume = async () => {
  try {
    updateStepProgress('cv-parsing', 0, 'loading')

    // Simulate progress updates
    const progressInterval = setInterval(() => {
      const currentStep = getStep('cv-parsing')
      if (currentStep && currentStep.progress < 90) {
        updateStepProgress('cv-parsing', currentStep.progress + 10, 'loading')
      }
    }, 300)

    const result = await parseCV(inputCV.value, selectedLanguage.value)

    clearInterval(progressInterval)

    if (result && result.success && result.data) {
      setParsedCV(result.data as ParsedCVResult, result.time_seconds)
      updateStepProgress('cv-parsing', 100, 'complete')
      return result.data as ParsedCVResult
    } else {
      updateStepProgress('cv-parsing', 0, 'error', result?.error || 'Parsing failed')
      return null
    }
  } catch (error: any) {
    updateStepProgress('cv-parsing', 0, 'error', error.message || 'Parsing failed')
    return null
  }
}

const calculateCompatibilityScore = async (jd: any, cv: any) => {
  try {
    updateStepProgress('score-calc', 0, 'loading')

    // Simulate progress updates
    const progressInterval = setInterval(() => {
      const currentStep = getStep('score-calc')
      if (currentStep && currentStep.progress < 90) {
        updateStepProgress('score-calc', currentStep.progress + 10, 'loading')
      }
    }, 400)

    const result = await calculateScore(cv, jd, selectedLanguage.value)

    clearInterval(progressInterval)

    if (result) {
      setScore(result, result.time_seconds)
      updateStepProgress('score-calc', 100, 'complete')

      // Auto-select score tab when complete
      selectedStepId.value = 'score-calc'

      // Phase 4: Generate smart questions after score is calculated
      await generateSmartQuestions(cv, jd, result)
    } else {
      updateStepProgress('score-calc', 0, 'error', 'Score calculation failed')
    }
  } catch (error: any) {
    updateStepProgress('score-calc', 0, 'error', error.message || 'Score calculation failed')
  }
}

const generateSmartQuestions = async (cv: any, jd: any, score: any) => {
  try {
    updateStepProgress('smart-questions', 0, 'loading')

    // Simulate progress updates
    const progressInterval = setInterval(() => {
      const currentStep = getStep('smart-questions')
      if (currentStep && currentStep.progress < 90) {
        updateStepProgress('smart-questions', currentStep.progress + 10, 'loading')
      }
    }, 300)

    const result = await generateQuestions(cv, jd, score, selectedLanguage.value)

    clearInterval(progressInterval)

    if (result) {
      setQuestions(result as any, result.time_seconds)
      updateStepProgress('smart-questions', 100, 'complete')

      // Auto-select questions tab when complete
      selectedStepId.value = 'smart-questions'
    } else {
      updateStepProgress('smart-questions', 0, 'error', 'Question generation failed')
    }
  } catch (error: any) {
    updateStepProgress('smart-questions', 0, 'error', error.message || 'Question generation failed')
  }
}

const handleAnswersSubmitted = async (result: any, answers: any, updatedCV: any) => {
  setAnswersResult(result, result.time_seconds)

  // Automatically trigger resume rewrite (Phase 5)
  await triggerResumeRewrite(updatedCV, answers)
}

const triggerResumeRewrite = async (updatedCV: any, answers: any) => {
  try {
    // Update step status
    updateStepProgress('resume-rewrite', 0, 'loading')
    selectedStepId.value = 'resume-rewrite'

    // Call API to rewrite resume with questions
    const result = await rewriteResume(
      updatedCV,
      questionsResult.value!.questions as any,
      answers,
      parsedJD.value!,
      selectedLanguage.value
    )

    if (result) {
      setRewrittenResume(result)
      updateStepProgress('resume-rewrite', 100, 'complete')

      // Automatically trigger cover letter generation (Phase 6)
      await triggerCoverLetterGeneration(result)
    }
  } catch (error) {
    console.error('Failed to rewrite resume:', error)
    updateStepProgress('resume-rewrite', 0, 'error', 'Failed to rewrite resume')
  }
}

const triggerCoverLetterGeneration = async (rewriteResult: any) => {
  try {
    // Update step status
    updateStepProgress('cover-letter', 0, 'loading')
    selectedStepId.value = 'cover-letter'

    // Pass parsed_format directly to backend - no text conversion needed in frontend!
    const result = await generateCoverLetter(
      rewriteResult.parsed_format,
      parsedJD.value!,
      scoreResult.value || undefined,
      selectedLanguage.value
    )

    if (result) {
      setCoverLetter(result)
      updateStepProgress('cover-letter', 100, 'complete')
    }
  } catch (error) {
    console.error('Failed to generate cover letter:', error)
    updateStepProgress('cover-letter', 0, 'error', 'Failed to generate cover letter')
  }
}
</script>

<style scoped lang="scss">




/* Wizard Layout */
.layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  height: 85vh;
  overflow: hidden;
  border-radius:  0.5rem;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-bottom-left-radius: 0.5rem;
}

.sidebar-nav-scrollable {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: thin;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    border-radius: 3px;
  }
}

.content {
  height: 85vh;
  display: flex;
  flex-direction: column;
  background-color: white;
  border-bottom-right-radius: 0.5rem;
  overflow-y: auto;
}

.content-animated {
  flex: 1;
  overflow-y: auto;

  .content {
    height: auto;
    padding: 2rem;
  }
}

/* Sidebar Steps */
.step-button {
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  background: transparent;
  border-radius: 0.5rem;
  position: relative;

  &:hover:not(:disabled) {
    background-color: rgba(255, 255, 255, 0.05);
  }

  &--active {
    background-color: rgba(255, 255, 255, 0.1);
  }

  &--disabled {
    opacity: 0.4;
    cursor: not-allowed;

    .step-number {
      background-color: rgba(255, 255, 255, 0.05);
    }

    .step-title,
    .step-subtitle {
      color: rgba(255, 255, 255, 0.5);
    }
  }

  &:disabled {
    pointer-events: none;
  }
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 600;
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  flex-shrink: 0;
  position: relative;

  .step-button--active & {
    background-color: var(--primary-500);
  }
}

.step-info {
  flex: 1;
  min-width: 0;
}

.step-title {
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.step-subtitle {
  font-size: 0.75rem;
  opacity: 0.7;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.step-progress-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 0;
  overflow: hidden;
}

.step-progress-fill {
  height: 100%;
  background-color: var(--primary-500);
  transition: width 0.3s ease;
  border-radius: 0;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .page-with-bg {
    padding: 0.5rem;
  }

  .layout {
    grid-template-columns: 1fr;
    height: auto;
    min-height: calc(100vh - 120px);
  }

  .sidebar {
    height: auto;
    border-radius: 0.5rem 0.5rem 0 0;
    border-bottom-left-radius: 0;

    .p-6 {
      padding: 1rem;
    }
  }

  .content {
    height: auto;
    min-height: 400px;
    border-radius: 0 0 0.5rem 0.5rem;
    border-bottom-right-radius: 0.5rem;
  }

  .content-animated .content {
    padding: 1rem;
  }

  .sidebar-nav-scrollable {
    max-height: 250px;
  }
}
</style>
