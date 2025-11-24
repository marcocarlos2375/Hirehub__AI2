export interface DomainMatch {
  domain_name: string  // Format: "Role - Industry"
  technical_role: string  // e.g., "Backend Developer", "Senior API Engineer"
  industry: string  // e.g., "Gaming", "FinTech", "HealthTech"
  fit_score: number
  rank: number
  matching_skills: string[]  // Combined role + industry skills
  skills_to_learn: string[]  // Combined list (for backwards compatibility)
  role_skills_to_learn: string[]  // Technical skills needed for role
  industry_skills_to_learn: string[]  // Domain knowledge for industry
  learning_priority: 'HIGH' | 'MEDIUM' | 'LOW'
  time_to_ready: string
  reasoning: string  // Why this ROLE fits
  industry_rationale: string  // Why this INDUSTRY matches
}

export interface DomainFinderRequest {
  resume_text: string
  language: string
}

export interface DomainFinderResponse {
  success: boolean
  domains: DomainMatch[] | null
  total_suggested: number
  error: string | null
  time_seconds: number
  model: string
  language: string
}

export const useDomainFinder = () => {
  const config = useRuntimeConfig()
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const result = ref<DomainFinderResponse | null>(null)

  const findDomains = async (resumeText: string, language: string = 'english', bypassCache: boolean = false): Promise<DomainFinderResponse | null> => {
    if (!resumeText || resumeText.trim().length < 50) {
      error.value = 'Resume text must be at least 50 characters'
      return null
    }

    // Auto-truncate if over 6200 characters
    const truncatedText = resumeText.length > 6200
      ? resumeText.substring(0, 6200)
      : resumeText

    isLoading.value = true
    error.value = null
    result.value = null

    try {
      // Build URL with bypass_cache query parameter if needed
      const url = bypassCache
        ? '/api/find-domains?bypass_cache=true'
        : '/api/find-domains'

      const response = await $fetch<DomainFinderResponse>(url, {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: {
          resume_text: truncatedText,
          language: language
        }
      })

      result.value = response
      return response
    } catch (err: any) {
      const errorMessage = err?.data?.detail || err?.message || 'Failed to analyze domains'
      error.value = errorMessage
      console.error('Domain finder error:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  return {
    findDomains,
    isLoading: readonly(isLoading),
    error: readonly(error),
    result: readonly(result)
  }
}
