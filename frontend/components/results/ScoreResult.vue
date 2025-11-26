<template>
  <div class="score-result">
    <div class="score-result__hero">
      <div class="score-result__hero-content">
        <div class="score-result__hero-badge">
          EVALUATION
        </div>
        <h1 class="score-result__hero-title">{{ data.score_message.title }}</h1>
        <p class="score-result__hero-subtitle">{{ data.score_message.subtitle }}</p>

        <div v-if="timeSeconds" class="score-result__meta">
          <svg class="score-result__meta-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <span>Analysis time: <strong>{{ timeSeconds }}s</strong></span>
        </div>
      </div>

      <CategoryLineGraph
        :categoryScores="data.category_scores"
        :label="`${data.overall_status} - Match`"
        :overallScore="data.overall_score"
      />
    </div>

    <section class="score-result__section">
      <h2 class="score-result__section-header">Performance Categories</h2>
      <div class="score-result__category-grid">
        <div
          v-for="(category, key) in data.category_scores"
          :key="key"
          class="score-result__stat-card"
        >
          <div class="score-result__stat-card-header">
            <h3 class="score-result__stat-name">{{ key.replace(/_/g, ' ') }}</h3>
            <span class="score-result__weight-pill">Weight: {{ Math.round(category.weight * 100) }}%</span>
          </div>

          <div class="score-result__stat-main">
            <div class="score-result__stat-value-wrapper" :class="`text-${getScoreLevel(category.score)}`">
              <span class="score-result__stat-value">{{ category.score }}</span><span class="score-result__stat-value-max">/100</span>
            </div>
            <div class="score-result__stat-status">{{ category.status }}</div>
          </div>

          <div class="score-result__stat-progress-bg">
            <div
              class="score-result__stat-progress-fill"
              :class="`bg-${getScoreLevel(category.score)}`"
              :style="{ '--target-width': category.score + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </section>

    <div class="score-result__details-grid">

      <section class="score-result__section">
        <h2 class="score-result__section-header">
          Identified Gaps
          <span class="score-result__count-badge" v-if="totalGaps > 0">{{ totalGaps }}</span>
        </h2>

        <div class="score-result__gaps-container">
          <div v-if="data.gaps.critical.length" class="score-result__gap-cluster score-result__gap-cluster--critical">
            <h4 class="score-result__cluster-title score-result__cluster-title--critical">Critical Attention Needed</h4>
            <GapCard v-for="gap in data.gaps.critical" :key="gap.id" variant="critical" :gap="gap" />
          </div>

          <div v-if="data.gaps.important.length" class="score-result__gap-cluster score-result__gap-cluster--important">
            <h4 class="score-result__cluster-title score-result__cluster-title--important">Important Factors</h4>
            <GapCard v-for="gap in data.gaps.important" :key="gap.id" variant="important" :gap="gap" />
          </div>

           <div v-if="data.gaps.nice_to_have.length || data.gaps.logistical.length" class="score-result__gap-cluster score-result__gap-cluster--minor">
            <h4 class="score-result__cluster-title score-result__cluster-title--neutral">Minor & Logistical</h4>
            <GapCard v-for="gap in data.gaps.nice_to_have" :key="gap.id" variant="nice-to-have" :gap="gap" />
            <GapCard v-for="gap in data.gaps.logistical" :key="gap.id" variant="logistical" :gap="gap" />
          </div>

          <div v-if="totalGaps === 0" class="score-result__empty-state">
            <div class="score-result__empty-icon">✨</div>
            <p>No gaps identified. Perfect match!</p>
          </div>
        </div>
      </section>

      <section class="score-result__section">
        <h2 class="score-result__section-header">Core Strengths</h2>
        <div class="score-result__strengths-list">
          <div v-for="(strength, index) in data.strengths" :key="index" class="score-result__strength-item">
            <div class="score-result__strength-icon">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
            </div>
            <div class="score-result__strength-content">
              <h3 class="score-result__strength-title">{{ strength.title }}</h3>
              <p class="score-result__strength-desc">{{ strength.description }}</p>
              <div class="score-result__evidence-box">
                <strong>Evidence:</strong> {{ strength.evidence }}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <div class="score-result__viability">
      <div class="score-result__viability-metric">
        <span class="score-result__viability-label">Viability Likelihood</span>
        <span class="score-result__viability-value" :class="getViabilityColorClass(data.application_viability.current_likelihood)">
          {{ data.application_viability.current_likelihood }}
        </span>
      </div>
      <div class="score-result__viability-divider"></div>
      <div class="score-result__viability-blockers">
        <span class="score-result__viability-label">Key Hurdles:</span>
        <div class="score-result__viability-blocker-tags">
          <span v-for="(blocker, idx) in data.application_viability.key_blockers" :key="idx" class="score-result__viability-blocker-tag">
            {{ blocker }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ScoreResponse } from '~/composables/analysis/useScoreCalculator'
import GapCard from '~/components/cards/GapCard.vue'
import CategoryLineGraph from '~/components/results/CategoryLineGraph.vue'

interface Props {
  data: ScoreResponse
  timeSeconds?: number
}

const props = defineProps<Props>()

// -- Logic Helpers --

const totalGaps = computed(() => {
  return props.data.gaps.critical.length +
         props.data.gaps.important.length +
         props.data.gaps.nice_to_have.length +
         props.data.gaps.logistical.length
})

const getScoreLevel = (score: number): string => {
  if (score >= 75) return 'high'
  if (score >= 60) return 'good'
  if (score >= 40) return 'medium'
  return 'low'
}

const getViabilityColorClass = (likelihood: string) => {
  if (likelihood.toLowerCase().includes('high')) return 'text-high'
  if (likelihood.toLowerCase().includes('medium')) return 'text-medium'
  return 'text-low'
}
</script>

<style lang="scss" scoped>
// --- Design Tokens ---
$c-bg-page: #f8fafc;
$c-surface: #ffffff;
$c-text-main: #0f172a;
$c-text-muted: #64748b;
$c-border: #e2e8f0;

// Semantic Colors
$c-success: #10b981;
$c-success-light: #ecfdf5;
$c-warning: #f59e0b;
$c-warning-light: #fffbeb;
$c-danger: #ef4444;
$c-danger-light: #fef2f2;
$c-info: #3b82f6;

$radius-lg: 1rem;
$radius-md: 0.75rem;

// --- Layout ---
.score-result {
  color: $c-text-main;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

// --- 1. Hero Section ---
.score-result__hero {
  background: $c-surface;
  border-radius: $radius-lg;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  overflow: hidden;

  @media (max-width: 768px) {
    flex-direction: column-reverse;
    text-align: center;
    gap: 1rem;
    padding: 0.75rem;
  }
}

.score-result__hero-content {
  flex: 1;
  max-width: 600px;
}

.score-result__hero-badge {
  color: var(--primary-400);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.score-result__hero-title {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: 0.5rem;
  color: $c-text-main;
}

.score-result__hero-subtitle {
  font-size: 0.95rem;
  line-height: 1.5;
  color: $c-text-muted;
  margin-bottom: 0.75rem;
}

.score-result__meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: lighten($c-text-muted, 10%);

  @media (max-width: 768px) {
    justify-content: center;
  }
}

.score-result__meta-icon {
  width: 16px;
  height: 16px;
}

// --- 2. Viability Strip ---
.score-result__viability {
  background: $c-surface;
  color: $c-text-main;
  border-radius: $radius-md;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid $c-border;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.65rem 0.85rem;
  }
}

.score-result__viability-metric {
  display: flex;
  flex-direction: column;
  min-width: 120px;
}

.score-result__viability-label {
  font-size: 0.65rem;
  text-transform: uppercase;
  color: $c-text-muted;
  margin-bottom: 0.15rem;
  letter-spacing: 0.05em;
}

.score-result__viability-value {
  font-size: 1.35rem;
  font-weight: 600;
}

.score-result__viability-divider {
  width: 1px;
  height: 30px;
  background: $c-border;

  @media (max-width: 768px) {
    width: 100%;
    height: 1px;
  }
}

.score-result__viability-blockers {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.score-result__viability-blocker-tags {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.score-result__viability-blocker-tag {
  background: $c-bg-page;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
  color: $c-text-main;
}

// --- 3. Categories ---
.score-result__section {
  // Shared section styles
}

.score-result__section-header {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.score-result__category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.75rem;
}

.score-result__stat-card {
  background: $c-surface;
  padding: 1rem;
  border-radius: $radius-md;
}

.score-result__stat-card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.score-result__stat-name {
  font-size: 0.7rem;
  font-weight: 600;
  color: $c-text-muted;
  text-transform: uppercase;
  letter-spacing: 0.005em;
}

.score-result__weight-pill {
  font-size: 0.7rem;
  background: $c-bg-page;
  padding: 2px 8px;
  border-radius: 4px;
  color: $c-text-muted;
  height: fit-content;
}

.score-result__stat-main {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.score-result__stat-value-wrapper {
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1;
}

.score-result__stat-value {
  color: currentColor;
}

.score-result__stat-value-max {
  font-size: 0.3em;
  color: currentColor;
  opacity: 0.7;
}

.score-result__stat-status {
  font-size: 0.85rem;
  font-weight: 500;
  color: $c-text-muted;
}

.score-result__stat-progress-bg {
  height: 4px;
  background: $c-bg-page;
  overflow: hidden;
}

.score-result__stat-progress-fill {
  height: 100%;
  width: 0;
  animation: fillProgress 1.5s ease-out forwards;
  position: relative;
  overflow: hidden;

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg,
      rgba(255, 255, 255, 0) 0%,
      rgba(255, 255, 255, 0.3) 50%,
      rgba(255, 255, 255, 0) 100%
    );
  }
}

@keyframes fillProgress {
  from {
    width: 0;
  }
  to {
    width: var(--target-width);
  }
}

// Colors for Stats
.text-high {
  color: var(--secondary-500);
}
.bg-high {
  background-color: var(--secondary-500);
}
.text-good {
  color: var(--secondary-500);
}
.bg-good {
  background-color: var(--secondary-500);
}
.text-medium {
  color: $c-warning;
}
.bg-medium {
  background-color: $c-warning;
}
.text-low {
  color: $c-danger;
}
.bg-low {
  background-color: $c-danger;
}

// --- 4. Split Grid (Gaps/Strengths) ---
.score-result__details-grid {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.score-result__count-badge {
  background: $c-danger-light;
  color: $c-danger;
  font-size: 0.75rem;
  padding: 0.1rem 0.5rem;
  border-radius: 1rem;
}

.score-result__gaps-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.score-result__gap-cluster {
  :deep(.gap-card) {
    margin-bottom: 8px;

    &:last-child {
      margin-bottom: 0;
    }
  }
}

.score-result__gap-cluster--critical {
  color: $c-danger;
}

.score-result__gap-cluster--important {
  color: $c-warning;
}

.score-result__gap-cluster--minor {
  color: $c-text-muted;
}

.score-result__cluster-title {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.score-result__cluster-title--critical {
  color: $c-danger;
}

.score-result__cluster-title--important {
  color: darken($c-warning, 10%);
}

.score-result__cluster-title--neutral {
  color: $c-text-muted;
}

.score-result__empty-state {
  text-align: center;
  padding: 3rem;
  background: $c-surface;
  border-radius: $radius-md;
  border: 2px dashed $c-border;
  color: $c-text-muted;
}

.score-result__empty-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

// Strengths
.score-result__strengths-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.score-result__strength-item {
  background: $c-surface;
  padding: 1.25rem;
  border-radius: $radius-md;
  border: 1px solid $c-border;
  display: flex;
  gap: 1rem;
}

.score-result__strength-icon {
  width: 2rem;
  height: 2rem;
  background: $c-success-light;
  color: darken($c-success, 10%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.score-result__strength-content {
  flex: 1;
}

.score-result__strength-title {
  font-weight: 700;
  color: $c-text-main;
  margin-bottom: 0.25rem;
}

.score-result__strength-desc {
  font-size: 0.9rem;
  color: $c-text-muted;
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

.score-result__evidence-box {
  background: $c-bg-page;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  color: darken($c-text-muted, 10%);
}
</style>