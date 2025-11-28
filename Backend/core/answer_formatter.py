"""
Answer Formatter Module

This module handles AI-powered formatting of user answers into professional CV/resume entries.
It detects the type of experience (project, job, course, etc.) and generates structured output
with bullet points, technologies, and metadata.
"""

import json
from typing import Optional
from pydantic import BaseModel
import google.generativeai as genai
import os

# Initialize Gemini client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class FormattedAnswer(BaseModel):
    """Structured CV entry with professional formatting - supports multiple entry types."""
    type: str  # "project" | "job" | "course" | "research" | "volunteer" | "publication" | "certification" | "award" | "conference" | "patent" | "other"
    name: str  # Generated name/title appropriate for the type
    description: Optional[str] = None  # 2-3 sentence description (15-30 words)

    # Common metadata (all types)
    duration: Optional[str] = None  # Timeframe (e.g., "3 months", "2 years")
    date: Optional[str] = None  # Specific date (e.g., "June 2024", "2023")
    bullet_points: list[str]  # 3-5 professional bullet points
    technologies: list[str]  # Tech stack, tools, or relevant technologies

    # Job-specific
    company: Optional[str] = None  # Company name for jobs
    team_size: Optional[str] = None  # Team size for projects/jobs

    # Course-specific
    provider: Optional[str] = None  # Education provider for courses
    skills_gained: Optional[list[str]] = None  # Skills learned from courses

    # Publication-specific
    publisher: Optional[str] = None  # Publisher/venue for publications
    authors: Optional[list[str]] = None  # Co-authors for publications/patents

    # Certification/Award-specific
    issuer: Optional[str] = None  # Issuing organization
    credential_id: Optional[str] = None  # Credential ID for certifications

    # Conference-specific
    venue: Optional[str] = None  # Conference/event venue

    # General
    url: Optional[str] = None  # Verification/reference URL
    raw_answer: str  # Original refined answer


def format_answer(
    question_text: str,
    answer_text: str,
    gap_info: dict,
    refinement_data: dict,
    language: str = "english"
) -> FormattedAnswer:
    """
    Format user answer into professional CV entry with AI.

    Args:
        question_text: The question that was asked
        answer_text: User's refined answer
        gap_info: {title, description} of the skill gap
        refinement_data: Additional details from refinement suggestions
        language: Target language for output

    Returns:
        FormattedAnswer object with type, name, bullet points, etc.
    """

    # Build formatting prompt
    prompt = build_formatting_prompt(
        question_text=question_text,
        answer_text=answer_text,
        gap_info=gap_info,
        refinement_data=refinement_data,
        language=language
    )

    # Call Gemini to format
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(prompt)

    # Extract JSON from response
    response_text = response.text.strip()

    # Remove markdown code blocks if present
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    # Parse JSON
    formatted_data = json.loads(response_text)

    # Add raw answer
    formatted_data['raw_answer'] = answer_text

    # Create FormattedAnswer object
    return FormattedAnswer(**formatted_data)


def build_formatting_prompt(
    question_text: str,
    answer_text: str,
    gap_info: dict,
    refinement_data: dict,
    language: str
) -> str:
    """Build the AI prompt for answer formatting."""

    # Format refinement data for display
    refinement_details = "\n".join([
        f"- {key}: {value}" for key, value in refinement_data.items()
    ])

    prompt = f"""You are a professional resume writer. Format the following answer into a structured CV entry.

**CRITICAL: NEVER INVENT INFORMATION**
- Only use facts explicitly stated in the user's answer and refinement data below
- If metrics aren't provided, don't add them
- If technologies aren't mentioned, don't guess them
- If timeline isn't clear, leave duration empty
- When in doubt, be conservative - omit rather than invent
- DO NOT convert vague terms like "significantly" or "many" into specific numbers

**Question Context:**
Gap: {gap_info.get('title', 'N/A')}
Description: {gap_info.get('description', 'N/A')}

**Question Asked:**
{question_text}

**User's Answer:**
{answer_text}

**Additional Details Provided:**
{refinement_details}

**Your Task:**
1. **Detect the type** of experience from the question and answer:
   - **project**: Building/developing something (app, system, tool, chatbot, website, etc.)
   - **job**: Work experience at a company, professional role, internship
   - **course**: Educational content, online course, bootcamp, training
   - **research**: Academic research, studies, thesis (NOT published papers - those are publications)
   - **volunteer**: Non-profit work, community service, open source contribution
   - **publication**: Published papers, articles, blog posts, technical writing (keywords: "published", "paper", "article", "wrote", "author")
   - **certification**: Professional certifications, licenses, credentials (keywords: "certified", "certification", "license", "credential", "exam")
   - **award**: Honors, achievements, recognitions, competition wins (keywords: "won", "awarded", "recognized", "prize", "hackathon", "competition")
   - **conference**: Speaking engagements, presentations, talks (keywords: "presented", "spoke at", "talk", "speaker", "conference")
   - **patent**: Intellectual property, inventions (keywords: "patent", "invention", "filed", "intellectual property")
   - **other**: General experience that doesn't fit above categories

2. **Generate an appropriate name/title** based on the type:
   - **Projects** → Descriptive project name (e.g., "Customer Service Chatbot")
   - **Jobs** → Role title (e.g., "Machine Learning Engineer")
   - **Courses** → Course name (e.g., "Advanced LLM Development")
   - **Research** → Research topic/thesis title
   - **Volunteer** → Volunteer role/contribution description
   - **Publications** → Paper/article title based on topic
   - **Certifications** → Official certification name (e.g., "AWS Solutions Architect - Professional")
   - **Awards** → Award name + event (e.g., "First Place - TechCon 2024 Hackathon")
   - **Conferences** → Talk/presentation title + event
   - **Patents** → Patent/invention title
   - Keep names generic if user didn't provide specific details

3. **Format into 3-5 professional bullet points**:
   - Start with strong action verbs (Built, Developed, Implemented, Achieved, Led, Designed, Created, Engineered)
   - Include ONLY technologies, frameworks, and tools explicitly mentioned by the user
   - Include ONLY quantifiable metrics that were explicitly provided in the answer or refinement data
   - If no metrics provided, describe the achievement without inventing numbers
   - Keep each bullet to 12-18 words
   - Use professional, ATS-friendly language
   - Before writing each bullet, verify: Can I find this fact in the user's input?

4. **Extract metadata** (ONLY from user's explicit statements):
   - **description**: 2-3 sentence summary (15-30 words) based ONLY on what user said - no invented metrics or details
   - **technologies**: List ONLY tech mentioned by user (don't guess or add related technologies)
   - **duration**: Timeframe if user stated it (e.g., "3 months", "6 weeks") - leave empty if not mentioned
   - **date**: Specific date if mentioned (e.g., "June 2024", "March 2024") - for publications, certifications, awards
   - **company**: For jobs ONLY if user mentioned company name
   - **team_size**: For projects/jobs ONLY if user mentioned it (e.g., "Solo project", "Team of 5")
   - **provider**: For courses ONLY if user mentioned platform/institution
   - **skills_gained**: For courses ONLY if user explicitly listed skills learned
   - **publisher**: For publications ONLY if user mentioned journal/conference/platform
   - **authors**: For publications/patents ONLY if user listed co-authors (array of names)
   - **issuer**: For certifications/awards ONLY if user mentioned issuing organization
   - **credential_id**: For certifications ONLY if user provided credential/license number
   - **venue**: For conferences ONLY if user mentioned event/conference name
   - **url**: ONLY if user provided a verification/reference link

**CRITICAL Output Format (JSON):**
{{
  "type": "project|job|course|research|volunteer|publication|certification|award|conference|patent|other",
  "name": "Professional name/title (required)",
  "description": "2-3 sentence summary (15-30 words) based on user's actual statements - NO invented details",

  "duration": "Timeframe (optional)",
  "date": "Specific date for publications/certifications/awards (optional)",
  "bullet_points": [
    "Action verb + specific technical details + quantifiable impact (ONLY if user provided metrics)",
    "Another achievement with technologies mentioned by user",
    "Third accomplishment based on user's actual statements"
  ],
  "technologies": ["Tech1", "Tech2"],

  "company": "Company name (jobs only, optional)",
  "team_size": "Solo|2-3 people|5+ team (projects/jobs only, optional)",
  "provider": "Education provider (courses only, optional)",
  "skills_gained": ["Skill1", "Skill2"] (courses only, optional)",
  "publisher": "Journal/conference/platform (publications only, optional)",
  "authors": ["Author1", "Author2"] (publications/patents only, optional)",
  "issuer": "Issuing organization (certifications/awards only, optional)",
  "credential_id": "Credential number (certifications only, optional)",
  "venue": "Event/conference name (conferences only, optional)",
  "url": "Verification link (optional)"
}}

**Example 1: Project WITH detailed metrics provided by user**
User answer: "I built a chatbot using GPT-4 and LangChain for customer service"
Refinement data:
- metrics: "Reduced response time from 12 minutes to 38 seconds, handled 250+ daily queries"
- timeline: "3 months"

Output:
{{
  "type": "project",
  "name": "Customer Service Chatbot",
  "description": "Developed an AI-powered chatbot using GPT-4 and LangChain to handle customer service inquiries and reduce response times for support operations.",
  "duration": "3 months",
  "bullet_points": [
    "Built customer service chatbot using OpenAI's GPT-4 API and LangChain framework",
    "Reduced average response time from 12 minutes to 38 seconds for customer inquiries",
    "Handled 250+ daily customer queries using conversational AI technology"
  ],
  "technologies": ["GPT-4", "LangChain"],
  "team_size": "Solo project"
}}

**Example 2: Project WITHOUT specific metrics (minimal user input)**
User answer: "I built a chatbot for customer service using AI. It reduced response time significantly."
Refinement data: (empty or minimal)

Output:
{{
  "type": "project",
  "name": "AI Customer Service Chatbot",
  "description": "Created an AI-powered chatbot system to handle customer service inquiries and improve response times for support requests.",
  "duration": "",
  "bullet_points": [
    "Developed AI-powered chatbot to handle customer service inquiries",
    "Implemented conversational AI to improve response time for support requests",
    "Created automated system to assist with customer support operations"
  ],
  "technologies": ["AI"],
  "team_size": ""
}}

**Example 3: Job WITH metrics (user provided specific details)**
User answer: "I worked as an ML Engineer at Tech Startup building chatbots"
Refinement data:
- metrics: "Processed 250+ daily queries, reduced response time from 12 min to 38 sec"
- company: "Tech Startup Inc."
- timeline: "Jan 2023 - Present"

Output:
{{
  "type": "job",
  "name": "Machine Learning Engineer",
  "description": "Worked as an ML Engineer building customer service chatbot solutions using GPT-4 and cloud infrastructure to improve support operations.",
  "company": "Tech Startup Inc.",
  "duration": "Jan 2023 - Present",
  "bullet_points": [
    "Developed customer service chatbot using GPT-4 API to handle customer queries",
    "Reduced average response time from 12 minutes to 38 seconds for support tickets",
    "Processed 250+ daily customer queries using conversational AI technology"
  ],
  "technologies": ["GPT-4"]
}}

**Example 4: Job WITHOUT metrics (minimal user input)**
User answer: "I worked as a software developer building chatbots with AI"
Refinement data: (minimal)

Output:
{{
  "type": "job",
  "name": "Software Developer",
  "description": "Worked as a software developer building AI-powered chatbot applications to improve customer service and support operations.",
  "company": "",
  "duration": "",
  "bullet_points": [
    "Developed AI-powered chatbot applications for customer service",
    "Built conversational AI solutions to assist with support operations",
    "Implemented chatbot technology to improve customer interactions"
  ],
  "technologies": ["AI"]
}}

**Example 5: Course WITH specific projects (user provided details)**
User answer: "I took a course on LLM development and built several chatbot projects"
Refinement data:
- provider: "Coursera"
- timeline: "8 weeks"
- projects: "Built 3 chatbot applications using GPT-4 and LangChain"

Output:
{{
  "type": "course",
  "name": "Advanced LLM Application Development",
  "description": "Completed an 8-week course on building LLM applications, focusing on chatbot development using GPT-4 and LangChain frameworks.",
  "provider": "Coursera",
  "duration": "8 weeks",
  "bullet_points": [
    "Built 3 chatbot applications using GPT-4 and LangChain frameworks",
    "Learned LLM integration techniques for conversational AI development",
    "Developed practical projects implementing chatbot solutions"
  ],
  "technologies": ["GPT-4", "LangChain"],
  "skills_gained": ["LLM Integration", "Chatbot Development"]
}}

**Example 6: Course WITHOUT specific projects (minimal user input)**
User answer: "I completed a course on LLM and AI"
Refinement data: (minimal)

Output:
{{
  "type": "course",
  "name": "LLM and AI Development Course",
  "description": "Completed coursework on large language models and AI development, focusing on conversational AI and chatbot technologies.",
  "provider": "",
  "duration": "",
  "bullet_points": [
    "Studied large language model concepts and AI development techniques",
    "Learned about conversational AI and chatbot implementation",
    "Completed coursework on LLM application development"
  ],
  "technologies": ["LLM", "AI"],
  "skills_gained": ["AI Development", "LLM Concepts"]
}}

**Example 7: Publication (user published a paper)**
User answer: "I published a research paper on LLM optimization"
Refinement data:
- publisher: "ACL 2024 Conference"
- date: "June 2024"

Output:
{{
  "type": "publication",
  "name": "Research on LLM Optimization Techniques",
  "description": "Published research paper on optimizing large language models for production deployment at ACL 2024, focusing on inference speed improvements.",
  "publisher": "ACL 2024 Conference",
  "date": "June 2024",
  "bullet_points": [
    "Published research on LLM optimization techniques at ACL 2024 conference",
    "Presented findings on improving inference speed for production systems",
    "Contributed to academic knowledge on large language model deployment"
  ],
  "technologies": ["LLM"]
}}

**Example 8: Certification (user earned a professional certification)**
User answer: "I got AWS Solutions Architect certification"
Refinement data:
- issuer: "Amazon Web Services"
- credential_id: "AWS-SA-123456"
- date: "March 2024"

Output:
{{
  "type": "certification",
  "name": "AWS Certified Solutions Architect - Professional",
  "description": "Earned AWS Solutions Architect Professional certification, demonstrating expertise in designing and deploying scalable, fault-tolerant systems on AWS cloud platform.",
  "issuer": "Amazon Web Services",
  "credential_id": "AWS-SA-123456",
  "date": "March 2024",
  "bullet_points": [
    "Achieved AWS Solutions Architect Professional certification",
    "Demonstrated expertise in cloud architecture and system design",
    "Validated skills in deploying scalable applications on AWS infrastructure"
  ],
  "technologies": ["AWS"]
}}

**Example 9: Award (user won a competition or received recognition)**
User answer: "I won first place in a hackathon for building an AI chatbot"
Refinement data:
- issuer: "TechCon 2024"
- date: "February 2024"
- project: "Built AI customer service chatbot in 24 hours"

Output:
{{
  "type": "award",
  "name": "First Place - TechCon 2024 Hackathon",
  "description": "Won first place at TechCon 2024 hackathon for developing an innovative AI-powered customer service chatbot within 24-hour timeframe.",
  "issuer": "TechCon 2024",
  "date": "February 2024",
  "bullet_points": [
    "Won first place in TechCon 2024 hackathon competition",
    "Built AI-powered customer service chatbot in 24-hour timeframe",
    "Demonstrated rapid prototyping and AI development skills"
  ],
  "technologies": ["AI"]
}}

**Important Guidelines**:
- Analyze the question and answer carefully for type detection:
  - "experience", "worked at", "role" → likely a **job**
  - "built", "developed", "created" → likely a **project**
  - "course", "learned", "studied" → likely a **course**
  - "published", "paper", "article" → likely a **publication**
  - "certified", "certification", "exam" → likely a **certification**
  - "won", "awarded", "prize", "hackathon" → likely an **award**
  - "presented", "spoke at", "talk" → likely a **conference**
  - "patent", "filed", "invention" → likely a **patent**
- Use the gap context to help determine type
- Extract exact technologies mentioned - don't invent new ones
- Keep bullet points concise (12-18 words) but information-dense
- Include specific numbers ONLY when user provided them in the details
- Make the name/title professional and searchable
- Leave optional fields empty if user didn't provide that information

Language: {language}

Output only valid JSON, no additional text.
"""

    return prompt
