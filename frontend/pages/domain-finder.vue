<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 py-12 px-4">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-10">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">Career Domain Finder</h1>
        <p class="text-lg text-gray-600">Discover the best career paths based on your skills and experience</p>
        <p class="text-sm text-gray-500 mt-2">Powered by Gemini 2.5 Flash-Lite</p>
      </div>

      <!-- Navigation Links -->
      <div class="mb-6 flex justify-center gap-4">
        <NuxtLink
          to="/"
          class="text-sm text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-2"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Job Matcher
        </NuxtLink>
      </div>

      <!-- Input Card -->
      <div class="bg-white rounded-xl shadow-xl p-8 mb-8">
        <!-- Language Selector -->
        <div class="mb-6 flex justify-end">
          <select
            v-model="selectedLanguage"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option value="english">🇬🇧 English</option>
            <option value="french">🇫🇷 Français</option>
            <option value="german">🇩🇪 Deutsch</option>
            <option value="spanish">🇪🇸 Español</option>
          </select>
        </div>

        <!-- Resume Input -->
        <div>
          <div class="flex justify-between items-center mb-3">
            <label class="block text-sm font-semibold text-gray-700">
              Your Resume / CV
            </label>
            <div class="flex items-center gap-2">
              <select
                v-model="selectedSampleProfile"
                class="text-sm px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <optgroup label="Technical Careers">
                  <option value="fullstack">Full-Stack Engineer (5 yrs)</option>
                  <option value="intern">Student Seeking Internship</option>
                  <option value="uxdesigner">Junior UX Designer (1-2 yrs)</option>
                </optgroup>
                <optgroup label="Career Transitions to Tech">
                  <option value="logistics">Logistics Coordinator (3-4 yrs)</option>
                  <option value="healthcare">Medical Professional (2-3 yrs)</option>
                  <option value="lawyer">Lawyer (3-5 yrs)</option>
                </optgroup>
              </select>
              <button
                @click="loadSampleResume"
                class="text-sm text-green-600 hover:text-green-800 font-medium whitespace-nowrap"
              >
                Load Sample
              </button>
            </div>
          </div>

          <textarea
            v-model="resumeText"
            rows="15"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
            placeholder="Paste your resume here (minimum 50 characters)..."
          ></textarea>

          <div class="flex justify-between items-center mt-2">
            <span class="text-sm" :class="resumeText.length > 6200 ? 'text-amber-600' : 'text-gray-500'">
              {{ resumeText.length }} / 6200 characters
            </span>
            <span v-if="resumeText.length < 50 && resumeText.length > 0" class="text-sm text-red-500">
              Need {{ 50 - resumeText.length }} more
            </span>
          </div>
        </div>

        <!-- Analyze Button -->
        <div class="mt-6 flex justify-center">
          <button
            @click="analyzeDomains"
            :disabled="isLoading || resumeText.length < 50"
            class="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <svg v-if="isLoading" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span v-if="!isLoading">Analyze My Career Domains</span>
            <span v-else>Analyzing...</span>
          </button>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div class="flex items-start">
          <svg class="h-5 w-5 text-red-600 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <div class="flex-1">
            <h3 class="text-sm font-semibold text-red-800 mb-1">Analysis Error</h3>
            <p class="text-sm text-red-700">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="bg-white rounded-xl shadow-xl p-12">
        <div class="flex flex-col items-center justify-center">
          <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mb-4"></div>
          <p class="text-lg font-medium text-gray-700">Analyzing your resume...</p>
          <p class="text-sm text-gray-500 mt-2">This may take a few seconds</p>
        </div>
      </div>

      <!-- Results -->
      <div v-if="result && result.success && result.domains" class="bg-white rounded-xl shadow-xl p-8">
        <!-- Refresh Button -->
        <div class="mb-6 flex justify-end">
          <button
            @click="refreshResults"
            :disabled="isLoading"
            class="px-4 py-2 bg-white border-2 border-indigo-600 text-indigo-600 font-medium rounded-lg hover:bg-indigo-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <svg class="h-4 w-4" :class="{ 'animate-spin': isLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>{{ isLoading ? 'Refreshing...' : 'Refresh Results' }}</span>
          </button>
        </div>

        <DomainFinderResult
          :domains="result.domains"
          :time-seconds="result.time_seconds"
        />
      </div>

      <!-- No Results -->
      <div v-if="result && !result.success" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div class="flex items-start">
          <svg class="h-6 w-6 text-yellow-600 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          <div class="flex-1">
            <h3 class="text-sm font-semibold text-yellow-800 mb-1">Could Not Generate Domain Suggestions</h3>
            <p class="text-sm text-yellow-700">{{ result.error || 'Please try again with a different resume' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { SAMPLE_RESUMES } from '~/composables/useSampleResumes'

const { findDomains, isLoading, error, result } = useDomainFinder()

const resumeText = ref('')
const selectedLanguage = ref('english')
const selectedSampleProfile = ref('fullstack')

const analyzeDomains = async () => {
  await findDomains(resumeText.value, selectedLanguage.value)
}

const refreshResults = async () => {
  // Call with bypass_cache=true to force fresh results
  await findDomains(resumeText.value, selectedLanguage.value, true)
}

const loadSampleResume = () => {
  const sample = SAMPLE_RESUMES[selectedSampleProfile.value]
  if (sample) {
    resumeText.value = sample.content
  }
}

// Legacy sample loader - keeping the old hardcoded sample as backup
const loadLegacySample = () => {
  resumeText.value = `JOHN DOE
Software Engineer

Email: john.doe@email.com | Phone: (555) 123-4567 | Location: San Francisco, CA
LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

PROFESSIONAL SUMMARY
Experienced Full-Stack Software Engineer with 5 years of expertise in building scalable web applications using modern JavaScript frameworks and cloud technologies. Proven track record of delivering high-quality code and collaborating with cross-functional teams to solve complex technical challenges.

TECHNICAL SKILLS
Programming Languages: JavaScript, TypeScript, Python, Java
Frontend: React, Vue.js, Next.js, HTML5, CSS3, Tailwind CSS
Backend: Node.js, Express, FastAPI, Django, RESTful APIs, GraphQL
Databases: PostgreSQL, MongoDB, Redis, MySQL
Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD (GitHub Actions, Jenkins)
Tools & Technologies: Git, Webpack, Babel, Jest, Cypress, Postman

WORK EXPERIENCE

Senior Software Engineer | Tech Startup Inc.
San Francisco, CA | Jan 2022 - Present
- Led development of a real-time collaboration platform serving 50K+ daily active users using React, Node.js, and WebSockets
- Architected and implemented microservices architecture reducing API response time by 60%
- Mentored team of 3 junior developers and conducted code reviews to maintain code quality
- Implemented CI/CD pipeline using GitHub Actions, reducing deployment time from 2 hours to 15 minutes

Software Engineer | Digital Solutions Co.
San Francisco, CA | Jun 2020 - Dec 2021
- Developed and maintained customer-facing web applications using Vue.js and Django
- Optimized database queries improving page load times by 40%
- Collaborated with product team to implement new features based on user feedback
- Wrote comprehensive unit and integration tests achieving 85% code coverage

Junior Software Engineer | WebDev Agency
Remote | May 2019 - May 2020
- Built responsive websites and web applications for clients using React and Node.js
- Integrated third-party APIs including Stripe, SendGrid, and Twilio
- Participated in agile sprints and daily standups with distributed team

EDUCATION

Bachelor of Science in Computer Science
University of California, Berkeley | Graduated: May 2019
GPA: 3.7/4.0

PROJECTS

E-Commerce Platform (Personal Project)
- Built full-stack e-commerce application with Next.js, Node.js, and PostgreSQL
- Implemented payment processing with Stripe API and order management system
- Deployed on AWS with Docker and automated CI/CD pipeline

Chat Application with Real-time Features
- Developed real-time chat application using React, Socket.io, and Redis
- Implemented user authentication, message encryption, and file sharing
- Achieved 99.9% uptime with load balancing and horizontal scaling

CERTIFICATIONS
AWS Certified Developer - Associate (2023)
MongoDB Certified Developer (2022)`
}
</script>
