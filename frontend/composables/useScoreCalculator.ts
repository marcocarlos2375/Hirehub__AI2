export interface ScoreRequest {
  parsed_cv: Record<string, any>
  parsed_jd: Record<string, any>
  language: string
}

// Detailed gap analysis models (pipeline.md aligned)
export interface GapItem {
  id: string
  title: string
  current: string
  required: string
  impact: string
  severity: string
  description: string
  addressability: string
  timeframe_to_address?: string
}

export interface CategorizedGaps {
  critical: GapItem[]
  important: GapItem[]
  nice_to_have: GapItem[]
  logistical: GapItem[]
}

export interface CategoryScore {
  score: number
  weight: number
  status: string
}

export interface StrengthItem {
  title: string
  description: string
  evidence: string
}

export interface ApplicationViability {
  current_likelihood: string
  key_blockers: string[]
}

export interface ScoreResponse {
  success: boolean
  overall_score: number
  overall_status: string  // NEW: "STRONG FIT" | "MODERATE FIT" | "WEAK FIT" | "POOR FIT"
  category_scores: Record<string, CategoryScore>  // NEW: Detailed with weights and status
  gaps: CategorizedGaps  // NEW: Categorized gaps
  strengths: StrengthItem[]  // NEW: Structured strengths
  application_viability: ApplicationViability  // NEW: Viability assessment
  similarity_metrics: {
    overall_embedding_similarity: number
    skills_cosine_similarity: number
    experience_cosine_similarity: number
    experience_weighted_similarity: number
    critical_skills_match: number
    important_skills_match: number
    exact_keyword_match: number
    fuzzy_keyword_match: number
    semantic_skills_match: number
    missing_critical_skills: string[]
    matched_skills: string[]
    cache_stats: {
      l1_hits: number
      l2_hits: number
      misses: number
      total_requests: number
      hit_rate: number
    }
  }
  time_seconds: number
  model: string
}

export const useScoreCalculator = () => {
  const config = useRuntimeConfig()
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const result = ref<ScoreResponse | null>(null)

  const calculateScore = async (
    parsedCV: Record<string, any>,
    parsedJD: Record<string, any>,
    language: string = 'english'
  ): Promise<ScoreResponse | null> => {
    if (!parsedCV || !parsedJD) {
      error.value = 'Both CV and JD data are required'
      return null
    }

    isLoading.value = true
    error.value = null
    result.value = null

    try {
      const response = await $fetch<ScoreResponse>('/api/calculate-score', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          parsed_cv: parsedCV,
          parsed_jd: parsedJD,
          language: language
        }
      })

      result.value = response
      return response
    } catch (err: any) {
      const errorMessage = err?.data?.detail || err?.message || 'Failed to calculate compatibility score'
      error.value = errorMessage
      console.error('Score calculation error:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  return {
    calculateScore,
    isLoading: readonly(isLoading),
    error: readonly(error),
    result: readonly(result)
  }
}
