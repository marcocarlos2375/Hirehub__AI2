<template>
  <div class="job-parsing-result">
    <!-- Header -->
    <div class="result-header">
      <div class="header-left">
        <span class="status-badge">
          <svg class="status-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          Parsed Successfully
        </span>
        <span v-if="timeSeconds" class="time-badge">{{ timeSeconds }}s</span>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- Left Column -->
      <div class="left-column">
        <!-- Position Card -->
        <HbCard :border="false" :shadow="'none'" bg-color="transparent" padding="none">
          <div class="position-section">
            <h2 class="position-title">{{ data.position_title || 'N/A' }}</h2>
            <p class="company-name">{{ data.company_name || 'Company not specified' }}</p>

            <div class="meta-info">
              <div v-if="data.location" class="meta-item">
                <svg class="meta-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {{ data.location }}
              </div>
              <div v-if="data.work_mode" class="meta-item">
                <svg class="meta-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                {{ data.work_mode }}
              </div>
            </div>
          </div>
        </HbCard>

        <!-- Salary & Experience -->
        <HbCard :border="false" :shadow="'none'" bg-color="transparent" padding="none">
          <div class="info-section">
            <div v-if="data.salary_range" class="info-block">
              <span class="info-label">Salary</span>
              <span class="info-value accent">{{ data.salary_range }}</span>
            </div>
            <div v-if="data.experience_years_required || data.experience_level" class="info-block">
              <span class="info-label">Experience</span>
              <span class="info-value">
                <template v-if="data.experience_years_required">{{ data.experience_years_required }}+ years</template>
                <template v-if="data.experience_level"> · {{ data.experience_level }}</template>
              </span>
            </div>
          </div>
        </HbCard>

        <!-- Quick Stats -->
        <HbCard :border="false" :shadow="'none'" bg-color="transparent" padding="none">
          <div class="stats-section">
            <span class="section-label">Overview</span>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-value">{{ data.hard_skills_required?.length || 0 }}</span>
                <span class="stat-label">Skills</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ data.responsibilities?.length || 0 }}</span>
                <span class="stat-label">Tasks</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ data.tech_stack?.length || 0 }}</span>
                <span class="stat-label">Tech</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ data.soft_skills_required?.length || 0 }}</span>
                <span class="stat-label">Soft</span>
              </div>
            </div>
          </div>
        </HbCard>
      </div>

      <!-- Right Column -->
      <div class="right-column">
        <!-- Technical Skills -->
        <section v-if="data.hard_skills_required?.length" class="content-section">
          <h3 class="section-title">Technical Skills</h3>
          <div class="tags-container">
            <span
              v-for="skill in data.hard_skills_required"
              :key="skill.skill"
              class="skill-tag"
              :class="getPriorityClass(skill.priority)"
            >
              <span class="priority-dot" :class="getPriorityDotClass(skill.priority)"></span>
              {{ skill.skill }}
            </span>
          </div>
          <div class="legend">
            <span class="legend-item"><span class="dot critical"></span>Critical</span>
            <span class="legend-item"><span class="dot important"></span>Important</span>
            <span class="legend-item"><span class="dot nice"></span>Nice-to-have</span>
          </div>
        </section>

        <!-- Soft Skills -->
        <section v-if="data.soft_skills_required?.length" class="content-section">
          <h3 class="section-title">Soft Skills</h3>
          <ul class="list-simple">
            <li v-for="(skill, index) in data.soft_skills_required" :key="index">
              <svg class="check-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              {{ skill }}
            </li>
          </ul>
        </section>

        <!-- Responsibilities -->
        <section v-if="data.responsibilities?.length" class="content-section">
          <h3 class="section-title">Responsibilities</h3>
          <ol class="list-numbered">
            <li v-for="(task, index) in data.responsibilities" :key="index">
              <span class="number">{{ index + 1 }}</span>
              <span class="text">{{ task }}</span>
            </li>
          </ol>
        </section>

        <!-- Tech Stack -->
        <section v-if="data.tech_stack?.length" class="content-section">
          <h3 class="section-title">Tech Stack</h3>
          <div class="tags-container">
            <span v-for="tech in data.tech_stack" :key="tech" class="tech-tag">
              {{ tech }}
            </span>
          </div>
        </section>

        <!-- Domain Expertise -->
        <section v-if="data.domain_expertise" class="content-section">
          <h3 class="section-title">Domain</h3>
          <div class="domain-content">
            <div v-if="data.domain_expertise.industry?.length" class="domain-block">
              <span class="domain-label">Industry</span>
              <div class="tags-container">
                <span v-for="ind in data.domain_expertise.industry" :key="ind" class="domain-tag">
                  {{ ind }}
                </span>
              </div>
            </div>
            <div v-if="data.domain_expertise.specific_knowledge?.length" class="domain-block">
              <span class="domain-label">Knowledge</span>
              <ul class="list-bullet">
                <li v-for="knowledge in data.domain_expertise.specific_knowledge" :key="knowledge">
                  {{ knowledge }}
                </li>
              </ul>
            </div>
          </div>
        </section>

        <!-- Implicit Requirements -->
        <section v-if="data.implicit_requirements?.length" class="content-section">
          <h3 class="section-title">Implicit Requirements</h3>
          <div class="implicit-grid">
            <div v-for="req in data.implicit_requirements" :key="req" class="implicit-item">
              <span class="arrow">→</span>
              {{ req }}
            </div>
          </div>
        </section>

        <!-- Culture -->
        <section v-if="data.company_culture_signals?.length" class="content-section">
          <h3 class="section-title">Culture & Benefits</h3>
          <ul class="list-simple culture-list">
            <li v-for="culture in data.company_culture_signals" :key="culture">
              {{ culture }}
            </li>
          </ul>
        </section>

        <!-- ATS Keywords -->
        <section v-if="data.ats_keywords?.length" class="content-section">
          <h3 class="section-title">ATS Keywords</h3>
          <div class="tags-container">
            <span v-for="keyword in data.ats_keywords" :key="keyword" class="ats-tag">
              {{ keyword }}
            </span>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ParsedJobResult } from '~/composables/analysis/useAnalysisState'

interface Props {
  data: ParsedJobResult
  timeSeconds?: number
}

defineProps<Props>()

const getPriorityClass = (priority: string) => {
  const p = priority.toLowerCase()
  if (p === 'critical') return 'priority-critical'
  if (p === 'important') return 'priority-important'
  return 'priority-nice'
}

const getPriorityDotClass = (priority: string) => {
  const p = priority.toLowerCase()
  if (p === 'critical') return 'dot-critical'
  if (p === 'important') return 'dot-important'
  return 'dot-nice'
}
</script>

<style scoped>
.job-parsing-result {
  --accent: var(--primary-400);
  --accent-light: var(--primary-100);
  --text-primary: var(--gray-900);
  --text-secondary: var(--gray-600);
  --text-muted: var(--gray-400);
  --divider: var(--gray-200);

  /* Priority colors - traffic light style */
  --critical-bg: #fef2f2;
  --critical-text: #991b1b;
  --critical-dot: #ef4444;
  --important-bg: #fefce8;
  --important-text: #854d0e;
  --important-dot: #eab308;
  --nice-bg: #f0fdf4;
  --nice-text: #166534;
  --nice-dot: #22c55e;
}

/* Header */
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--divider);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background: var(--accent-light);
  color: var(--primary-700);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  border-radius: var(--radius-full);
}

.status-icon {
  width: 1rem;
  height: 1rem;
}

.time-badge {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

/* Grid Layout */
.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 1024px) {
  .content-grid {
    grid-template-columns: 280px 1fr;
  }
}

/* Left Column */
.left-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.position-section {
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--divider);
}

.position-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
  line-height: 1.3;
}

.company-name {
  font-size: var(--text-base);
  color: var(--accent);
  font-weight: var(--font-medium);
  margin: 0 0 1rem 0;
}

.meta-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.meta-icon {
  width: 1rem;
  height: 1rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

/* Info Section */
.info-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--divider);
}

.info-block {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: var(--text-xs);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.info-value.accent {
  color: var(--accent);
  font-weight: var(--font-medium);
}

/* Stats Section */
.stats-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-label {
  font-size: var(--text-xs);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--accent);
  line-height: 1;
}

.stat-label {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: 0.25rem;
}

/* Right Column */
.right-column {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.025em;
  margin: 0;
}

/* Tags */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.skill-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  font-size: var(--text-sm);
  border-radius: var(--radius-md);
  background: var(--gray-100);
  color: var(--text-primary);
}

.skill-tag.priority-critical {
  background: var(--critical-bg);
  color: var(--critical-text);
}

.skill-tag.priority-important {
  background: var(--important-bg);
  color: var(--important-text);
}

.skill-tag.priority-nice {
  background: var(--nice-bg);
  color: var(--nice-text);
}

.priority-dot {
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 50%;
}

.dot-critical {
  background: var(--critical-dot);
}

.dot-important {
  background: var(--important-dot);
}

.dot-nice {
  background: var(--nice-dot);
}

.tech-tag {
  padding: 0.375rem 0.75rem;
  font-size: var(--text-sm);
  background: var(--accent-light);
  color: var(--primary-700);
  border-radius: var(--radius-md);
}

.domain-tag {
  padding: 0.375rem 0.75rem;
  font-size: var(--text-sm);
  background: var(--gray-100);
  color: var(--text-secondary);
  border-radius: var(--radius-md);
}

.ats-tag {
  padding: 0.25rem 0.5rem;
  font-size: var(--text-xs);
  background: var(--gray-100);
  color: var(--text-muted);
  border-radius: var(--radius-sm);
}

/* Legend */
.legend {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.dot {
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 50%;
}

.dot.critical {
  background: var(--critical-dot);
}

.dot.important {
  background: var(--important-dot);
}

.dot.nice {
  background: var(--nice-dot);
}

/* Lists */
.list-simple {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.list-simple li {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.check-icon {
  width: 1rem;
  height: 1rem;
  color: var(--accent);
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.list-numbered {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.list-numbered li {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  background: var(--accent-light);
  color: var(--primary-700);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.text {
  flex: 1;
  line-height: 1.5;
}

.list-bullet {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.list-bullet li {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  padding-left: 1rem;
  position: relative;
}

.list-bullet li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--accent);
}

/* Domain */
.domain-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.domain-block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.domain-label {
  font-size: var(--text-xs);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Implicit Grid */
.implicit-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 0.5rem;
}

@media (min-width: 768px) {
  .implicit-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.implicit-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.arrow {
  color: var(--accent);
  flex-shrink: 0;
}

/* Culture List */
.culture-list li::before {
  content: none;
}

.culture-list li {
  padding-left: 0;
}
</style>
