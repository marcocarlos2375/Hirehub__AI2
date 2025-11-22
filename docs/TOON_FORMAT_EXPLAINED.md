# TOON Format: Token-Optimized Object Notation

## What is TOON?

**TOON (Token-Optimized Object Notation)** is a compact, human-readable data serialization format designed specifically for **LLM (Large Language Model) applications**. It reduces token usage by 40-50% compared to JSON while maintaining the same data structure and semantic meaning.

TOON was created to optimize the input/output tokens when working with LLMs, resulting in:
- **Faster response times** (10-24% faster)
- **Lower API costs** (fewer tokens = lower cost)
- **Better context window utilization** (more data fits in the same context)

---

## Why TOON Instead of JSON?

### The Problem with JSON for LLMs

JSON is verbose with repetitive syntax that wastes tokens:

```json
{
  "company_name": "Acme Corp",
  "position_title": "Software Engineer",
  "hard_skills_required": [
    {
      "skill": "Java",
      "priority": "critical"
    },
    {
      "skill": "Spring Boot",
      "priority": "critical"
    }
  ]
}
```

**Token count: ~150 tokens** (with all the braces, quotes, commas, and indentation)

### The TOON Solution

TOON uses a cleaner, more compact syntax:

```toon
company_name: Acme Corp
position_title: Software Engineer

hard_skills_required[2]{skill,priority}:
  Java,critical
  Spring Boot,critical
```

**Token count: ~60 tokens** (60% reduction!)

---

## TOON Syntax Rules

### 1. **Simple Key-Value Pairs**
```toon
company_name: Acme Corp
position_title: Software Engineer
location: New York, NY
salary_range: $120,000 - $150,000
experience_years_required: 5
```

**Equivalent JSON:**
```json
{
  "company_name": "Acme Corp",
  "position_title": "Software Engineer",
  "location": "New York, NY",
  "salary_range": "$120,000 - $150,000",
  "experience_years_required": 5
}
```

---

### 2. **Simple Arrays**
```toon
tech_stack[5]:
  - Java
  - Spring Boot
  - React
  - AWS
  - Docker
```

**Format:** `array_name[count]:`
- `[count]` = actual number of items
- Each item starts with `- `

**Equivalent JSON:**
```json
{
  "tech_stack": [
    "Java",
    "Spring Boot",
    "React",
    "AWS",
    "Docker"
  ]
}
```

---

### 3. **Arrays of Objects with Structured Data**
```toon
hard_skills_required[12]{skill,priority}:
  Java,critical
  Spring Boot,critical
  React,important
  Typescript,important
  API design,important
  Microservice architecture,important
  Test-driven development,important
  CI/CD,important
  AWS,nice
  Docker,nice
  Kubernetes,nice
  GraphQL,nice
```

**Format:** `array_name[count]{field1,field2,...}:`
- `{skill,priority}` declares the object structure
- Each line = one object with comma-separated values
- NO dashes, NO quotes

**Equivalent JSON:**
```json
{
  "hard_skills_required": [
    {"skill": "Java", "priority": "critical"},
    {"skill": "Spring Boot", "priority": "critical"},
    {"skill": "React", "priority": "important"},
    {"skill": "Typescript", "priority": "important"},
    {"skill": "API design", "priority": "important"},
    {"skill": "Microservice architecture", "priority": "important"},
    {"skill": "Test-driven development", "priority": "important"},
    {"skill": "CI/CD", "priority": "important"},
    {"skill": "AWS", "priority": "nice"},
    {"skill": "Docker", "priority": "nice"},
    {"skill": "Kubernetes", "nice"},
    {"skill": "GraphQL", "priority": "nice"}
  ]
}
```

**Token savings: ~70%** for this structure!

---

### 4. **Nested Objects**
```toon
domain_expertise:
  industry[3]:
    - Music
    - Film
    - Television
  specific_knowledge[5]:
    - Entertainment data analysis
    - SaaS platform development
    - API design patterns
    - Cloud-native development
    - Microservices architecture
```

**Equivalent JSON:**
```json
{
  "domain_expertise": {
    "industry": [
      "Music",
      "Film",
      "Television"
    ],
    "specific_knowledge": [
      "Entertainment data analysis",
      "SaaS platform development",
      "API design patterns",
      "Cloud-native development",
      "Microservices architecture"
    ]
  }
}
```

---

## Complete Example: Job Description Parsing

### TOON Format (Full)
```toon
company_name: Luminate
position_title: Software Engineer
location: New York, NY
work_mode: hybrid
salary_range: $135,000 - $150,000
experience_years_required: 2
experience_level: mid

hard_skills_required[14]{skill,priority}:
  Java,critical
  Spring Boot,critical
  React,critical
  Typescript,critical
  API design,important
  Microservice architecture,important
  Test-driven development,important
  CI/CD,important
  AWS,nice
  Object-oriented design,important
  SaaS platform development,important
  Data aggregation and analysis,important
  Software testing,important
  Database management,nice

soft_skills_required[6]:
  - Strong communication skills are required to effectively convey technical information to both technical and non-technical audiences.
  - Technical fluency is essential for understanding and utilizing various technologies and tools.
  - Empathy is needed to understand and address the needs of customers and colleagues.
  - Humility is important for continuous learning and accepting feedback.
  - Collaborative skills are necessary for working effectively within a team environment.
  - Ability to adapt to changing priorities and requirements is crucial for success.

responsibilities[12]:
  - Collaborate with the team to deliver on Luminate's product roadmap using modern software development practices.
  - Develop all parts of the software stack, including test suites, infrastructure, and documentation.
  - Manage risk and uncertainty while expanding the platform to new markets and audiences.
  - Contribute to the engineering practice by sharing unique strengths and promoting continuous improvement.
  - Assemble large, complex datasets that meet both non-functional and functional business requirements.
  - Work with stakeholders, including data, design, and product teams, to assist them with data-related technical issues.
  - Participate in code reviews and provide constructive feedback to other engineers.
  - Write clean, well-documented, and testable code.
  - Troubleshoot and debug software issues.
  - Participate in the design and architecture of new features and systems.
  - Stay up-to-date with the latest technologies and trends in software development.
  - Contribute to the continuous improvement of development processes and tools.

tech_stack[10]:
  - Java
  - Spring Boot
  - React
  - Typescript
  - AWS
  - Microservices
  - CI/CD pipelines
  - REST APIs
  - Git
  - SQL

domain_expertise:
  industry[3]:
    - Music
    - Film
    - Television
  specific_knowledge[5]:
    - Entertainment data analysis
    - SaaS platform development
    - Data aggregation and processing
    - API design and implementation
    - Cloud computing (AWS)

implicit_requirements[8]:
  - Passion for entertainment industry
  - Strong problem-solving skills
  - Ability to work independently
  - Team player
  - Adaptability
  - Attention to detail
  - Proactive communication
  - Commitment to quality

company_culture_signals[8]:
  - Music fans and gamers
  - Data-driven decision making
  - Collaborative environment
  - Emphasis on continuous improvement
  - Employee well-being focus
  - Hybrid work model
  - Community involvement
  - Commitment to diversity and inclusion

ats_keywords[15]:
  - Software Engineer
  - Java
  - Spring Boot
  - React
  - Typescript
  - API design
  - Microservices
  - AWS
  - CI/CD
  - Test-driven development
  - SaaS
  - Data analysis
  - Entertainment industry
  - Hybrid work
  - New York
```

**TOON Token Count: ~800 tokens**

---

### Same Data in JSON Format
```json
{
  "company_name": "Luminate",
  "position_title": "Software Engineer",
  "location": "New York, NY",
  "work_mode": "hybrid",
  "salary_range": "$135,000 - $150,000",
  "experience_years_required": 2,
  "experience_level": "mid",
  "hard_skills_required": [
    {"skill": "Java", "priority": "critical"},
    {"skill": "Spring Boot", "priority": "critical"},
    {"skill": "React", "priority": "critical"},
    {"skill": "Typescript", "priority": "critical"},
    {"skill": "API design", "priority": "important"},
    {"skill": "Microservice architecture", "priority": "important"},
    {"skill": "Test-driven development", "priority": "important"},
    {"skill": "CI/CD", "priority": "important"},
    {"skill": "AWS", "priority": "nice"},
    {"skill": "Object-oriented design", "priority": "important"},
    {"skill": "SaaS platform development", "priority": "important"},
    {"skill": "Data aggregation and analysis", "priority": "important"},
    {"skill": "Software testing", "priority": "important"},
    {"skill": "Database management", "priority": "nice"}
  ],
  "soft_skills_required": [
    "Strong communication skills are required to effectively convey technical information to both technical and non-technical audiences.",
    "Technical fluency is essential for understanding and utilizing various technologies and tools.",
    "Empathy is needed to understand and address the needs of customers and colleagues.",
    "Humility is important for continuous learning and accepting feedback.",
    "Collaborative skills are necessary for working effectively within a team environment.",
    "Ability to adapt to changing priorities and requirements is crucial for success."
  ],
  "responsibilities": [
    "Collaborate with the team to deliver on Luminate's product roadmap using modern software development practices.",
    "Develop all parts of the software stack, including test suites, infrastructure, and documentation.",
    "Manage risk and uncertainty while expanding the platform to new markets and audiences.",
    "Contribute to the engineering practice by sharing unique strengths and promoting continuous improvement.",
    "Assemble large, complex datasets that meet both non-functional and functional business requirements.",
    "Work with stakeholders, including data, design, and product teams, to assist them with data-related technical issues.",
    "Participate in code reviews and provide constructive feedback to other engineers.",
    "Write clean, well-documented, and testable code.",
    "Troubleshoot and debug software issues.",
    "Participate in the design and architecture of new features and systems.",
    "Stay up-to-date with the latest technologies and trends in software development.",
    "Contribute to the continuous improvement of development processes and tools."
  ],
  "tech_stack": [
    "Java",
    "Spring Boot",
    "React",
    "Typescript",
    "AWS",
    "Microservices",
    "CI/CD pipelines",
    "REST APIs",
    "Git",
    "SQL"
  ],
  "domain_expertise": {
    "industry": [
      "Music",
      "Film",
      "Television"
    ],
    "specific_knowledge": [
      "Entertainment data analysis",
      "SaaS platform development",
      "Data aggregation and processing",
      "API design and implementation",
      "Cloud computing (AWS)"
    ]
  },
  "implicit_requirements": [
    "Passion for entertainment industry",
    "Strong problem-solving skills",
    "Ability to work independently",
    "Team player",
    "Adaptability",
    "Attention to detail",
    "Proactive communication",
    "Commitment to quality"
  ],
  "company_culture_signals": [
    "Music fans and gamers",
    "Data-driven decision making",
    "Collaborative environment",
    "Emphasis on continuous improvement",
    "Employee well-being focus",
    "Hybrid work model",
    "Community involvement",
    "Commitment to diversity and inclusion"
  ],
  "ats_keywords": [
    "Software Engineer",
    "Java",
    "Spring Boot",
    "React",
    "Typescript",
    "API design",
    "Microservices",
    "AWS",
    "CI/CD",
    "Test-driven development",
    "SaaS",
    "Data analysis",
    "Entertainment industry",
    "Hybrid work",
    "New York"
  ]
}
```

**JSON Token Count: ~1,500 tokens**

**Token Savings: ~46% reduction with TOON!**

---

## Performance Benchmarks

We tested TOON vs JSON across 4 popular LLM models. Here are the results:

### Speed Comparison

| Model | TOON Time | JSON Time | Time Saved | Improvement |
|-------|-----------|-----------|------------|-------------|
| **Gemini 2.0 Flash Lite** | 5.788s | 6.622s | 0.834s | **12.6% faster** |
| **GPT-3.5-Turbo** | 5.592s | 6.440s | 0.848s | **13.2% faster** |
| **Gemini 2.0 Flash (Full)** | 6.719s | 8.802s | 2.083s | **23.7% faster** 🏆 |
| **GPT-4o-Mini** | 19.452s | 21.722s | 2.270s | **10.5% faster** |
| **TOTAL (all 4 models)** | 37.551s | 43.586s | 6.035s | **13.8% faster** |

### Quality Comparison (Gemini 2.0 Flash Lite)

| Metric | TOON (Improved) | JSON | Status |
|--------|----------------|------|--------|
| Hard Skills Count | 14 | 14 | ✅ EQUAL |
| Soft Skills Count | 6 | 6 | ✅ EQUAL |
| Responsibilities Count | 12 | 12 | ✅ EQUAL |
| Priority Accuracy | ✅ Correct | ✅ Correct | ✅ EQUAL |
| Quality Score | 92/100 | 92/100 | ✅ EQUAL |

**Conclusion: TOON matches JSON quality while being 13.8% faster!**

---

## When to Use TOON

### ✅ TOON is Perfect For:

1. **LLM-based data extraction** (job descriptions, resumes, documents)
2. **High-volume API calls** where token costs matter
3. **Structured data with repeated patterns** (lists, tables, catalogs)
4. **Context window optimization** (fit more data in limited context)
5. **Prompt engineering** (cleaner examples, less noise)

### ❌ When NOT to Use TOON:

1. **Browser/client-side parsing** (use JSON for native support)
2. **Existing JSON APIs** (don't break compatibility)
3. **Data interchange with non-LLM systems** (stick with JSON)
4. **Complex nested data** with many levels (JSON is clearer)

---

## Implementation Tips

### 1. Use TOON in LLM Prompts

```python
prompt = f"""Extract job details and return in TOON format:

company_name: string
position_title: string
location: string

hard_skills_required[COUNT]{{skill,priority}}:
  skill_name,priority_level

JOB DESCRIPTION:
{job_description}
"""
```

### 2. Parse TOON Response Back to JSON

```python
def parse_toon_to_json(toon_text):
    # Use LLM to extract structured data
    # Or implement custom parser
    # Return JSON/dict
    pass
```

### 3. Optimize Your Prompts

**Key Guidelines:**
- Show exact count in brackets: `[12]` not `[...]`
- Declare object structure: `{skill,priority}`
- Use clear examples with realistic data
- Add extraction rules and quality checklist

---

## Cost Savings at Scale

### Example: Processing 10,000 Job Descriptions

**Assumptions:**
- Average job description: 500 tokens input
- TOON output: ~800 tokens
- JSON output: ~1,500 tokens
- Model: GPT-3.5-Turbo ($0.50/$1.50 per 1M tokens)

**TOON Cost:**
- Input: 10,000 × 500 = 5M tokens = $2.50
- Output: 10,000 × 800 = 8M tokens = $12.00
- **Total: $14.50**

**JSON Cost:**
- Input: 10,000 × 500 = 5M tokens = $2.50
- Output: 10,000 × 1,500 = 15M tokens = $22.50
- **Total: $25.00**

**Savings: $10.50 (42% cost reduction) + 16.8 hours saved!**

---

## Summary

TOON is a **token-optimized alternative to JSON** specifically designed for LLM applications:

✅ **40-50% fewer tokens** than JSON
✅ **13.8% faster** on average across models
✅ **Equal quality** to JSON (when properly prompted)
✅ **Human-readable** and easy to understand
✅ **Significant cost savings** at scale

**Best for:** LLM-based data extraction, high-volume API calls, context optimization

**Not for:** Browser apps, existing JSON APIs, non-LLM systems

---

## Resources

- **Implementation:** See `main.py` for full TOON extraction example
- **Quality Analysis:** See `TOON_IMPROVEMENTS.md` for prompt optimization guide
- **Benchmarks:** Run `docker-compose run --rm benchmark` to test yourself

**Questions?** TOON is a custom format created for this project. Adapt it to your needs!
