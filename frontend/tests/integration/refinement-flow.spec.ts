import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useAdaptiveQuestions } from '~/composables/adaptive-questions/useAdaptiveQuestions'

describe('Answer Refinement Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should complete full refinement cycle: poor answer → refinement → improved score', async () => {
    const { evaluateAnswer, refineAnswer } = useAdaptiveQuestions()

    // Step 1: Submit poor answer and get evaluation
    const poorAnswerResponse = {
      success: true,
      question_id: 'test_q1',
      answer_text: 'I built a chatbot',
      quality_score: 4,
      quality_issues: [
        'Too vague - lacks specific details',
        'No metrics or quantifiable results',
        'Missing technical implementation details'
      ],
      quality_strengths: [],
      improvement_suggestions: [
        'Add specific metrics like "Tested with 50 beta users achieving 87% query resolution rate"',
        'Specify architecture and scale like "Built microservices handling 10K requests/sec using Node.js + Redis"',
        'Add project scope and duration like "6-month development across 3 agile sprints"'
      ],
      is_acceptable: false,
      time_seconds: 1.5,
      model: 'gemini-2.0-flash-exp'
    }

    vi.mocked($fetch).mockResolvedValueOnce(poorAnswerResponse)

    const evaluation = await evaluateAnswer(
      'test_q1',
      'Describe a chatbot project you built',
      'I built a chatbot',
      {
        title: 'AI/Chatbot Development',
        description: 'Missing experience in AI chatbots'
      },
      'english'
    )

    // Assertions for poor answer evaluation
    expect(evaluation.quality_score).toBeLessThan(7)
    expect(evaluation.is_acceptable).toBe(false)
    expect(evaluation.quality_issues.length).toBeGreaterThan(0)
    expect(evaluation.improvement_suggestions.length).toBeGreaterThan(0)

    // Step 2: User provides refinement data
    const refinementData = {
      'Metrics': 'Tested with 50 beta users achieving 87% query resolution rate and 4.2/5 satisfaction score',
      'Technical Details': 'Built using Python, OpenAI GPT-3.5 API, Flask framework, deployed on AWS EC2 with auto-scaling',
      'Timeline': 'Completed 6-month development across 3 agile sprints, delivered MVP in 8 weeks'
    }

    // Step 3: Submit refinement and get improved answer
    const refinedResponse = {
      question_id: 'test_q1',
      refined_answer: `I built an AI-powered customer support chatbot using Python and OpenAI GPT-3.5 API. The chatbot was tested with 50 beta users and achieved an 87% query resolution rate with a 4.2/5 satisfaction score. The technical stack included Flask framework for the backend and was deployed on AWS EC2 with auto-scaling capabilities. The project spanned 6 months across 3 agile sprints, with an MVP delivered in 8 weeks. The system handled over 2,000 daily requests with an average response time of 340ms.`,
      quality_score: 8,
      quality_issues: [],
      quality_strengths: [
        'Specific metrics and measurable results',
        'Clear technical implementation details',
        'Well-defined timeline and scope'
      ],
      improvement_suggestions: [],
      current_step: 'quality_evaluation',
      iteration: 1,
      is_acceptable: true
    }

    vi.mocked($fetch).mockResolvedValueOnce(refinedResponse)

    const refined = await refineAnswer(
      'test_q1',
      'Describe a chatbot project you built',
      {
        id: 'test_q1',
        question_text: 'Describe a chatbot project you built',
        title: 'AI/Chatbot Development'
      },
      {
        title: 'AI/Chatbot Development',
        description: 'Missing experience in AI chatbots'
      },
      evaluation.answer_text,
      evaluation.quality_issues,
      refinementData
    )

    // Assertions for refined answer
    expect(refined.quality_score).toBeGreaterThanOrEqual(7)
    expect(refined.quality_score).toBeGreaterThan(evaluation.quality_score)
    expect(refined.refined_answer).toContain('50 beta users')
    expect(refined.refined_answer).toContain('87%')
    expect(refined.refined_answer).toContain('Python')
    expect(refined.refined_answer).toContain('6 months')
    expect(refined.iteration).toBe(1)
  })

  it('should handle max iteration limit (2 iterations)', async () => {
    const { evaluateAnswer, refineAnswer } = useAdaptiveQuestions()

    // First evaluation - score 4
    vi.mocked($fetch).mockResolvedValueOnce({
      success: true,
      question_id: 'test_q2',
      answer_text: 'I worked on a project',
      quality_score: 4,
      quality_issues: ['Too vague'],
      improvement_suggestions: ['Add details'],
      is_acceptable: false,
      time_seconds: 1.0,
      model: 'gemini-2.0-flash-exp'
    })

    const eval1 = await evaluateAnswer(
      'test_q2',
      'Describe your project',
      'I worked on a project',
      { title: 'Test', description: 'Test' }
    )

    // First refinement - score still 5 (not acceptable)
    vi.mocked($fetch).mockResolvedValueOnce({
      question_id: 'test_q2',
      refined_answer: 'I worked on a project with some details',
      quality_score: 5,
      quality_issues: ['Still vague'],
      is_acceptable: false,
      current_step: 'quality_evaluation',
      iteration: 1
    })

    const refined1 = await refineAnswer(
      'test_q2',
      'Describe your project',
      {},
      { title: 'Test', description: 'Test' },
      eval1.answer_text,
      eval1.quality_issues,
      { 'Details': 'Some details' }
    )

    expect(refined1.iteration).toBe(1)
    expect(refined1.is_acceptable).toBe(false)

    // Second refinement - iteration 2, system should accept even if score < 7
    vi.mocked($fetch).mockResolvedValueOnce({
      question_id: 'test_q2',
      refined_answer: 'I worked on a project with more details',
      quality_score: 6,
      quality_issues: [],
      is_acceptable: true, // Accepted due to max iterations
      current_step: 'final_answer',
      iteration: 2
    })

    const refined2 = await refineAnswer(
      'test_q2',
      'Describe your project',
      {},
      { title: 'Test', description: 'Test' },
      refined1.refined_answer,
      refined1.quality_issues || [],
      { 'More': 'More details' }
    )

    expect(refined2.iteration).toBe(2)
    expect(refined2.is_acceptable).toBe(true) // Accepted at max iterations
  })

  it('should preserve context through refinement iterations', async () => {
    const { refineAnswer } = useAdaptiveQuestions()

    const questionData = {
      id: 'test_q3',
      question_text: 'Describe your leadership experience',
      title: 'Leadership Skills',
      context_why: 'Job requires team leadership'
    }

    const gapInfo = {
      title: 'Leadership Skills',
      description: 'Missing leadership experience'
    }

    vi.mocked($fetch).mockResolvedValueOnce({
      question_id: 'test_q3',
      refined_answer: 'Refined answer with context preserved',
      quality_score: 8,
      current_step: 'quality_evaluation',
      iteration: 1
    })

    await refineAnswer(
      'test_q3',
      questionData.question_text,
      questionData,
      gapInfo,
      'Original answer',
      ['Issue 1'],
      { 'Leadership': 'Led team of 5 developers' }
    )

    // Verify that all context was passed to API
    expect($fetch).toHaveBeenCalledWith(
      '/api/adaptive-questions/refine-answer',
      expect.objectContaining({
        body: expect.objectContaining({
          question_id: 'test_q3',
          question_text: 'Describe your leadership experience',
          question_data: questionData,
          gap_info: gapInfo,
          generated_answer: 'Original answer',
          quality_issues: ['Issue 1']
        })
      })
    )
  })

  it('should handle refinement errors gracefully', async () => {
    const { refineAnswer } = useAdaptiveQuestions()

    vi.mocked($fetch).mockRejectedValueOnce({
      status: 422,
      statusText: 'Unprocessable Entity',
      data: {
        detail: 'Missing required field: question_text'
      }
    })

    await expect(
      refineAnswer(
        'test_q4',
        'Test',
        {},
        { title: 'Test', description: 'Test' },
        'Test',
        [],
        {}
      )
    ).rejects.toThrow()
  })
})
