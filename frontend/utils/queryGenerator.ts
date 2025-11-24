export interface JobSearchQuery {
  id: number
  query: string
  description: string
}

export interface QuerySet {
  domainName: string
  technicalRole: string
  industry: string
  queries: JobSearchQuery[]
}

// Role synonym mappings for common technical and non-technical roles
const ROLE_SYNONYMS: Record<string, string[]> = {
  // Full-Stack
  'full-stack': ['full-stack developer', 'fullstack engineer', 'full stack developer', 'full-stack engineer', 'fullstack developer'],
  'full stack': ['full-stack developer', 'fullstack engineer', 'full stack developer'],

  // Backend
  'backend': ['backend engineer', 'back-end developer', 'server-side engineer', 'backend developer', 'API developer'],
  'back-end': ['backend engineer', 'back-end developer', 'backend developer'],

  // Frontend
  'frontend': ['frontend engineer', 'front-end developer', 'UI engineer', 'frontend developer', 'web developer'],
  'front-end': ['frontend engineer', 'front-end developer', 'frontend developer'],

  // DevOps & Infrastructure
  'devops': ['devops engineer', 'SRE', 'site reliability engineer', 'infrastructure engineer', 'cloud engineer'],
  'cloud': ['cloud engineer', 'cloud architect', 'AWS engineer', 'azure engineer', 'cloud infrastructure engineer'],
  'sre': ['SRE', 'site reliability engineer', 'devops engineer', 'platform engineer'],

  // Data & Analytics
  'data scientist': ['data scientist', 'ML engineer', 'machine learning engineer', 'data analyst', 'analytics engineer'],
  'data engineer': ['data engineer', 'big data engineer', 'ETL developer', 'data pipeline engineer'],
  'data analyst': ['data analyst', 'business intelligence analyst', 'analytics engineer'],

  // Mobile
  'mobile': ['mobile developer', 'iOS developer', 'android developer', 'mobile engineer', 'react native developer'],
  'ios': ['iOS developer', 'iOS engineer', 'swift developer', 'mobile developer'],
  'android': ['android developer', 'android engineer', 'kotlin developer', 'mobile developer'],

  // Design
  'ux designer': ['UX designer', 'UI/UX designer', 'user experience designer', 'product designer'],
  'ui designer': ['UI designer', 'user interface designer', 'visual designer', 'product designer'],
  'product designer': ['product designer', 'UX designer', 'UI/UX designer'],

  // Product & Management
  'product manager': ['product manager', 'technical product manager', 'APM', 'product lead', 'PM'],
  'project manager': ['project manager', 'technical project manager', 'scrum master', 'agile coach'],

  // QA & Testing
  'qa engineer': ['QA engineer', 'test engineer', 'quality assurance engineer', 'automation engineer', 'SDET'],

  // Security
  'security engineer': ['security engineer', 'cybersecurity engineer', 'information security analyst', 'security analyst'],

  // Architecture
  'solutions architect': ['solutions architect', 'enterprise architect', 'technical architect', 'cloud architect'],
  'software architect': ['software architect', 'principal engineer', 'technical architect'],

  // Non-Technical Career Transitions
  'supply chain analyst': ['supply chain analyst', 'logistics analyst', 'operations analyst', 'procurement analyst'],
  'logistics coordinator': ['logistics coordinator', 'supply chain coordinator', 'operations coordinator'],
  'healthcare it': ['healthcare IT specialist', 'clinical informatics', 'medical technology specialist', 'health informatics'],
  'clinical informatics': ['clinical informatics specialist', 'healthcare data analyst', 'medical informatics'],
  'legal technology': ['legal technology specialist', 'legaltech', 'legal operations', 'legal engineer'],
  'compliance analyst': ['compliance analyst', 'regulatory analyst', 'compliance officer'],

  // Entry Level
  'junior': ['junior developer', 'junior engineer', 'entry level developer', 'associate developer'],
  'intern': ['intern', 'internship', 'co-op', 'summer intern'],
  'entry level': ['entry level', 'junior', 'associate', 'graduate']
}

// Industry keyword mappings
const INDUSTRY_KEYWORDS: Record<string, string[]> = {
  // Tech Industries
  'gaming': ['gaming', 'game development', 'video games', 'game studios', 'interactive entertainment'],
  'fintech': ['fintech', 'financial technology', 'banking', 'payments', 'digital banking', 'cryptocurrency'],
  'healthtech': ['healthtech', 'health tech', 'medical technology', 'healthcare software', 'telehealth', 'digital health'],
  'edtech': ['edtech', 'education technology', 'online learning', 'e-learning', 'educational software'],
  'saas': ['saas', 'software as a service', 'cloud software', 'b2b software', 'enterprise software'],
  'ecommerce': ['ecommerce', 'e-commerce', 'retail tech', 'online shopping', 'marketplace'],
  'e-commerce': ['e-commerce', 'ecommerce', 'retail tech', 'online retail'],

  // Specialized Tech
  'media': ['media', 'streaming', 'content delivery', 'digital media', 'entertainment technology'],
  'advertising': ['adtech', 'advertising technology', 'marketing technology', 'martech', 'digital advertising'],
  'martech': ['martech', 'marketing technology', 'marketing automation', 'adtech'],
  'social media': ['social media', 'social networking', 'community platform'],
  'cybersecurity': ['cybersecurity', 'information security', 'security', 'infosec'],

  // Industry Domains
  'transportation': ['transportation', 'mobility', 'ride-sharing', 'logistics tech', 'fleet management'],
  'real estate': ['real estate', 'proptech', 'property technology', 'real estate tech'],
  'travel': ['travel', 'hospitality', 'booking platform', 'travel tech'],
  'food tech': ['food tech', 'food delivery', 'restaurant technology', 'foodtech'],

  // Traditional Industries Transitioning to Tech
  'healthcare': ['healthcare', 'medical', 'hospital', 'clinical', 'health services'],
  'finance': ['finance', 'banking', 'financial services', 'investment'],
  'insurance': ['insurance', 'insurtech', 'insurance technology'],
  'legal': ['legal', 'legaltech', 'law', 'legal services'],
  'supply chain': ['supply chain', 'logistics', 'warehousing', 'distribution'],
  'logistics': ['logistics', 'supply chain', 'transportation', 'freight'],
  'manufacturing': ['manufacturing', 'industrial', 'factory automation', 'IoT'],

  // Emerging Fields
  'ai': ['AI', 'artificial intelligence', 'machine learning', 'deep learning'],
  'blockchain': ['blockchain', 'cryptocurrency', 'web3', 'crypto'],
  'iot': ['IoT', 'internet of things', 'connected devices', 'smart devices'],
  'cloud services': ['cloud', 'AWS', 'Azure', 'GCP', 'cloud infrastructure']
}

/**
 * Normalize role name to find matching synonyms
 */
function normalizeRole(role: string): string {
  const normalized = role.toLowerCase()

  // Check for direct matches first
  if (ROLE_SYNONYMS[normalized]) {
    return normalized
  }

  // Check for partial matches
  for (const key in ROLE_SYNONYMS) {
    if (normalized.includes(key) || key.includes(normalized)) {
      return key
    }
  }

  // Default fallback
  return normalized
}

/**
 * Normalize industry name to find matching keywords
 */
function normalizeIndustry(industry: string): string {
  const normalized = industry.toLowerCase()

  // Check for direct matches first
  if (INDUSTRY_KEYWORDS[normalized]) {
    return normalized
  }

  // Check for partial matches
  for (const key in INDUSTRY_KEYWORDS) {
    if (normalized.includes(key) || key.includes(normalized)) {
      return key
    }
  }

  // Default fallback
  return normalized
}

/**
 * Get role synonyms for a given technical role
 */
export function getRoleSynonyms(technicalRole: string): string[] {
  const normalized = normalizeRole(technicalRole)
  const synonyms = ROLE_SYNONYMS[normalized] || [technicalRole.toLowerCase()]

  // Return first 5 synonyms max
  return synonyms.slice(0, 5)
}

/**
 * Get industry keywords for a given industry
 */
export function getIndustryKeywords(industry: string): string[] {
  const normalized = normalizeIndustry(industry)
  const keywords = INDUSTRY_KEYWORDS[normalized] || [industry.toLowerCase()]

  // Return first 5 keywords max
  return keywords.slice(0, 5)
}

/**
 * Generate 10 job search query variations for a single domain
 */
export function generateQueriesForDomain(technicalRole: string, industry: string, domainName: string): QuerySet {
  const roleSynonyms = getRoleSynonyms(technicalRole)
  const industryKeywords = getIndustryKeywords(industry)

  const queries: JobSearchQuery[] = []

  // Query 1: Basic combination (first 2 role synonyms + first 2 industry keywords)
  queries.push({
    id: 1,
    query: `intitle:jobs ("${roleSynonyms[0]}" OR "${roleSynonyms[1] || roleSynonyms[0]}") ("${industryKeywords[0]}" OR "${industryKeywords[1] || industryKeywords[0]}")`,
    description: 'Standard search with primary role and industry terms'
  })

  // Query 2: Alternative role synonyms (synonyms 2-3 + keywords 2-3)
  queries.push({
    id: 2,
    query: `intitle:jobs ("${roleSynonyms[2] || roleSynonyms[0]}" OR "${roleSynonyms[3] || roleSynonyms[1]}") ("${industryKeywords[2] || industryKeywords[0]}" OR "${industryKeywords[3] || industryKeywords[1]}")`,
    description: 'Alternative synonyms for broader coverage'
  })

  // Query 3: All role variations (first 3) + primary industry
  queries.push({
    id: 3,
    query: `intitle:jobs ("${roleSynonyms[0]}" OR "${roleSynonyms[1] || roleSynonyms[0]}" OR "${roleSynonyms[2] || roleSynonyms[0]}") "${industryKeywords[0]}"`,
    description: 'Multiple role variations with primary industry'
  })

  // Query 4: Primary role + all industry keywords (first 3)
  queries.push({
    id: 4,
    query: `intitle:jobs "${roleSynonyms[0]}" ("${industryKeywords[0]}" OR "${industryKeywords[1] || industryKeywords[0]}" OR "${industryKeywords[2] || industryKeywords[0]}")`,
    description: 'Primary role with multiple industry keywords'
  })

  // Query 5: Combination with most variations
  queries.push({
    id: 5,
    query: `intitle:jobs ("${roleSynonyms[0]}" OR "${roleSynonyms[1] || roleSynonyms[0]}") ("${industryKeywords[0]}" OR "${industryKeywords[1] || industryKeywords[0]}" OR "${industryKeywords[2] || industryKeywords[0]}")`,
    description: 'Comprehensive search with multiple variations'
  })

  // Query 6: LinkedIn-specific search
  queries.push({
    id: 6,
    query: `site:linkedin.com/jobs intitle:jobs ("${roleSynonyms[0]}" OR "${roleSynonyms[1] || roleSynonyms[0]}") ("${industryKeywords[0]}" OR "${industryKeywords[1] || industryKeywords[0]}")`,
    description: 'LinkedIn-focused search'
  })

  // Query 7: Indeed-specific search
  queries.push({
    id: 7,
    query: `site:indeed.com intitle:jobs ("${roleSynonyms[0]}" OR "${roleSynonyms[1] || roleSynonyms[0]}") ("${industryKeywords[0]}" OR "${industryKeywords[1] || industryKeywords[0]}")`,
    description: 'Indeed-focused search'
  })

  // Query 8: Remote work variation
  queries.push({
    id: 8,
    query: `intitle:jobs ("${roleSynonyms[0]}" OR "${roleSynonyms[1] || roleSynonyms[0]}") ("${industryKeywords[0]}" OR "${industryKeywords[1] || industryKeywords[0]}") ("remote" OR "work from home")`,
    description: 'Search for remote opportunities'
  })

  // Query 9: Senior/Lead level variation
  queries.push({
    id: 9,
    query: `intitle:jobs ("senior ${roleSynonyms[0]}" OR "lead ${roleSynonyms[1] || roleSynonyms[0]}") ("${industryKeywords[0]}" OR "${industryKeywords[1] || industryKeywords[0]}")`,
    description: 'Senior-level positions'
  })

  // Query 10: Startup/scale-up focused
  queries.push({
    id: 10,
    query: `intitle:jobs ("${roleSynonyms[0]}" OR "${roleSynonyms[1] || roleSynonyms[0]}") ("${industryKeywords[0]}" OR "${industryKeywords[1] || industryKeywords[0]}") ("startup" OR "scale-up")`,
    description: 'Startup and growth company opportunities'
  })

  return {
    domainName,
    technicalRole,
    industry,
    queries
  }
}

/**
 * Generate job search queries for multiple domains
 */
export function generateJobSearchQueries(domains: Array<{technical_role: string, industry: string, domain_name: string}>): QuerySet[] {
  return domains.map(domain =>
    generateQueriesForDomain(domain.technical_role, domain.industry, domain.domain_name)
  )
}
