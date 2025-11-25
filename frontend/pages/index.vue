<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-10">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">CV/JD Compatibility Analyzer</h1>
        <p class="text-lg text-gray-600">Powered by Gemini 2.5 Flash-Lite & Advanced Embeddings</p>
      </div>

      <!-- Navigation Links -->
      <div class="mb-6 flex justify-center gap-4">
        <NuxtLink to="/domain-finder">
          <HbButton variant="secondary">
            <template #leading-icon>
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </template>
            Discover Career Domains
          </HbButton>
        </NuxtLink>
      </div>

      <!-- Input Card -->
      <HbCard>
        <!-- Language Selector -->
        <div class="mb-6 flex justify-end">
          <HbSelect
            v-model="selectedLanguage"
            :options="languageOptions"
          />
        </div>

        <!-- Dual Input Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <!-- Job Description Input -->
          <div>
            <div class="flex justify-between items-center mb-3">
              <label class="block text-sm font-semibold text-gray-700">
                Job Description
              </label>
              <div class="flex items-center gap-2">
                <HbSelect
                  v-model="selectedSampleType"
                  :options="sampleTypeOptions"
                  class="text-xs"
                />
                <HbButton
                  @click="loadSampleJob"
                  variant="link"
                  size="sm"
                >
                  Load Sample
                </HbButton>
              </div>
            </div>

            <HbInput
              v-model="jobDescription"
              type="textarea"
              :rows="15"
              placeholder="Paste job description here (minimum 50 characters)..."
            />

            <div class="flex justify-between items-center mt-2">
              <span class="text-sm" :class="jobDescription.length > 6200 ? 'text-amber-600' : 'text-gray-500'">
                {{ jobDescription.length }} / 6200 characters
              </span>
              <span v-if="jobDescription.length < 50 && jobDescription.length > 0" class="text-sm text-red-500">
                Need {{ 50 - jobDescription.length }} more
              </span>
            </div>
          </div>

          <!-- CV/Resume Input -->
          <div>
            <div class="flex justify-between items-center mb-3">
              <label class="block text-sm font-semibold text-gray-700">
                CV / Resume
              </label>
              <HbButton
                @click="loadSampleCV"
                variant="link"
                size="sm"
              >
                Load Sample
              </HbButton>
            </div>

            <HbInput
              v-model="cvText"
              type="textarea"
              :rows="15"
              placeholder="Paste resume/CV here (minimum 50 characters)..."
            />

            <div class="flex justify-between items-center mt-2">
              <span class="text-sm" :class="cvText.length > 6200 ? 'text-amber-600' : 'text-gray-500'">
                {{ cvText.length }} / 6200 characters
              </span>
              <span v-if="cvText.length < 50 && cvText.length > 0" class="text-sm text-red-500">
                Need {{ 50 - cvText.length }} more
              </span>
            </div>
          </div>
        </div>

        <!-- Next Button -->
        <HbButton
          @click="handleNext"
          :disabled="!isValidInput"
          variant="primary"
          size="lg"
          class="w-full"
        >
          <span v-if="isValidInput">
            Analyze Compatibility →
          </span>
          <span v-else>
            Please enter both JD and CV (minimum 50 characters each)
          </span>
        </HbButton>

        <p class="mt-4 text-center text-sm text-gray-600">
          Advanced analysis using embeddings, semantic matching, and AI-powered gap analysis
        </p>
      </HbCard>

      <!-- Info Footer -->
      <div class="mt-8 text-center text-sm text-gray-600">
        <p>Comprehensive analysis including: Category Scores • Gap Analysis • Strengths • Application Viability</p>
        <p class="mt-1">Processing time: ~7-8 seconds per analysis</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const selectedLanguage = ref('english')
const selectedSampleType = ref('poor-match')  // 'poor-match' or 'good-match'
const jobDescription = ref('')
const cvText = ref('')

const { setInput } = useAnalysisState()
const router = useRouter()

// Language options for HbSelect
const languageOptions = [
  { value: 'english', label: '🇬🇧 English' },
  { value: 'french', label: '🇫🇷 Français' },
  { value: 'german', label: '🇩🇪 Deutsch' },
  { value: 'spanish', label: '🇪🇸 Español' }
]

// Sample type options for HbSelect
const sampleTypeOptions = [
  { value: 'poor-match', label: 'AI/ML Engineer (Poor Match ~16%)' },
  { value: 'good-match', label: 'Backend Engineer (Good Match ~75%)' }
]

const isValidInput = computed(() => {
  return jobDescription.value.length >= 50 && cvText.value.length >= 50
})

const sampleJob = `Senior AI/ML Engineer | AI Startup Inc

Location: San Francisco, CA (onsite)
Salary: $180,000 - $250,000
Experience Required: 10+ years

About the Role:
We are building the rails to put real world assets on-chain. Join our team to work at the intersection of high-performance backend systems, crypto infrastructure, and financial engineering.

Requirements:
- 10+ years of professional experience in software development
- Strong experience with Machine Learning frameworks (TensorFlow, PyTorch - CRITICAL)
- Deep expertise in Large Language Models (LLMs) and deploying them in production
- Experience with MLOps, model deployment, and monitoring
- Strong programming skills in Python
- Experience with NLP and/or Computer Vision
- Knowledge of AWS, Docker, and Kubernetes
- Experience with Vector Databases is a plus
- Knowledge of Rust is a bonus

Tech Stack:
Python, TensorFlow, PyTorch, Transformers, AWS SageMaker, Docker, Kubernetes, MLflow

Responsibilities:
- Design and implement state-of-the-art ML models for production systems
- Build and deploy LLM-based applications at scale
- Optimize model performance and inference speed
- Collaborate with product team on AI feature development
- Conduct ML research and experiments
- Mentor junior ML engineers and establish best practices

What We Offer:
- Competitive compensation and equity
- Work on cutting-edge AI technology
- Fast-paced startup environment
- Opportunity to shape the DNA of a generational company`

const sampleJobGoodMatch = `Senior Backend Engineer | TechScale Solutions

Location: San Francisco, CA (hybrid)
Salary: $160,000 - $200,000
Experience Required: 5-8 years

About the Role:
We're building scalable cloud infrastructure for our rapidly growing SaaS platform. Join our backend team to design and implement high-performance APIs and microservices.

Requirements:
- 5-8 years of professional software development experience
- Strong expertise in Python and modern web frameworks (Flask, FastAPI - CRITICAL)
- Experience building RESTful APIs and microservices architecture
- Proficiency with cloud platforms, especially AWS (EC2, Lambda, RDS, S3)
- Strong knowledge of Docker and Kubernetes
- Experience with SQL and NoSQL databases (PostgreSQL, Redis, MongoDB)
- Understanding of CI/CD pipelines and DevOps practices
- Experience with caching strategies and performance optimization
- Agile/Scrum methodology experience
- Strong problem-solving and analytical skills

Tech Stack:
Python, FastAPI, Node.js, PostgreSQL, Redis, AWS, Docker, Kubernetes, Git, CI/CD

Responsibilities:
- Design and develop scalable REST APIs serving millions of requests
- Build and maintain microservices architecture
- Optimize database queries and API performance
- Implement caching layers and improve system reliability
- Lead code reviews and mentor junior developers
- Collaborate with frontend and product teams
- Deploy and monitor production services on AWS
- Participate in on-call rotation and incident response

What We Offer:
- Competitive salary and equity
- Flexible hybrid work environment
- Modern tech stack and clean codebase
- Strong engineering culture
- Career growth opportunities`

const sampleCV = `John Doe
Email: john.doe@email.com | Phone: (555) 123-4567
Location: San Francisco, CA | LinkedIn: linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Senior Software Engineer with 8 years of experience building scalable systems and leading technical projects. Strong expertise in Python, JavaScript, cloud infrastructure, and microservices architecture.

TECHNICAL SKILLS
Languages: Python, JavaScript, SQL
Frameworks: React, Node.js, Flask, FastAPI
Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD, Git
Databases: PostgreSQL, Redis, MongoDB
Methodologies: Microservices, REST APIs, TDD, Agile

WORK EXPERIENCE

Senior Software Engineer | Tech Corp | 2020 - Present (4 years)
- Built scalable microservices handling 1M+ requests per day
- Led team of 5 engineers in cloud migration project from on-premise to AWS
- Reduced API latency by 60% through caching and optimization strategies
- Implemented CI/CD pipeline reducing deployment time by 80%
- Designed and developed REST APIs used by 50+ internal services

Software Engineer | StartupXYZ | 2016 - 2020 (4 years)
- Developed REST APIs using Python Flask for e-commerce platform
- Integrated payment processing system (Stripe) handling $2M+ monthly transactions
- Built automated testing framework improving code coverage from 40% to 85%
- Collaborated with frontend team on React-based admin dashboard

EDUCATION
B.S. Computer Science | University of Technology | 2016
GPA: 3.7/4.0

SOFT SKILLS
- Team collaboration and cross-functional communication
- Problem solving and analytical thinking
- Technical leadership and mentoring
- Adaptable to fast-paced environments`

const loadSampleJob = () => {
  if (selectedSampleType.value === 'good-match') {
    jobDescription.value = sampleJobGoodMatch
  } else {
    jobDescription.value = sampleJob
  }
}

const loadSampleCV = () => {
  cvText.value = sampleCV
}

const handleNext = () => {
  if (!isValidInput.value) return

  // Save to shared state
  setInput(jobDescription.value, cvText.value, selectedLanguage.value)

  // Navigate to analyze page
  router.push('/analyze')
}
</script>
