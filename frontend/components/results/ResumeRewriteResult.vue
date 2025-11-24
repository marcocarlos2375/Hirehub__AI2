<template>
  <div class="resume-rewrite-result">
    <div class="header">
      <h2 class="title">✨ Resume Rewritten Successfully</h2>
      <p class="subtitle">Your resume has been enhanced with insights from your answers</p>
      <p class="time-badge">Completed in {{ timeSeconds }}s</p>
    </div>

    <!-- Enhancements Summary -->
    <div v-if="enhancementsMade && enhancementsMade.length > 0" class="enhancements-summary">
      <h3>📝 Enhancements Made:</h3>
      <ul>
        <li v-for="(enhancement, index) in enhancementsMade" :key="index">
          {{ enhancement }}
        </li>
      </ul>
    </div>

    <!-- Tabbed Interface -->
    <div class="tabs-container">
      <div class="tabs-header">
        <button
          class="tab-button"
          :class="{ active: activeTab === 'edit' }"
          @click="activeTab = 'edit'"
        >
          ✏️ Edit Resume
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'preview' }"
          @click="activeTab = 'preview'"
        >
          📄 Preview
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'sample' }"
          @click="activeTab = 'sample'"
        >
          💻 Sample JSON
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'parsed' }"
          @click="activeTab = 'parsed'"
        >
          📋 Parsed JSON
        </button>
      </div>

      <div class="tabs-content">
        <!-- Edit Resume Tab -->
        <div v-if="activeTab === 'edit'" class="tab-pane">
          <!-- Edit Controls -->
          <div v-if="hasChanges" class="edit-controls">
            <p class="changes-indicator">✏️ You have unsaved changes</p>
            <div class="control-buttons">
              <button class="save-button" @click="saveEditedResume">
                💾 Save Edited Resume
              </button>
              <button class="reset-button" @click="resetChanges">
                ↺ Reset Changes
              </button>
            </div>
          </div>

          <div class="edit-sections">
            <!-- Professional Summary -->
            <div v-if="content.professionalSummary" class="edit-section">
              <h3 class="edit-section-title">Professional Summary</h3>
              <div class="edit-field">
                <label class="edit-label">Summary Text</label>
                <textarea
                  v-model="editableContent.content.professionalSummary"
                  @input="hasChanges = true"
                  class="edit-input-textarea"
                  rows="4"
                  placeholder="Write your professional summary..."
                ></textarea>
              </div>
            </div>

            <!-- Work Experience -->
            <div v-if="content.employmentHistory && content.employmentHistory.length > 0" class="edit-section">
              <h3 class="edit-section-title">Work Experience</h3>
              <div v-for="(job, index) in content.employmentHistory" :key="index" class="edit-item">
                <div class="edit-item-header">
                  <h4 class="edit-item-title">{{ job.jobTitle }} at {{ job.company }}</h4>
                  <span class="edit-item-dates">{{ job.startDate }} - {{ job.endDate || 'Present' }}</span>
                </div>
                <div class="edit-field">
                  <label class="edit-label">Description (supports HTML)</label>
                  <textarea
                    v-model="editableContent.content.employmentHistory[index].description"
                    @input="hasChanges = true"
                    class="edit-input-textarea"
                    rows="6"
                    placeholder="Describe your responsibilities and achievements..."
                  ></textarea>
                  <p class="edit-hint">💡 This description has been enhanced with ATS keywords. Feel free to adjust the wording.</p>
                </div>
              </div>
            </div>

            <!-- Projects -->
            <div v-if="content.projects && content.projects.length > 0" class="edit-section">
              <h3 class="edit-section-title">Projects</h3>
              <div v-for="(project, index) in content.projects" :key="index" class="edit-item">
                <div class="edit-item-header">
                  <h4 class="edit-item-title">{{ project.title }}</h4>
                </div>

                <div class="edit-field">
                  <label class="edit-label">Description</label>
                  <textarea
                    v-model="editableContent.content.projects[index].description"
                    @input="hasChanges = true"
                    class="edit-input-textarea"
                    rows="4"
                    placeholder="Describe the project..."
                  ></textarea>
                </div>

                <!-- Technologies -->
                <div v-if="project.technologies && project.technologies.length > 0" class="edit-field">
                  <label class="edit-label">Technologies</label>
                  <div class="tech-tags-edit">
                    <span v-for="(tech, techIndex) in project.technologies" :key="techIndex" class="tech-tag-edit">
                      {{ tech }}
                      <button
                        class="tech-remove-btn"
                        @click="removeProjectTech(index, techIndex)"
                        title="Remove technology"
                      >
                        ✕
                      </button>
                    </span>
                  </div>
                </div>

                <!-- Achievements with Suggestions -->
                <div v-if="project.achievements && project.achievements.length > 0" class="edit-field">
                  <label class="edit-label">Achievements</label>
                  <div class="achievements-edit">
                    <div v-for="(achievement, achIndex) in project.achievements" :key="achIndex" class="achievement-edit-item">
                      <span v-if="isSuggested(achievement)" class="suggested-achievement-edit">
                        <span class="suggestion-badge-edit">SUGGESTED</span>
                        <span class="achievement-text-edit">{{ removeSuggestedPrefix(achievement) }}</span>
                        <div class="suggestion-actions-edit">
                          <button
                            class="accept-btn-edit"
                            @click="acceptSuggestion('projects', index, achIndex)"
                            title="Accept this suggestion"
                          >
                            ✓ Accept
                          </button>
                          <button
                            class="reject-btn-edit"
                            @click="rejectSuggestion('projects', index, achIndex)"
                            title="Remove this suggestion"
                          >
                            ✕ Remove
                          </button>
                        </div>
                      </span>
                      <span v-else class="accepted-achievement-edit">
                        <span class="achievement-check">✓</span>
                        <input
                          v-model="editableContent.content.projects[index].achievements[achIndex]"
                          @input="hasChanges = true"
                          class="achievement-input-edit"
                          type="text"
                        />
                        <button
                          class="achievement-remove-btn"
                          @click="removeProjectAchievement(index, achIndex)"
                          title="Remove achievement"
                        >
                          ✕
                        </button>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Skills -->
            <div v-if="content.skills && content.skills.length > 0" class="edit-section">
              <h3 class="edit-section-title">Skills</h3>
              <div class="edit-field">
                <label class="edit-label">Your Skills</label>
                <div class="skills-edit">
                  <span v-for="(skill, index) in content.skills" :key="index" class="skill-tag-edit">
                    {{ skill.skill }}
                    <button
                      class="skill-remove-btn"
                      @click="removeSkill(index)"
                      title="Remove skill"
                    >
                      ✕
                    </button>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Preview Tab -->
        <div v-if="activeTab === 'preview'" class="tab-pane">
          <!-- Edit Controls -->
          <div v-if="hasChanges" class="edit-controls">
            <p class="changes-indicator">✏️ You have unsaved changes</p>
            <div class="control-buttons">
              <button class="save-button" @click="saveEditedResume">
                💾 Save Edited Resume
              </button>
              <button class="reset-button" @click="resetChanges">
                ↺ Reset Changes
              </button>
            </div>
          </div>

          <div class="resume-preview">
            <div class="resume-container">
              <!-- Header -->
              <div class="resume-header">
                <h1 class="resume-name">
                  {{ content.personalInfo?.firstName }} {{ content.personalInfo?.lastName }}
                </h1>
                <p v-if="content.personalInfo?.jobTitle" class="resume-job-title">
                  {{ content.personalInfo.jobTitle }}
                </p>
                <div class="resume-contact">
                  <span v-if="content.personalInfo?.email">📧 {{ content.personalInfo.email }}</span>
                  <span v-if="content.personalInfo?.phone">📱 {{ content.personalInfo.phone }}</span>
                  <span v-if="content.personalInfo?.location">📍 {{ content.personalInfo.location }}</span>
                </div>
                <div v-if="content.personalInfo?.socialLinks" class="resume-social">
                  <a v-if="content.personalInfo.socialLinks.linkedin" :href="content.personalInfo.socialLinks.linkedin" target="_blank" class="social-link">
                    🔗 LinkedIn
                  </a>
                  <a v-if="content.personalInfo.socialLinks.github" :href="content.personalInfo.socialLinks.github" target="_blank" class="social-link">
                    💻 GitHub
                  </a>
                  <a v-if="content.personalInfo.socialLinks.portfolio" :href="content.personalInfo.socialLinks.portfolio" target="_blank" class="social-link">
                    🌐 Portfolio
                  </a>
                </div>
              </div>

              <!-- Professional Summary -->
              <div v-if="content.professionalSummary" class="resume-section">
                <h2 class="section-title">Professional Summary</h2>
                <div class="section-content" v-html="content.professionalSummary"></div>
              </div>

              <!-- Work Experience -->
              <div v-if="content.employmentHistory && content.employmentHistory.length > 0" class="resume-section">
                <h2 class="section-title">Work Experience</h2>
                <div v-for="(job, index) in content.employmentHistory" :key="index" class="experience-item">
                  <div class="experience-header">
                    <div>
                      <h3 class="experience-title">{{ job.jobTitle }}</h3>
                      <p class="experience-company">{{ job.company }} • {{ job.location }}</p>
                    </div>
                    <div class="experience-dates">
                      {{ job.startDate }} - {{ job.endDate || 'Present' }}
                    </div>
                  </div>

                  <!-- Editable Description -->
                  <div class="editable-field-container">
                    <div
                      v-if="editingField !== `employmentHistory-${index}-description`"
                      class="experience-description editable-field"
                      v-html="job.description"
                      @click="startEditing(`employmentHistory-${index}-description`, job.description)"
                      title="Click to edit"
                    ></div>
                    <div v-else class="editing-container">
                      <textarea
                        v-model="editingValue"
                        @keydown.enter.meta="saveField('employmentHistory', index, 'description')"
                        @keydown.esc="cancelEditing"
                        class="edit-textarea"
                        rows="5"
                      ></textarea>
                      <div class="edit-actions">
                        <button
                          class="save-edit-btn"
                          @click="saveField('employmentHistory', index, 'description')"
                        >
                          ✓ Save
                        </button>
                        <button class="cancel-edit-btn" @click="cancelEditing">
                          ✕ Cancel
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Projects -->
              <div v-if="content.projects && content.projects.length > 0" class="resume-section">
                <h2 class="section-title">Projects</h2>
                <div v-for="(project, index) in content.projects" :key="index" class="project-item">
                  <h3 class="project-title">{{ project.title }}</h3>

                  <!-- Editable Project Description -->
                  <div class="editable-field-container">
                    <div
                      v-if="editingField !== `projects-${index}-description`"
                      class="project-description editable-field"
                      v-html="project.description"
                      @click="startEditing(`projects-${index}-description`, project.description)"
                      title="Click to edit"
                    ></div>
                    <div v-else class="editing-container">
                      <textarea
                        v-model="editingValue"
                        @keydown.enter.meta="saveField('projects', index, 'description')"
                        @keydown.esc="cancelEditing"
                        class="edit-textarea"
                        rows="4"
                      ></textarea>
                      <div class="edit-actions">
                        <button
                          class="save-edit-btn"
                          @click="saveField('projects', index, 'description')"
                        >
                          ✓ Save
                        </button>
                        <button class="cancel-edit-btn" @click="cancelEditing">
                          ✕ Cancel
                        </button>
                      </div>
                    </div>
                  </div>

                  <div v-if="project.technologies && project.technologies.length > 0" class="project-technologies">
                    <span v-for="(tech, techIndex) in project.technologies" :key="techIndex" class="tech-badge">
                      {{ tech }}
                    </span>
                  </div>

                  <!-- Achievements with Accept/Reject for [SUGGESTED] items -->
                  <div v-if="project.achievements && project.achievements.length > 0" class="project-achievements">
                    <div v-for="(achievement, achIndex) in project.achievements" :key="achIndex" class="achievement-item">
                      <span v-if="isSuggested(achievement)" class="suggested-achievement">
                        <span class="suggestion-badge">SUGGESTED</span>
                        <span class="achievement-text">{{ removeSuggestedPrefix(achievement) }}</span>
                        <div class="suggestion-actions">
                          <button
                            class="accept-btn"
                            @click="acceptSuggestion('projects', index, achIndex)"
                            title="Accept suggestion"
                          >
                            ✓
                          </button>
                          <button
                            class="reject-btn"
                            @click="rejectSuggestion('projects', index, achIndex)"
                            title="Reject suggestion"
                          >
                            ✕
                          </button>
                        </div>
                      </span>
                      <span v-else>
                        ✓ {{ achievement }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Skills -->
              <div v-if="content.skills && content.skills.length > 0" class="resume-section">
                <h2 class="section-title">Skills</h2>
                <div class="skills-container">
                  <span v-for="(skill, index) in content.skills" :key="index" class="skill-badge">
                    {{ skill.skill }}
                  </span>
                </div>
              </div>

              <!-- Education -->
              <div v-if="content.education && content.education.length > 0" class="resume-section">
                <h2 class="section-title">Education</h2>
                <div v-for="(edu, index) in content.education" :key="index" class="education-item">
                  <div class="education-header">
                    <div>
                      <h3 class="education-degree">{{ edu.degree }}</h3>
                      <p class="education-institution">{{ edu.institution }}</p>
                    </div>
                    <div class="education-date">{{ edu.graduationDate }}</div>
                  </div>
                  <p v-if="edu.gpa" class="education-gpa">GPA: {{ edu.gpa }}</p>
                </div>
              </div>

              <!-- Certifications -->
              <div v-if="content.certifications && content.certifications.length > 0" class="resume-section">
                <h2 class="section-title">Certifications</h2>
                <div v-for="(cert, index) in content.certifications" :key="index" class="certification-item">
                  <h3 class="certification-title">{{ cert.title }}</h3>
                  <p class="certification-issuer">{{ cert.issuer }} • {{ cert.date }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sample Format Tab -->
        <div v-if="activeTab === 'sample'" class="tab-pane">
          <div class="tab-pane-header">
            <h4>Frontend-Ready Format (camelCase, HTML descriptions)</h4>
            <button class="copy-button" @click="copyToClipboard(sampleFormat, 'sample')">
              {{ copiedTab === 'sample' ? '✓ Copied!' : '📋 Copy JSON' }}
            </button>
          </div>
          <pre class="json-viewer"><code>{{ JSON.stringify(sampleFormat, null, 2) }}</code></pre>
        </div>

        <!-- Parsed Format Tab -->
        <div v-if="activeTab === 'parsed'" class="tab-pane">
          <div class="tab-pane-header">
            <h4>Backend-Compatible Format (snake_case, plain text)</h4>
            <button class="copy-button" @click="copyToClipboard(parsedFormat, 'parsed')">
              {{ copiedTab === 'parsed' ? '✓ Copied!' : '📋 Copy JSON' }}
            </button>
          </div>
          <pre class="json-viewer"><code>{{ JSON.stringify(parsedFormat, null, 2) }}</code></pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  sampleFormat: Record<string, any>
  parsedFormat: Record<string, any>
  enhancementsMade: string[]
  timeSeconds: number
}

const props = defineProps<Props>()

const activeTab = ref<'edit' | 'preview' | 'sample' | 'parsed'>('edit')
const copiedTab = ref<string | null>(null)

// Editable content state
const editableContent = ref<any>(null)
const hasChanges = ref(false)
const editingField = ref<string | null>(null)
const editingValue = ref<string>('')

// Initialize editable content from props
watch(() => props.sampleFormat, (newVal) => {
  if (newVal && !editableContent.value) {
    editableContent.value = JSON.parse(JSON.stringify(newVal))
  }
}, { immediate: true })

const content = computed(() => editableContent.value?.content || {})

// Detect if a string contains [SUGGESTED] marker
const isSuggested = (text: string): boolean => {
  return typeof text === 'string' && text.includes('[SUGGESTED]')
}

// Remove [SUGGESTED] prefix from text
const removeSuggestedPrefix = (text: string): string => {
  return text.replace(/\[SUGGESTED\]\s*/g, '')
}

// Accept a suggestion (remove [SUGGESTED] prefix)
const acceptSuggestion = (section: 'projects' | 'employmentHistory', index: number, achievementIndex?: number) => {
  if (section === 'projects' && achievementIndex !== undefined) {
    const achievement = editableContent.value.content.projects[index].achievements[achievementIndex]
    editableContent.value.content.projects[index].achievements[achievementIndex] = removeSuggestedPrefix(achievement)
  } else if (section === 'employmentHistory' && achievementIndex !== undefined) {
    // For future use if work experience has achievements array
  }
  hasChanges.value = true
}

// Reject a suggestion (remove entire item)
const rejectSuggestion = (section: 'projects' | 'employmentHistory', index: number, achievementIndex?: number) => {
  if (section === 'projects' && achievementIndex !== undefined) {
    editableContent.value.content.projects[index].achievements.splice(achievementIndex, 1)
  } else if (section === 'employmentHistory' && achievementIndex !== undefined) {
    // For future use
  }
  hasChanges.value = true
}

// Start editing a field
const startEditing = (fieldPath: string, currentValue: string) => {
  editingField.value = fieldPath
  editingValue.value = currentValue
}

// Save edited field
const saveField = (section: string, index: number, field: string) => {
  const sectionData = editableContent.value.content[section]
  if (sectionData && sectionData[index]) {
    sectionData[index][field] = editingValue.value
    hasChanges.value = true
  }
  editingField.value = null
  editingValue.value = ''
}

// Cancel editing
const cancelEditing = () => {
  editingField.value = null
}

// Save entire edited resume
const saveEditedResume = async () => {
  try {
    await navigator.clipboard.writeText(JSON.stringify(editableContent.value, null, 2))
    alert('Edited resume copied to clipboard!')
  } catch (err) {
    console.error('Failed to copy:', err)
    alert('Failed to copy to clipboard')
  }
}

// Reset changes
const resetChanges = () => {
  editableContent.value = JSON.parse(JSON.stringify(props.sampleFormat))
  hasChanges.value = false
}

// Remove project technology
const removeProjectTech = (projectIndex: number, techIndex: number) => {
  editableContent.value.content.projects[projectIndex].technologies.splice(techIndex, 1)
  hasChanges.value = true
}

// Remove project achievement
const removeProjectAchievement = (projectIndex: number, achIndex: number) => {
  editableContent.value.content.projects[projectIndex].achievements.splice(achIndex, 1)
  hasChanges.value = true
}

// Remove skill
const removeSkill = (skillIndex: number) => {
  editableContent.value.content.skills.splice(skillIndex, 1)
  hasChanges.value = true
}

const copyToClipboard = async (data: Record<string, any>, tabName: string) => {
  try {
    await navigator.clipboard.writeText(JSON.stringify(data, null, 2))
    copiedTab.value = tabName
    setTimeout(() => {
      copiedTab.value = null
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>

<style scoped>
.resume-rewrite-result {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.125rem;
  color: #4a5568;
  margin-bottom: 0.5rem;
}

.time-badge {
  display: inline-block;
  background-color: #48bb78;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.enhancements-summary {
  background-color: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.enhancements-summary h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
}

.enhancements-summary ul {
  list-style-type: disc;
  margin-left: 1.5rem;
  color: #4a5568;
}

.enhancements-summary li {
  margin-bottom: 0.5rem;
  line-height: 1.6;
}

.tabs-container {
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  overflow: hidden;
}

.tabs-header {
  display: flex;
  background-color: #f7fafc;
  border-bottom: 1px solid #e2e8f0;
}

.tab-button {
  flex: 1;
  padding: 1rem 1.5rem;
  background: none;
  border: none;
  font-size: 1rem;
  font-weight: 500;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 3px solid transparent;
}

.tab-button:hover {
  background-color: #edf2f7;
  color: #2d3748;
}

.tab-button.active {
  color: #3182ce;
  border-bottom-color: #3182ce;
  background-color: white;
}

.tabs-content {
  padding: 1.5rem;
}

.tab-pane {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tab-pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.tab-pane-header h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.copy-button {
  padding: 0.5rem 1rem;
  background-color: #3182ce;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.copy-button:hover {
  background-color: #2c5282;
}

.json-viewer {
  background-color: #1a202c;
  color: #e2e8f0;
  padding: 1.5rem;
  border-radius: 0.375rem;
  overflow-x: auto;
  max-height: 600px;
  overflow-y: auto;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
}

.json-viewer code {
  color: inherit;
  background: none;
  padding: 0;
}

/* Scrollbar styling for JSON viewer */
.json-viewer::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.json-viewer::-webkit-scrollbar-track {
  background: #2d3748;
  border-radius: 0.375rem;
}

.json-viewer::-webkit-scrollbar-thumb {
  background: #4a5568;
  border-radius: 0.375rem;
}

.json-viewer::-webkit-scrollbar-thumb:hover {
  background: #718096;
}

/* Resume Preview Styles */
.resume-preview {
  background-color: #f7fafc;
  padding: 2rem;
  border-radius: 0.5rem;
  min-height: 600px;
}

.resume-container {
  background-color: white;
  max-width: 850px;
  margin: 0 auto;
  padding: 3rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border-radius: 0.5rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* Header Section */
.resume-header {
  text-align: center;
  padding-bottom: 2rem;
  border-bottom: 2px solid #e2e8f0;
  margin-bottom: 2rem;
}

.resume-name {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 0.5rem;
  letter-spacing: -0.025em;
}

.resume-job-title {
  font-size: 1.25rem;
  color: #4a5568;
  margin-bottom: 1rem;
  font-weight: 500;
}

.resume-contact {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  flex-wrap: wrap;
  color: #718096;
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
}

.resume-social {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 0.75rem;
}

.social-link {
  color: #3182ce;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: color 0.2s;
}

.social-link:hover {
  color: #2c5282;
  text-decoration: underline;
}

/* Section Styles */
.resume-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 1.125rem;
}

.section-content {
  color: #4a5568;
  line-height: 1.7;
  font-size: 0.95rem;
}

/* Work Experience */
.experience-item {
  margin-bottom: 2rem;
}

.experience-item:last-child {
  margin-bottom: 0;
}

.experience-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  gap: 1rem;
}

.experience-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.experience-company {
  font-size: 0.95rem;
  color: #4a5568;
  font-weight: 500;
}

.experience-dates {
  font-size: 0.875rem;
  color: #718096;
  white-space: nowrap;
  font-weight: 500;
}

.experience-description {
  color: #4a5568;
  line-height: 1.7;
  font-size: 0.95rem;
}

.experience-description :deep(ul) {
  margin-left: 1.25rem;
  margin-top: 0.5rem;
}

.experience-description :deep(li) {
  margin-bottom: 0.5rem;
}

.experience-description :deep(strong) {
  color: #2d3748;
  font-weight: 600;
}

/* Projects */
.project-item {
  margin-bottom: 1.75rem;
  padding-bottom: 1.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.project-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

.project-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.75rem;
}

.project-description {
  color: #4a5568;
  line-height: 1.7;
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
}

.project-description :deep(p) {
  margin-bottom: 0.5rem;
}

.project-description :deep(strong) {
  color: #2d3748;
  font-weight: 600;
}

.project-technologies {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.tech-badge {
  display: inline-block;
  background-color: #edf2f7;
  color: #2d3748;
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.8rem;
  font-weight: 500;
  border: 1px solid #cbd5e0;
}

.project-achievements {
  margin-top: 0.75rem;
}

.achievement-item {
  color: #4a5568;
  font-size: 0.875rem;
  margin-bottom: 0.375rem;
  padding-left: 0.25rem;
}

/* Skills */
.skills-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.skill-badge {
  display: inline-block;
  background-color: #3182ce;
  color: white;
  padding: 0.375rem 0.875rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Education */
.education-item {
  margin-bottom: 1.5rem;
}

.education-item:last-child {
  margin-bottom: 0;
}

.education-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.education-degree {
  font-size: 1.075rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.education-institution {
  font-size: 0.95rem;
  color: #4a5568;
  font-weight: 500;
}

.education-date {
  font-size: 0.875rem;
  color: #718096;
  white-space: nowrap;
}

.education-gpa {
  font-size: 0.875rem;
  color: #718096;
  margin-top: 0.25rem;
}

/* Certifications */
.certification-item {
  margin-bottom: 1rem;
}

.certification-item:last-child {
  margin-bottom: 0;
}

.certification-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.certification-issuer {
  font-size: 0.875rem;
  color: #718096;
}

/* Edit Controls */
.edit-controls {
  background-color: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 0.5rem;
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.changes-indicator {
  font-weight: 600;
  color: #856404;
  margin: 0;
}

.control-buttons {
  display: flex;
  gap: 0.75rem;
}

.save-button {
  padding: 0.5rem 1rem;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.save-button:hover {
  background-color: #218838;
}

.reset-button {
  padding: 0.5rem 1rem;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.reset-button:hover {
  background-color: #5a6268;
}

/* Editable Fields */
.editable-field-container {
  position: relative;
}

.editable-field {
  cursor: pointer;
  transition: background-color 0.2s;
  padding: 0.5rem;
  margin: -0.5rem;
  border-radius: 0.25rem;
}

.editable-field:hover {
  background-color: #f7fafc;
  outline: 2px dashed #cbd5e0;
}

.editing-container {
  margin: 0.5rem 0;
}

.edit-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #3182ce;
  border-radius: 0.375rem;
  font-family: inherit;
  font-size: 0.95rem;
  line-height: 1.7;
  color: #2d3748;
  resize: vertical;
}

.edit-textarea:focus {
  outline: none;
  border-color: #2c5282;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.save-edit-btn {
  padding: 0.375rem 0.875rem;
  background-color: #3182ce;
  color: white;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.save-edit-btn:hover {
  background-color: #2c5282;
}

.cancel-edit-btn {
  padding: 0.375rem 0.875rem;
  background-color: #e2e8f0;
  color: #2d3748;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-edit-btn:hover {
  background-color: #cbd5e0;
}

/* Suggested Achievements */
.suggested-achievement {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #fff9e6;
  padding: 0.5rem;
  border-radius: 0.25rem;
  border: 1px solid #ffd700;
}

.suggestion-badge {
  display: inline-block;
  background-color: #ffc107;
  color: #856404;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.achievement-text {
  flex: 1;
  color: #4a5568;
  font-size: 0.875rem;
}

.suggestion-actions {
  display: flex;
  gap: 0.25rem;
}

.accept-btn,
.reject-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.accept-btn {
  background-color: #28a745;
  color: white;
}

.accept-btn:hover {
  background-color: #218838;
  transform: scale(1.1);
}

.reject-btn {
  background-color: #dc3545;
  color: white;
}

.reject-btn:hover {
  background-color: #c82333;
  transform: scale(1.1);
}

/* Edit Resume Tab Styles */
.edit-sections {
  max-width: 900px;
  margin: 0 auto;
}

.edit-section {
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.edit-section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e2e8f0;
}

.edit-item {
  padding: 1.25rem;
  margin-bottom: 1.25rem;
  background-color: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
}

.edit-item:last-child {
  margin-bottom: 0;
}

.edit-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
}

.edit-item-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.edit-item-dates {
  font-size: 0.875rem;
  color: #718096;
  white-space: nowrap;
}

.edit-field {
  margin-bottom: 1rem;
}

.edit-field:last-child {
  margin-bottom: 0;
}

.edit-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 0.5rem;
}

.edit-input-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #cbd5e0;
  border-radius: 0.375rem;
  font-family: inherit;
  font-size: 0.95rem;
  line-height: 1.6;
  color: #2d3748;
  resize: vertical;
  transition: border-color 0.2s;
}

.edit-input-textarea:focus {
  outline: none;
  border-color: #3182ce;
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
}

.edit-hint {
  font-size: 0.8rem;
  color: #718096;
  margin-top: 0.5rem;
  font-style: italic;
}

/* Tech Tags Edit */
.tech-tags-edit {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tech-tag-edit {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #edf2f7;
  color: #2d3748;
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid #cbd5e0;
}

.tech-remove-btn {
  background: none;
  border: none;
  color: #e53e3e;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.tech-remove-btn:hover {
  color: #c53030;
}

/* Achievements Edit */
.achievements-edit {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.achievement-edit-item {
  display: block;
}

/* Suggested Achievement in Edit Tab */
.suggested-achievement-edit {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background-color: #fff9e6;
  padding: 0.75rem;
  border-radius: 0.375rem;
  border: 2px solid #ffc107;
}

.suggestion-badge-edit {
  display: inline-block;
  background-color: #ffc107;
  color: #856404;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.achievement-text-edit {
  flex: 1;
  color: #2d3748;
  font-size: 0.95rem;
}

.suggestion-actions-edit {
  display: flex;
  gap: 0.5rem;
}

.accept-btn-edit,
.reject-btn-edit {
  padding: 0.375rem 0.875rem;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.accept-btn-edit {
  background-color: #28a745;
  color: white;
}

.accept-btn-edit:hover {
  background-color: #218838;
}

.reject-btn-edit {
  background-color: #dc3545;
  color: white;
}

.reject-btn-edit:hover {
  background-color: #c82333;
}

/* Accepted Achievement in Edit Tab */
.accepted-achievement-edit {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
}

.achievement-check {
  color: #28a745;
  font-weight: 700;
  font-size: 1rem;
}

.achievement-input-edit {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #cbd5e0;
  border-radius: 0.25rem;
  font-size: 0.9rem;
  color: #2d3748;
  transition: border-color 0.2s;
}

.achievement-input-edit:focus {
  outline: none;
  border-color: #3182ce;
  box-shadow: 0 0 0 2px rgba(49, 130, 206, 0.1);
}

.achievement-remove-btn {
  background: none;
  border: none;
  color: #e53e3e;
  font-size: 0.95rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  transition: color 0.2s;
}

.achievement-remove-btn:hover {
  color: #c53030;
}

/* Skills Edit */
.skills-edit {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.skill-tag-edit {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #3182ce;
  color: white;
  padding: 0.5rem 0.875rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.skill-remove-btn {
  background: none;
  border: none;
  color: white;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
}

.skill-remove-btn:hover {
  opacity: 0.8;
}
</style>
