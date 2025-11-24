export interface SampleResume {
  id: string
  name: string
  category: 'technical' | 'transition'
  experience: string
  content: string
}

export const SAMPLE_RESUMES: Record<string, SampleResume> = {
  fullstack: {
    id: 'fullstack',
    name: 'Full-Stack Engineer (5 yrs)',
    category: 'technical',
    experience: '5 years',
    content: `JOHN DOE
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
  },

  intern: {
    id: 'intern',
    name: 'Student Seeking Internship',
    category: 'technical',
    experience: '0-1 years',
    content: `EMILY CHEN
Computer Science Student

Email: emily.chen@university.edu | Phone: (555) 234-5678 | Location: Boston, MA
LinkedIn: linkedin.com/in/emilychen | GitHub: github.com/emilychen
Portfolio: emilychen.dev

EDUCATION
Bachelor of Science in Computer Science
Massachusetts Institute of Technology | Expected Graduation: May 2025
GPA: 3.8/4.0
Relevant Coursework: Data Structures, Algorithms, Web Development, Database Systems, Machine Learning

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, Java, C++
Web Development: React, HTML5, CSS3, Node.js, Express
Databases: PostgreSQL, MongoDB
Tools & Technologies: Git, GitHub, VS Code, Jupyter Notebook, Postman
Concepts: Object-Oriented Programming, RESTful APIs, Agile Development

INTERNSHIP EXPERIENCE
Software Engineering Intern | TechCorp
Boston, MA | Summer 2024 (3 months)
- Developed internal dashboard using React and Node.js for tracking project metrics
- Fixed 15+ bugs in production codebase and improved test coverage by 20%
- Participated in code reviews and daily standup meetings with engineering team
- Collaborated with senior engineers to implement new features using Agile methodology

ACADEMIC PROJECTS

Course Registration System
Fall 2024 | Python, Flask, PostgreSQL
- Built full-stack web application allowing students to browse and register for courses
- Implemented user authentication, search functionality, and enrollment system
- Managed PostgreSQL database with 10+ tables and complex relationships
- Deployed application on Heroku with CI/CD pipeline

Weather Dashboard App
Spring 2024 | React, JavaScript, OpenWeatherMap API
- Created responsive weather application fetching real-time data from external API
- Implemented location search, 5-day forecast, and favorite cities feature
- Designed clean UI/UX with mobile-first approach using CSS Grid and Flexbox

Task Manager CLI Tool
Fall 2023 | Python, SQLite
- Developed command-line task management application with CRUD operations
- Used SQLite for data persistence and implemented task prioritization
- Applied object-oriented programming principles and unit testing

HACKATHONS & COMPETITIONS

MIT HackMIT 2024 | 1st Place - Education Track
- Built AI-powered study buddy app using React Native and OpenAI API
- Implemented spaced repetition algorithm for optimized learning
- Presented to 500+ attendees and judges

Boston College Hackathon 2023 | Participant
- Created social networking platform for college students in 24 hours
- Worked with team of 4 using Git for version control and collaboration

LEADERSHIP & ACTIVITIES
- Vice President, MIT Computer Science Society (2024-Present)
- Member, Women in Computer Science (WiCS) (2023-Present)
- Volunteer Coding Tutor, Local High School (2023-2024)

CERTIFICATIONS & COURSES
- Completed Harvard CS50: Introduction to Computer Science (Online)
- freeCodeCamp Responsive Web Design Certification (2023)`
  },

  uxdesigner: {
    id: 'uxdesigner',
    name: 'Junior UX Designer (1-2 yrs)',
    category: 'technical',
    experience: '1-2 years',
    content: `SOPHIA MARTINEZ
UX/UI Designer

Email: sophia.martinez@email.com | Phone: (555) 345-6789 | Location: Austin, TX
LinkedIn: linkedin.com/in/sophiamartinez | Portfolio: sophiamartinez.design
Behance: behance.net/sophiamartinez

PROFESSIONAL SUMMARY
Creative UX/UI Designer with 2 years of experience designing user-centered digital products. Passionate about creating intuitive interfaces that solve real user problems. Strong background in user research, wireframing, prototyping, and design systems. Eager to explore product management and design engineering roles.

DESIGN SKILLS
Design Tools: Figma, Adobe XD, Sketch, Adobe Photoshop, Adobe Illustrator
Prototyping: Figma, Framer, InVision, Principle
Research: User Interviews, Usability Testing, A/B Testing, Surveys, Personas, Journey Mapping
Front-end: HTML5, CSS3, JavaScript basics, Tailwind CSS, Framer Motion
Collaboration: Jira, Confluence, Miro, FigJam, Notion

WORK EXPERIENCE

UX/UI Designer | Digital Agency Co.
Austin, TX | Mar 2023 - Present
- Design user interfaces for 10+ client projects including mobile apps and web applications
- Conduct user research through interviews, surveys, and usability testing with 50+ participants
- Create wireframes, high-fidelity mockups, and interactive prototypes using Figma
- Collaborate with developers to ensure design implementation matches specifications
- Established design system with 30+ reusable components reducing design time by 40%
- Present design concepts to stakeholders and iterate based on feedback

Junior UX Designer | StartupXYZ
Austin, TX | Jun 2022 - Feb 2023
- Redesigned onboarding flow increasing user activation rate by 35%
- Created responsive designs for web and mobile platforms (iOS and Android)
- Conducted competitive analysis and user testing sessions
- Worked closely with product managers to define features and requirements
- Maintained design documentation and style guides

EDUCATION
Bachelor of Fine Arts in Graphic Design
University of Texas at Austin | Graduated: May 2022
Minor: Human-Computer Interaction
GPA: 3.6/4.0

PROJECTS & CASE STUDIES

HealthTrack App - Redesign (Personal Project)
- Redesigned health tracking mobile app improving user retention by 25%
- Conducted user research with 20 participants to identify pain points
- Created user personas, user flows, wireframes, and high-fidelity prototypes
- Implemented accessibility best practices (WCAG 2.1 AA compliance)

E-Commerce Checkout Optimization
- Redesigned checkout process reducing cart abandonment by 30%
- Performed A/B testing comparing 3 different design variations
- Collaborated with front-end developers to implement final design
- Measured success with analytics and user feedback

TECHNICAL SKILLS
- Basic HTML/CSS: Can implement simple designs and collaborate effectively with developers
- Framer: Built interactive prototypes and simple websites with no-code tools
- Responsive Design: Mobile-first approach, understanding of breakpoints and adaptive layouts
- Design Tokens: Experience with design-to-development handoff using tokens and variables

CERTIFICATIONS & COURSES
- Google UX Design Professional Certificate (Coursera, 2022)
- Interaction Design Foundation - User Research Methods (2023)
- Frontend Fundamentals: HTML & CSS (Codecademy, 2024)

ACHIEVEMENTS
- Dribbble Featured Designer (Top 10% in Austin, 2024)
- Won "Best User Experience" Award at University Design Competition (2022)
- Published 2 design articles on Medium with 5K+ combined reads`
  },

  logistics: {
    id: 'logistics',
    name: 'Logistics Coordinator (3-4 yrs)',
    category: 'transition',
    experience: '3-4 years',
    content: `MARCUS JOHNSON
Logistics Coordinator

Email: marcus.johnson@email.com | Phone: (555) 456-7890 | Location: Chicago, IL
LinkedIn: linkedin.com/in/marcusjohnson

PROFESSIONAL SUMMARY
Detail-oriented Logistics Coordinator with 4 years of experience in supply chain management, inventory control, and warehouse operations. Proven track record of optimizing logistics processes, reducing costs, and improving efficiency through data analysis and technology adoption. Strong proficiency in SAP, Excel, and logistics software systems.

TECHNICAL SKILLS
Logistics Software: SAP S/4HANA, Oracle Transportation Management, Manhattan WMS
Data Analysis: Microsoft Excel (Advanced: VLOOKUP, Pivot Tables, Macros), Power BI, SQL basics
Inventory Management: Barcode scanning systems, RFID tracking, Inventory optimization
Tools: Microsoft Office Suite, Google Workspace, Slack, Asana
Systems: ERP systems, Transportation Management Systems (TMS), Warehouse Management Systems (WMS)

WORK EXPERIENCE

Senior Logistics Coordinator | Global Supply Chain Inc.
Chicago, IL | Jan 2022 - Present
- Manage end-to-end logistics operations for 200+ daily shipments across North America
- Optimize transportation routes using data analysis reducing shipping costs by 18%
- Coordinate with 50+ vendors and carriers to ensure on-time delivery (98% success rate)
- Implemented new inventory tracking system improving accuracy from 92% to 99%
- Created Excel dashboards and Power BI reports for real-time shipment tracking
- Train team of 5 junior coordinators on SAP system and best practices
- Analyze logistics data to identify trends and cost-saving opportunities

Logistics Coordinator | Regional Distribution Center
Chicago, IL | Mar 2021 - Dec 2021
- Coordinated inbound and outbound shipments for warehouse serving 30+ retail locations
- Processed 500+ shipping orders weekly using warehouse management system
- Maintained inventory accuracy through regular cycle counts and audits
- Collaborated with warehouse staff to optimize picking and packing processes
- Generated weekly reports on inventory levels, shipment status, and performance metrics
- Resolved shipping discrepancies and customer delivery issues

Warehouse Associate | Fulfillment Solutions LLC
Chicago, IL | Jun 2020 - Feb 2021
- Operated warehouse management software for order processing and inventory control
- Performed data entry and maintained accurate records in company database
- Assisted in implementing new barcode scanning system across warehouse
- Participated in process improvement initiatives reducing order errors by 25%

EDUCATION
Bachelor of Science in Business Administration
University of Illinois at Chicago | Graduated: May 2020
Concentration: Supply Chain Management
GPA: 3.4/4.0

CERTIFICATIONS & TRAINING
- Certified Supply Chain Professional (CSCP) - In Progress (Expected: 2025)
- SAP S/4HANA Logistics Certification (2023)
- OSHA Forklift Operator Certification (2020)
- Power BI Data Analysis Fundamentals (Microsoft, 2024)
- SQL for Data Analysis (Online Course - Udemy, 2024)

KEY ACHIEVEMENTS
- Reduced shipping errors by 40% through process improvements and staff training
- Saved company $150K annually by optimizing carrier contracts and route planning
- Implemented automated inventory alert system reducing stockouts by 60%
- Led cross-functional project to integrate new TMS with existing ERP system
- Achieved 99.5% on-time delivery rate for 12 consecutive months

TECHNICAL PROJECTS
Supply Chain Data Dashboard (Personal Project)
- Built interactive Power BI dashboard tracking KPIs (delivery times, costs, inventory turnover)
- Automated data extraction from SAP using Excel macros
- Presented insights to management leading to operational improvements

Inventory Optimization Analysis
- Analyzed 2 years of historical data to identify slow-moving inventory
- Created Excel model predicting optimal stock levels reducing carrying costs by 20%
- Used statistical analysis to forecast demand and prevent stockouts`
  },

  healthcare: {
    id: 'healthcare',
    name: 'Medical Professional (2-3 yrs)',
    category: 'transition',
    experience: '2-3 years',
    content: `RACHEL THOMPSON, RN
Registered Nurse

Email: rachel.thompson@email.com | Phone: (555) 567-8901 | Location: Seattle, WA
LinkedIn: linkedin.com/in/rachelthompson

PROFESSIONAL SUMMARY
Compassionate Registered Nurse with 3 years of clinical experience in patient care and healthcare technology. Proficient in Electronic Health Records (EHR) systems, medical data management, and healthcare software. Strong interest in healthcare technology and improving patient outcomes through data-driven solutions. Seeking opportunities to transition into HealthTech, clinical informatics, or healthcare data analysis.

CLINICAL SKILLS
Patient Care: Patient Assessment, Medication Administration, IV Therapy, Wound Care, Vital Signs Monitoring
Specialties: Medical-Surgical Nursing, Emergency Care, Patient Education
Clinical Documentation: Comprehensive charting, Care plans, Patient histories

TECHNICAL SKILLS
EHR Systems: Epic (Certified), Cerner, Meditech, Allscripts
Medical Software: CPOE (Computerized Physician Order Entry), eMar, Clinical Documentation Systems
Data Management: Microsoft Excel (Intermediate), Medical databases, Patient data analysis
Healthcare Tools: Telehealth platforms (Zoom for Healthcare, Doxy.me), Medical devices with digital interfaces
Computer Skills: Microsoft Office Suite, Google Workspace, Data entry and management

WORK EXPERIENCE

Registered Nurse | Seattle Medical Center
Seattle, WA | Jun 2022 - Present
- Provide direct patient care for 6-8 patients per shift in medical-surgical unit
- Utilize Epic EHR system for patient charting, medication orders, and care coordination
- Collaborate with interdisciplinary team to develop patient care plans
- Serve as Epic EHR "Super User" providing training and support to 15+ nursing staff
- Identify and report software bugs and workflow inefficiencies to IT department
- Participated in hospital's EHR upgrade project testing new features and providing feedback
- Analyze patient data trends to identify early warning signs and prevent complications
- Achieved 98% medication administration accuracy rate through systematic double-checking

Registered Nurse | Community Hospital
Seattle, WA | Aug 2021 - May 2022
- Delivered patient care in emergency department handling 20+ patients per shift
- Documented patient assessments, treatments, and outcomes in Cerner EHR system
- Assisted in transition from paper charting to electronic documentation
- Created standardized templates for common patient scenarios improving charting efficiency
- Educated patients and families on discharge instructions and medication management

EDUCATION
Bachelor of Science in Nursing (BSN)
University of Washington | Graduated: May 2021
GPA: 3.7/4.0
Dean's List: All semesters

LICENSES & CERTIFICATIONS
- Registered Nurse (RN) License - Washington State Board of Nursing (Active)
- Epic EHR Certification - Inpatient Clinical (2023)
- Basic Life Support (BLS) - American Heart Association (Current)
- Advanced Cardiovascular Life Support (ACLS) - American Heart Association (Current)
- Healthcare Data Analytics Certificate (Online - Coursera, 2024)

HEALTHCARE TECHNOLOGY EXPERIENCE

EHR Implementation Project - Epic Upgrade
Seattle Medical Center | 2024
- Served on hospital committee testing Epic EHR upgrade affecting 500+ users
- Provided clinical workflow feedback during software configuration
- Created training materials and quick reference guides for nursing staff
- Conducted user acceptance testing identifying 20+ usability issues before go-live
- Trained 30+ nurses on new EHR features and best practices

Clinical Data Quality Improvement Initiative
Seattle Medical Center | 2023
- Analyzed 6 months of patient charting data to identify documentation gaps
- Created Excel reports highlighting common errors and missing data fields
- Developed standardized workflows improving documentation completeness by 35%
- Presented findings to nursing leadership with actionable recommendations

ADDITIONAL SKILLS & INTERESTS
- Strong analytical mindset with interest in healthcare data analysis and outcomes improvement
- Experience with telehealth platforms and remote patient monitoring systems
- Understanding of HIPAA compliance and patient data privacy requirements
- Familiarity with HL7 data standards and healthcare interoperability concepts
- Self-taught SQL basics through online courses (DataCamp, 2024)
- Interest in clinical decision support systems and evidence-based practice

PROFESSIONAL DEVELOPMENT
- Attended Healthcare IT Conference (HIMSS) - 2024
- Completed "Introduction to Python for Healthcare" online course (2024)
- Member, American Medical Informatics Association (AMIA) - 2024
- Volunteer, Hospital's Innovation Committee exploring new health technologies

AWARDS & RECOGNITION
- Epic Super User of the Quarter (Q3 2024)
- Nursing Excellence Award for Technology Adoption (2023)
- Employee of the Month - June 2023`
  },

  lawyer: {
    id: 'lawyer',
    name: 'Lawyer (3-5 yrs)',
    category: 'transition',
    experience: '3-5 years',
    content: `DAVID ROBINSON, ESQ.
Attorney at Law

Email: david.robinson@lawfirm.com | Phone: (555) 678-9012 | Location: New York, NY
LinkedIn: linkedin.com/in/davidrobinson

PROFESSIONAL SUMMARY
Results-driven Attorney with 4 years of experience in corporate law, contract negotiation, and legal research. Extensive experience with legal technology platforms, document automation, and e-discovery tools. Strong analytical skills with a proven track record of streamlining legal processes through technology adoption. Interested in exploring opportunities in LegalTech, compliance, and legal operations.

LEGAL EXPERTISE
Practice Areas: Corporate Law, Contract Law, Mergers & Acquisitions, Compliance, Corporate Governance
Legal Skills: Legal Research, Contract Drafting & Review, Due Diligence, Risk Assessment, Regulatory Compliance
Litigation: Legal Brief Writing, Motion Practice, Discovery, Deposition (Limited experience)

TECHNOLOGY SKILLS
Legal Research Platforms: LexisNexis, Westlaw, Bloomberg Law, Fastcase
Document Management: iManage, NetDocuments, SharePoint, Clio
Contract Tools: ContractWorks, Ironclad, DocuSign CLM, PandaDoc
E-Discovery: Relativity, Everlaw, Logikcull
Document Automation: HotDocs, Contract Express, Smokeball
Practice Management: Clio Manage, MyCase, PracticePanther
Data Analysis: Microsoft Excel (Advanced), Tableau (Basic), SQL (Learning)
General: Microsoft Office Suite (Word, Excel, PowerPoint), Adobe Acrobat Pro, Google Workspace

WORK EXPERIENCE

Associate Attorney | Parker & Associates LLP
New York, NY | Sep 2021 - Present
- Draft and negotiate commercial contracts, SaaS agreements, and vendor contracts ($50M+ total value)
- Conduct legal research using LexisNexis and Westlaw on corporate and regulatory matters
- Manage contract lifecycle using Ironclad contract management system
- Perform due diligence for M&A transactions using virtual data rooms and document review platforms
- Implemented contract template system reducing drafting time by 50%
- Created automated contract review checklist using Microsoft Excel macros
- Advise clients on regulatory compliance including GDPR, CCPA, and data privacy laws
- Lead firm's LegalTech committee evaluating new software tools and AI solutions
- Train junior associates and paralegals on legal technology best practices

Junior Associate | Morrison Law Firm
New York, NY | Jun 2020 - Aug 2021
- Assisted senior attorneys with contract review, legal research, and client communication
- Managed document organization using iManage document management system
- Conducted legal research and prepared memoranda on various corporate law issues
- Reviewed and analyzed 500+ contracts during M&A due diligence processes
- Utilized e-discovery platform (Relativity) for document review in litigation matters
- Created Excel tracking systems for matter management and deadline monitoring

EDUCATION
Juris Doctor (J.D.)
Columbia Law School | Graduated: May 2020
Activities: Technology & Law Society, Moot Court Competition

Bachelor of Arts in Political Science
Yale University | Graduated: May 2017
GPA: 3.8/4.0, Magna Cum Laude

BAR ADMISSIONS
- New York State Bar (Admitted: 2020)
- United States District Court, Southern District of New York (Admitted: 2021)

LEGAL TECHNOLOGY EXPERIENCE

Contract Automation Project
Parker & Associates LLP | 2023-2024
- Led initiative to automate routine contract generation using HotDocs
- Created 15+ contract templates reducing drafting time from 4 hours to 30 minutes
- Developed workflow automation for contract approval process
- Trained 20+ attorneys on new contract automation system
- Saved firm estimated 200+ billable hours annually

AI-Powered Legal Research Pilot
Parker & Associates LLP | 2024
- Evaluated AI legal research tools (CoCounsel, Harvey.ai) for firm adoption
- Conducted comparative analysis of traditional vs. AI-assisted research methods
- Created best practices guide for using generative AI in legal work
- Presented findings to firm's management committee

TECHNICAL SKILLS DEVELOPMENT
- Completed "LegalTech Fundamentals" certification (LegalTech Hub, 2024)
- Self-taught Python basics for legal document analysis (Online - 2024)
- Learned SQL for contract database analysis (DataCamp, 2024)
- Attended LegalTech conferences: LegalWeek NYC (2023, 2024), CodeX FutureLaw (2024)

PUBLICATIONS & SPEAKING
- Article: "The Future of Contract Management: AI and Automation" - Law Technology Today (2024)
- Panelist: "LegalTech for Young Lawyers" - New York State Bar Association CLE (2024)
- Blog contributor: Writing about legal technology trends and practical applications

PROFESSIONAL AFFILIATIONS
- American Bar Association (ABA) - Member, Law Practice Division
- Legal Tech Association of New York - Member
- Association of Corporate Counsel (ACC) - Associate Member
- Legal Innovators Roundtable - Participant (2024)

AWARDS & RECOGNITION
- "Rising Star" in LegalTech - New York Legal Tech Awards (Nominated, 2024)
- Firm Innovation Award for Contract Automation Project (2024)
- Pro Bono Service Award - 100+ hours annually (2021-2024)`
  }
}
