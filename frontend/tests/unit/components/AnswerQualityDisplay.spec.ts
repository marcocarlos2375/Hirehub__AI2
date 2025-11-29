import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import AnswerQualityDisplay from '~/components/adaptive-questions/cards/AnswerQualityDisplay.vue'

describe('AnswerQualityDisplay Component', () => {
  const createWrapper = (props: any) => {
    return mount(AnswerQualityDisplay, { props })
  }

  it('should render quality score correctly', () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 8,
      isAcceptable: true
    })

    expect(wrapper.text()).toContain('8')
    expect(wrapper.text()).toContain('/ 10')
  })

  it('should display "Excellent Quality!" for score >= 9', () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 9,
      isAcceptable: true
    })

    expect(wrapper.text()).toContain('Excellent Quality!')
  })

  it('should display "Good Quality" for score between 7-8', () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 7,
      isAcceptable: true
    })

    expect(wrapper.text()).toContain('Good Quality')
  })

  it('should display "Needs Improvement" for score between 5-6', () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 5,
      isAcceptable: false
    })

    expect(wrapper.text()).toContain('Needs Improvement')
  })

  it('should display "Requires Refinement" for score < 5', () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 4,
      isAcceptable: false
    })

    expect(wrapper.text()).toContain('Requires Refinement')
  })

  it('should apply correct background class for high scores', () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 9,
      isAcceptable: true
    })

    const scoreCircle = wrapper.find('.w-24.h-24')
    expect(scoreCircle.classes()).toContain('bg-green-100')
  })

  it('should apply correct text class for medium scores', () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 7,
      isAcceptable: true
    })

    const scoreText = wrapper.find('.text-3xl')
    expect(scoreText.classes()).toContain('text-blue-700')
  })

  it('should display quality strengths when provided', () => {
    const strengths = ['Clear examples', 'Specific metrics', 'Professional tone']
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 8,
      qualityStrengths: strengths,
      isAcceptable: true
    })

    expect(wrapper.text()).toContain('Strengths')
    strengths.forEach(strength => {
      expect(wrapper.text()).toContain(strength)
    })
  })

  it('should display quality issues when provided', () => {
    const issues = ['Missing metrics', 'Too vague', 'No specific examples']
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 5,
      qualityIssues: issues,
      isAcceptable: false
    })

    expect(wrapper.text()).toContain('Issues Found')
    issues.forEach(issue => {
      expect(wrapper.text()).toContain(issue)
    })
  })

  it('should emit accept-answer event when accept button clicked', async () => {
    const generatedAnswer = 'My generated answer'
    const wrapper = createWrapper({
      generatedAnswer,
      qualityScore: 8,
      isAcceptable: true
    })

    const acceptButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Accept Answer')
    )
    await acceptButton!.trigger('click')

    expect(wrapper.emitted('accept-answer')).toBeTruthy()
    expect(wrapper.emitted('accept-answer')?.[0]).toEqual([generatedAnswer])
  })

  it('should show "Refine Answer" button when quality is not acceptable', () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 5,
      isAcceptable: false,
      showRefineButton: true
    })

    expect(wrapper.text()).toContain('Refine Answer')
  })

  it('should not show "Refine Answer" button when quality is acceptable', () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 8,
      isAcceptable: true,
      showRefineButton: true
    })

    expect(wrapper.text()).not.toContain('Refine Answer')
  })

  it('should emit refine-answer event when refine button clicked', async () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 5,
      isAcceptable: false,
      showRefineButton: true
    })

    const refineButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Refine Answer')
    )
    await refineButton!.trigger('click')

    expect(wrapper.emitted('refine-answer')).toBeTruthy()
  })

  it('should show "Accept Anyway" when quality is not acceptable', () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 5,
      isAcceptable: false
    })

    expect(wrapper.text()).toContain('Accept Anyway')
  })

  it('should apply green styling to accept button when acceptable', () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 8,
      isAcceptable: true
    })

    const acceptButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Accept Answer')
    )
    expect(acceptButton!.classes()).toContain('bg-green-600')
  })

  it('should apply indigo styling to accept button when not acceptable', () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 5,
      isAcceptable: false
    })

    const acceptButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Accept Anyway')
    )
    expect(acceptButton!.classes()).toContain('bg-indigo-600')
  })

  it('should not render strengths section when empty', () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 5,
      qualityStrengths: [],
      isAcceptable: false
    })

    expect(wrapper.text()).not.toContain('Strengths')
  })

  it('should not render issues section when empty', () => {
    const wrapper = createWrapper({
      generatedAnswer: 'Test answer',
      qualityScore: 8,
      qualityIssues: [],
      isAcceptable: true
    })

    expect(wrapper.text()).not.toContain('Issues Found')
  })
})
