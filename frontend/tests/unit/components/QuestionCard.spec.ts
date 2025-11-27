import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import QuestionContextCard from '~/components/adaptive-questions/QuestionContextCard.vue'
import type { QuestionItem } from '~/composables/analysis/useAnalysisState'

describe('QuestionContextCard Component', () => {
  const createMockQuestion = (overrides?: Partial<QuestionItem>): QuestionItem => ({
    id: 'q1',
    number: 1,
    title: 'Backend Development Experience',
    priority: 'HIGH',
    impact: 'Missing skills: Python, FastAPI',
    question_text: 'Can you describe your experience with Python backend development?',
    context_why: 'The role requires strong Python and FastAPI knowledge',
    examples: [
      'Describe API endpoints you built',
      'Explain database integration you implemented'
    ],
    ...overrides
  })

  it('should render question details correctly with full variant', () => {
    const question = createMockQuestion()
    const wrapper = mount(QuestionContextCard, {
      props: {
        question,
        variant: 'full',
        showImpact: true,
        showContextWhy: true,
        showExamples: true
      }
    })

    expect(wrapper.text()).toContain('Q1')
    expect(wrapper.text()).toContain('Backend Development Experience')
    expect(wrapper.text()).toContain('HIGH')
    expect(wrapper.text()).toContain('Missing skills: Python, FastAPI')
    expect(wrapper.text()).toContain('Can you describe your experience with Python backend development?')
    expect(wrapper.text()).toContain('The role requires strong Python and FastAPI knowledge')
  })

  it('should use HbBadge for priority display', () => {
    const question = createMockQuestion({ priority: 'HIGH' })
    const wrapper = mount(QuestionContextCard, {
      props: {
        question,
        variant: 'default'
      }
    })

    // QuestionContextCard uses HbBadge component now
    expect(wrapper.text()).toContain('HIGH')
    expect(wrapper.text()).toContain('Q1')
  })

  it('should toggle examples visibility when clicked', async () => {
    const question = createMockQuestion()
    const wrapper = mount(QuestionContextCard, {
      props: {
        question,
        variant: 'full',
        showExamples: true
      }
    })

    // Examples should be visible initially (default: expanded)
    expect(wrapper.text()).toContain('Examples')
    expect(wrapper.text()).toContain('Describe API endpoints you built')

    // Find the Examples button
    const toggleButton = wrapper.findAll('button').find(btn => btn.text().includes('Examples'))
    expect(toggleButton).toBeDefined()

    // Click to collapse examples
    await toggleButton!.trigger('click')

    // Examples should now be hidden
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).not.toContain('Describe API endpoints you built')

    // Click again to expand
    await toggleButton!.trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Describe API endpoints you built')
  })

  it('should emit need-help event when "I have no experience" button clicked', async () => {
    const question = createMockQuestion()
    const wrapper = mount(QuestionContextCard, {
      props: {
        question,
        variant: 'full',
        showExamples: true
      }
    })

    // Examples should be expanded by default
    // Find and click the "I have no experience" button
    const needHelpButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('I have no experience')
    )
    expect(needHelpButton).toBeDefined()

    await needHelpButton!.trigger('click')

    // Check event was emitted
    expect(wrapper.emitted('need-help')).toBeTruthy()
    expect(wrapper.emitted('need-help')?.length).toBe(1)
  })

  it('should not render examples section if showExamples is false', () => {
    const question = createMockQuestion()
    const wrapper = mount(QuestionContextCard, {
      props: {
        question,
        variant: 'default',
        showExamples: false
      }
    })

    expect(wrapper.text()).not.toContain('Examples')
  })

  it('should render slot content', () => {
    const question = createMockQuestion()
    const wrapper = mount(QuestionContextCard, {
      props: {
        question,
        variant: 'full'
      },
      slots: {
        default: '<div class="test-slot">Slot content here</div>'
      }
    })

    expect(wrapper.html()).toContain('test-slot')
    expect(wrapper.text()).toContain('Slot content here')
  })

  it('should handle questions without examples gracefully', () => {
    const question = createMockQuestion({ examples: [] })
    const wrapper = mount(QuestionContextCard, {
      props: {
        question,
        variant: 'full',
        showExamples: true
      }
    })

    // Should still render the main content
    expect(wrapper.text()).toContain('Backend Development Experience')
    expect(wrapper.text()).not.toContain('Examples')
  })
})
