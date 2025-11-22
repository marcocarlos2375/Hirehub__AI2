<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- Top Bar -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="max-w-7xl mx-auto flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">Compatibility Analysis</h1>
        <button
          @click="handleStartNew"
          class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
        >
          ← Start New Analysis
        </button>
      </div>
    </div>

    <!-- Main Layout: Sidebar + Content -->
    <div class="flex">
      <!-- Sidebar -->
      <AnalysisSidebar
        :steps="steps as any"
        :selected-step-id="selectedStepId"
        @select-step="handleSelectStep"
      />

      <!-- Main Content Area -->
      <div class="flex-1 p-8">
        <div class="max-w-6xl mx-auto">
          <!-- Job Parsing Content -->
          <div v-if="selectedStepId === 'job-parsing'">
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

          <!-- CV Parsing Content -->
          <div v-if="selectedStepId === 'cv-parsing'">
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

          <!-- Score Calculation Content -->
          <div v-if="selectedStepId === 'score-calc'">
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

          <!-- Smart Questions Content -->
          <div v-if="selectedStepId === 'smart-questions'">
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

          <!-- Resume Rewrite Content -->
          <div v-if="selectedStepId === 'resume-rewrite'">
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
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ParsedJobResult, ParsedCVResult } from '~/composables/useAnalysisState'

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
  updateStepProgress,
  reset
} = useAnalysisState()

const { parseJob } = useJobParser()
const { parseCV } = useCVParser()
const { calculateScore } = useScoreCalculator()
const { generateQuestions } = useQuestionGenerator()
const { rewriteResume } = useResumeRewriter()

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
    }
  } catch (error) {
    console.error('Failed to rewrite resume:', error)
    updateStepProgress('resume-rewrite', 0, 'error', 'Failed to rewrite resume')
  }
}
</script>
