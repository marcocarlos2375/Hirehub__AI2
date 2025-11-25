<template>
  <div class="dashboard-container">
    <div class="dashboard-hero">
      <div class="hero-content">
        <div class="hero-badge" :class="`status-${getStatusLevel(data.overall_score)}`">
          Evaluation
        </div>
        <h1 class="hero-title">{{ data.score_message.title }}</h1>
        <p class="hero-subtitle">{{ data.score_message.subtitle }}</p>
        
        <div v-if="timeSeconds" class="analysis-meta">
          <svg class="meta-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <span>Analysis time: <strong>{{ timeSeconds }}s</strong></span>
        </div>
      </div>

      <div class="score-dial">
        <div class="dial-ring" :style="getRingStyle(data.overall_score)">
          <div class="dial-inner">
            <span class="score-number"> {{ data.overall_status }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="viability-strip">
      <div class="viability-metric">
        <span class="label">Viability Likelihood</span>
        <span class="value" :class="getViabilityColorClass(data.application_viability.current_likelihood)">
          {{ data.application_viability.current_likelihood }}
        </span>
      </div>
      <div class="viability-divider"></div>
      <div class="viability-blockers">
        <span class="label">Key Hurdles:</span>
        <div class="blocker-tags">
          <span v-for="(blocker, idx) in data.application_viability.key_blockers" :key="idx" class="blocker-tag">
            {{ blocker }}
          </span>
        </div>
      </div>
    </div>

    <section class="dashboard-section">
      <h2 class="section-header">Performance Categories</h2>
      <div class="category-grid">
        <div 
          v-for="(category, key) in data.category_scores" 
          :key="key"
          class="stat-card"
        >
          <div class="stat-card-header">
            <h3 class="stat-name">{{ key.replace(/_/g, ' ') }}</h3>
            <span class="weight-pill">Weight: {{ Math.round(category.weight * 100) }}%</span>
          </div>
          
          <div class="stat-main">
            <div class="stat-value" :class="`text-${getScoreLevel(category.score)}`">
              {{ category.score }}
            </div>
            <div class="stat-status">{{ category.status }}</div>
          </div>

          <div class="stat-progress-bg">
            <div 
              class="stat-progress-fill" 
              :class="`bg-${getScoreLevel(category.score)}`"
              :style="{ width: category.score + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </section>

    <div class="details-grid">
      
      <section class="dashboard-section">
        <h2 class="section-header">
          Identified Gaps
          <span class="count-badge" v-if="totalGaps > 0">{{ totalGaps }}</span>
        </h2>
        
        <div class="gaps-container">
          <div v-if="data.gaps.critical.length" class="gap-cluster cluster-critical">
            <h4 class="cluster-title text-critical">Critical Attention Needed</h4>
            <GapCard v-for="gap in data.gaps.critical" :key="gap.id" variant="critical" :gap="gap" />
          </div>

          <div v-if="data.gaps.important.length" class="gap-cluster cluster-important">
            <h4 class="cluster-title text-important">Important Factors</h4>
            <GapCard v-for="gap in data.gaps.important" :key="gap.id" variant="important" :gap="gap" />
          </div>

           <div v-if="data.gaps.nice_to_have.length || data.gaps.logistical.length" class="gap-cluster cluster-minor">
            <h4 class="cluster-title text-neutral">Minor & Logistical</h4>
            <GapCard v-for="gap in data.gaps.nice_to_have" :key="gap.id" variant="nice-to-have" :gap="gap" />
            <GapCard v-for="gap in data.gaps.logistical" :key="gap.id" variant="logistical" :gap="gap" />
          </div>

          <div v-if="totalGaps === 0" class="empty-state">
            <div class="empty-icon">✨</div>
            <p>No gaps identified. Perfect match!</p>
          </div>
        </div>
      </section>

      <section class="dashboard-section">
        <h2 class="section-header">Core Strengths</h2>
        <div class="strengths-list">
          <div v-for="(strength, index) in data.strengths" :key="index" class="strength-item">
            <div class="strength-icon-box">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
            </div>
            <div class="strength-content">
              <h3 class="strength-title">{{ strength.title }}</h3>
              <p class="strength-desc">{{ strength.description }}</p>
              <div class="evidence-box">
                <strong>Evidence:</strong> {{ strength.evidence }}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ScoreResponse } from '~/composables/analysis/useScoreCalculator'
import GapCard from '~/components/cards/GapCard.vue'

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

// Returns a Conic Gradient string for the ring chart
const getRingStyle = (score: number) => {
  const color = score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444'
  const percent = score * 3.6 // 360 degrees
  return {
    background: `conic-gradient(${color} ${percent}deg, #e5e7eb 0deg)`
  }
}

const getStatusLevel = (score: number): string => {
  if (score >= 75) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'moderate'
  return 'low'
}

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
.dashboard-container {
  color: $c-text-main;
 
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

// --- 1. Hero Section ---
.dashboard-hero {
  background: $c-surface;
  border-radius: $radius-lg;
  padding: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
  
 
  @media (max-width: 768px) {
    flex-direction: column-reverse;
    text-align: center;
    gap: 2rem;
  }
}

.hero-content {
  flex: 1;
  max-width: 600px;
}

.hero-badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 2rem;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
  
}

.hero-title {
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 0.75rem;
  color: $c-text-main;
}

.hero-subtitle {
  font-size: 1.1rem;
  line-height: 1.6;
  color: $c-text-muted;
  margin-bottom: 1.5rem;
}

.analysis-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: lighten($c-text-muted, 10%);
  
  .meta-icon { width: 16px; height: 16px; }
  
  @media (max-width: 768px) {
    justify-content: center;
  }
}

// --- Ring Chart ---
.score-dial {
  position: relative;
  width: 160px;
  height: 160px;
  flex-shrink: 0;
  margin-left: 2rem;
  
  @media (max-width: 768px) {
    margin-left: 0;
  }
}

.dial-ring {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  // Background set via JS inline style
  position: relative;
  
  &::before {
    content: ''; // Inner shadow helper
    position: absolute;
    inset: 0;
    border-radius: 50%;
  }
}

.dial-inner {
  width: 80%; // Thickness of ring
  height: 80%;
  background: $c-surface;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.score-number {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1;
  color: $c-text-main;
}

.score-label {
  font-size: 0.875rem;
  color: $c-text-muted;
  font-weight: 500;
}

// --- 2. Viability Strip ---
.viability-strip {
  background: $c-text-main; // Dark theme for contrast
  color: white;
  border-radius: $radius-md;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 2rem;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}

.viability-metric {
  display: flex;
  flex-direction: column;
  min-width: 140px;
  
  .label { font-size: 0.75rem; text-transform: uppercase; opacity: 0.7; margin-bottom: 0.25rem; letter-spacing: 0.05em; }
  .value { font-size: 1.5rem; font-weight: 700; }
  
  .text-high { color: $c-success; }
  .text-medium { color: $c-warning; }
  .text-low { color: $c-danger; }
}

.viability-divider {
  width: 1px;
  height: 40px;
  background: rgba(255,255,255,0.2);
  
  @media (max-width: 768px) {
    width: 100%; height: 1px;
  }
}

.viability-blockers {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;

  .label { font-weight: 600; font-size: 0.9rem; white-space: nowrap; }
}

.blocker-tag {
  background: rgba(255,255,255,0.15);
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

// --- 3. Categories ---
.section-header {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: $c-surface;
  padding: 1.5rem;
  border-radius: $radius-md;
  border: 1px solid $c-border;
  
  &:hover {
    transform: translateY(-2px);
  }
}

.stat-card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  
  .stat-name { font-size: 0.9rem; font-weight: 600; color: $c-text-muted; text-transform: capitalize; }
  .weight-pill { font-size: 0.7rem; background: $c-bg-page; padding: 2px 8px; border-radius: 10px; color: $c-text-muted; height: fit-content; }
}

.stat-main {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1;
}

.stat-status {
  font-size: 0.85rem;
  font-weight: 500;
  color: $c-text-muted;
}

.stat-progress-bg {
  height: 8px;
  background: $c-bg-page;
  border-radius: 4px;
  overflow: hidden;
}

.stat-progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 1s ease-out;
}

// Colors for Stats
.text-high { color: $c-success; }
.bg-high { background-color: $c-success; }
.text-good { color: darken($c-success, 10%); }
.bg-good { background-color: darken($c-success, 10%); }
.text-medium { color: $c-warning; }
.bg-medium { background-color: $c-warning; }
.text-low { color: $c-danger; }
.bg-low { background-color: $c-danger; }

// --- 4. Split Grid (Gaps/Strengths) ---
.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  
  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
}

.count-badge {
  background: $c-danger-light;
  color: $c-danger;
  font-size: 0.75rem;
  padding: 0.1rem 0.5rem;
  border-radius: 1rem;
}

.gaps-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.gap-cluster {
  .cluster-title {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.75rem;
    padding-left: 0.5rem;
    border-left: 3px solid currentColor;
  }
  
  &.cluster-critical { color: $c-danger; }
  &.cluster-important { color: $c-warning; }
  &.cluster-minor { color: $c-text-muted; }
  
  .text-critical { color: $c-danger; }
  .text-important { color: darken($c-warning, 10%); }
  .text-neutral { color: $c-text-muted; }
}

.empty-state {
  text-align: center;
  padding: 3rem;
  background: $c-surface;
  border-radius: $radius-md;
  border: 2px dashed $c-border;
  color: $c-text-muted;
  
  .empty-icon { font-size: 2rem; margin-bottom: 0.5rem; }
}

// Strengths
.strengths-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.strength-item {
  background: $c-surface;
  padding: 1.25rem;
  border-radius: $radius-md;
  border: 1px solid $c-border;
  display: flex;
  gap: 1rem;
  
  .strength-icon-box {
    width: 2rem; height: 2rem;
    background: $c-success-light;
    color: darken($c-success, 10%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
}

.strength-content {
  flex: 1;
  
  .strength-title { font-weight: 700; color: $c-text-main; margin-bottom: 0.25rem; }
  .strength-desc { font-size: 0.9rem; color: $c-text-muted; margin-bottom: 0.75rem; line-height: 1.5; }
}

.evidence-box {
  background: $c-bg-page;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  color: darken($c-text-muted, 10%);
  border-left: 3px solid $c-success;
}
</style>