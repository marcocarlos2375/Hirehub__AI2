<template>
  <div class="cv-parsing-result">
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
        <!-- Personal Info -->
        <HbCard :border="false" :shadow="'none'" bg-color="transparent" padding="none">
          <div class="personal-section">
            <h2 class="candidate-name">{{ data.personal_info?.name || 'Candidate' }}</h2>

            <div class="contact-info">
              <div v-if="data.personal_info?.email" class="contact-item">
                <svg class="contact-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                {{ data.personal_info.email }}
              </div>
              <div v-if="data.personal_info?.phone" class="contact-item">
                <svg class="contact-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                {{ data.personal_info.phone }}
              </div>
              <div v-if="data.personal_info?.location" class="contact-item">
                <svg class="contact-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {{ data.personal_info.location }}
              </div>
            </div>

            <!-- Social Links -->
            <div v-if="data.personal_info?.linkedin || data.personal_info?.github || data.personal_info?.portfolio" class="social-links">
              <a v-if="data.personal_info.linkedin" :href="data.personal_info.linkedin" target="_blank" class="social-link">
                <svg class="social-icon" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                </svg>
                LinkedIn
              </a>
              <a v-if="data.personal_info.github" :href="data.personal_info.github" target="_blank" class="social-link">
                <svg class="social-icon" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                GitHub
              </a>
              <a v-if="data.personal_info.portfolio" :href="data.personal_info.portfolio" target="_blank" class="social-link">
                <svg class="social-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                </svg>
                Portfolio
              </a>
            </div>
          </div>
        </HbCard>

        <!-- Professional Summary -->
        <HbCard v-if="data.professional_summary" :border="false" :shadow="'none'" bg-color="transparent" padding="none">
          <div class="summary-section">
            <span class="section-label">Summary</span>
            <p class="summary-text">{{ data.professional_summary }}</p>
          </div>
        </HbCard>

        <!-- Quick Stats -->
        <HbCard :border="false" :shadow="'none'" bg-color="transparent" padding="none">
          <div class="stats-section">
            <span class="section-label">Overview</span>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-value">{{ data.technical_skills?.length || 0 }}</span>
                <span class="stat-label">Skills</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ data.work_experience?.length || 0 }}</span>
                <span class="stat-label">Positions</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ data.projects?.length || 0 }}</span>
                <span class="stat-label">Projects</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ data.certifications?.length || 0 }}</span>
                <span class="stat-label">Certs</span>
              </div>
            </div>
          </div>
        </HbCard>
      </div>

      <!-- Right Column -->
      <div class="right-column">
        <!-- Technical Skills -->
        <section v-if="data.technical_skills?.length" class="content-section">
          <h3 class="section-title">Technical Skills</h3>
          <div class="tags-container">
            <span v-for="skill in data.technical_skills" :key="skill" class="skill-tag">
              {{ skill }}
            </span>
          </div>
        </section>

        <!-- Tools -->
        <section v-if="data.tools?.length" class="content-section">
          <h3 class="section-title">Tools & Technologies</h3>
          <div class="tags-container">
            <span v-for="tool in data.tools" :key="tool" class="tool-tag">
              {{ tool }}
            </span>
          </div>
        </section>

        <!-- Soft Skills -->
        <section v-if="data.soft_skills?.length" class="content-section">
          <h3 class="section-title">Soft Skills</h3>
          <div class="tags-container">
            <span v-for="skill in data.soft_skills" :key="skill" class="soft-tag">
              {{ skill }}
            </span>
          </div>
        </section>

        <!-- Work Experience -->
        <section v-if="data.work_experience?.length" class="content-section">
          <h3 class="section-title">Experience</h3>
          <div class="experience-list">
            <div v-for="(exp, index) in data.work_experience" :key="index" class="experience-item">
              <div class="experience-header">
                <div class="experience-main">
                  <h4 class="role-title">{{ exp.role }}</h4>
                  <p class="company-name">{{ exp.company }}</p>
                </div>
                <span class="duration-badge">{{ exp.duration }}</span>
              </div>
              <p class="date-range">{{ exp.start_date }} - {{ exp.end_date }}</p>
              <ul v-if="exp.achievements?.length" class="achievements-list">
                <li v-for="(achievement, aidx) in exp.achievements" :key="aidx">
                  <span class="arrow">→</span>
                  {{ achievement }}
                </li>
              </ul>
            </div>
          </div>
        </section>

        <!-- Education -->
        <section v-if="data.education?.length" class="content-section">
          <h3 class="section-title">Education</h3>
          <div class="education-list">
            <div v-for="(edu, index) in data.education" :key="index" class="education-item">
              <h4 class="degree-title">{{ edu.degree }}</h4>
              <p class="institution-name">{{ edu.institution }}</p>
              <div class="education-meta">
                <span v-if="edu.graduation_date">{{ edu.graduation_date }}</span>
                <span v-if="edu.gpa">GPA: {{ edu.gpa }}</span>
                <span v-if="edu.honors">{{ edu.honors }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Projects -->
        <section v-if="data.projects?.length" class="content-section">
          <h3 class="section-title">Projects</h3>
          <div class="projects-list">
            <div v-for="(proj, index) in data.projects" :key="index" class="project-item">
              <h4 class="project-title">{{ proj.name }}</h4>
              <p class="project-description">{{ proj.description }}</p>
              <div v-if="proj.technologies?.length" class="tags-container mini">
                <span v-for="tech in proj.technologies" :key="tech" class="tech-mini-tag">
                  {{ tech }}
                </span>
              </div>
              <a v-if="proj.link" :href="proj.link" target="_blank" class="project-link">
                View Project →
              </a>
            </div>
          </div>
        </section>

        <!-- Certifications -->
        <section v-if="data.certifications?.length" class="content-section">
          <h3 class="section-title">Certifications</h3>
          <ul class="cert-list">
            <li v-for="(cert, index) in data.certifications" :key="index">
              <svg class="cert-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              {{ cert }}
            </li>
          </ul>
        </section>

        <!-- Languages -->
        <section v-if="data.languages?.length" class="content-section">
          <h3 class="section-title">Languages</h3>
          <div class="languages-list">
            <div v-for="(lang, index) in data.languages" :key="index" class="language-item">
              <span class="language-name">{{ lang.language }}</span>
              <span class="proficiency-badge">{{ lang.proficiency }}</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ParsedCVResult } from '~/composables/analysis/useAnalysisState'

interface Props {
  data: ParsedCVResult
  timeSeconds?: number
}

defineProps<Props>()
</script>

<style scoped>
.cv-parsing-result {
  --accent: var(--primary-400);
  --accent-light: var(--primary-100);
  --text-primary: var(--gray-900);
  --text-secondary: var(--gray-600);
  --text-muted: var(--gray-400);
  --divider: var(--gray-200);
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

.personal-section {
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--divider);
}

.candidate-name {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 1rem 0;
  line-height: 1.3;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.contact-icon {
  width: 1rem;
  height: 1rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

.social-links {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.social-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--text-sm);
  color: var(--accent);
  text-decoration: none;
  transition: color 0.2s;
}

.social-link:hover {
  color: var(--primary-600);
}

.social-icon {
  width: 1rem;
  height: 1rem;
}

/* Summary Section */
.summary-section {
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--divider);
}

.section-label {
  display: block;
  font-size: var(--text-xs);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.summary-text {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

/* Stats Section */
.stats-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
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

.tags-container.mini {
  gap: 0.375rem;
  margin-bottom: 0.5rem;
}

.skill-tag {
  padding: 0.375rem 0.75rem;
  font-size: var(--text-sm);
  background: var(--accent-light);
  color: var(--primary-700);
  border-radius: var(--radius-full);
}

.tool-tag {
  padding: 0.375rem 0.75rem;
  font-size: var(--text-sm);
  background: var(--gray-100);
  color: var(--text-primary);
  border-radius: var(--radius-md);
}

.soft-tag {
  padding: 0.375rem 0.75rem;
  font-size: var(--text-sm);
  background: var(--gray-50);
  color: var(--text-secondary);
  border-radius: var(--radius-md);
}

.tech-mini-tag {
  padding: 0.25rem 0.5rem;
  font-size: var(--text-xs);
  background: var(--gray-100);
  color: var(--text-muted);
  border-radius: var(--radius-sm);
}

/* Experience */
.experience-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.experience-item {
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--gray-100);
}

.experience-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.experience-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.25rem;
}

.experience-main {
  flex: 1;
}

.role-title {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin: 0;
}

.company-name {
  font-size: var(--text-sm);
  color: var(--accent);
  margin: 0.25rem 0 0 0;
}

.duration-badge {
  font-size: var(--text-xs);
  color: var(--text-muted);
  background: var(--gray-100);
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  white-space: nowrap;
}

.date-range {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin: 0.5rem 0;
}

.achievements-list {
  list-style: none;
  padding: 0;
  margin: 0.75rem 0 0 0;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.achievements-list li {
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

/* Education */
.education-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.education-item {
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--gray-100);
}

.education-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.degree-title {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin: 0;
}

.institution-name {
  font-size: var(--text-sm);
  color: var(--accent);
  margin: 0.25rem 0 0 0;
}

.education-meta {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  font-size: var(--text-xs);
  color: var(--text-muted);
}

/* Projects */
.projects-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.project-item {
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--gray-100);
}

.project-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.project-title {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin: 0;
}

.project-description {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0.5rem 0;
  line-height: 1.5;
}

.project-link {
  font-size: var(--text-xs);
  color: var(--accent);
  text-decoration: none;
  transition: color 0.2s;
}

.project-link:hover {
  color: var(--primary-600);
}

/* Certifications */
.cert-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cert-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.cert-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--accent);
  flex-shrink: 0;
  margin-top: 0.0625rem;
}

/* Languages */
.languages-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.language-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.language-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.proficiency-badge {
  font-size: var(--text-xs);
  color: var(--text-muted);
  background: var(--gray-100);
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  text-transform: capitalize;
}
</style>
