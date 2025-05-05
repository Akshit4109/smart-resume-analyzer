from flask import Flask, render_template, request, jsonify
import PyPDF2
import os
import re

app = Flask(__name__)

# Mapping of job roles to relevant skills
job_role_skills = {
    "Software Engineer": ["Python", "Java", "C++", "SQL", "Git", "Data Structures", "Algorithms", "Cloud Computing", "REST APIs", "Agile Development", "Software Testing"],
    "Front-end Developer": ["JavaScript", "HTML", "CSS", "React", "Vue.js", "Angular", "UI/UX", "TypeScript", "SASS", "Bootstrap", "Web Performance Optimization"],
    "Back-end Developer": ["Python", "Node.js", "Django", "Flask", "SQL", "MongoDB", "API", "Java", "Ruby on Rails", "GraphQL", "Microservices Architecture"],
    "Full-Stack Developer": ["JavaScript", "React", "Node.js", "MongoDB", "SQL", "Docker", "TypeScript", "Express.js", "REST APIs", "Authentication", "DevOps"],
    "Quality Assurance (QA) Engineer": ["Selenium", "JUnit", "Test Automation", "Python", "Bug Tracking", "TestNG", "CI/CD", "API Testing", "Performance Testing", "Load Testing"],
    "Data Scientist": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "Data Analysis", "R", "Big Data", "Data Visualization", "Hadoop", "SQL"],
    "Database Administrator": ["SQL", "MySQL", "PostgreSQL", "MongoDB", "OracleDB", "Database Optimization", "Backup and Recovery", "NoSQL", "Replication", "Sharding"],
    "DevOps Engineer": ["Docker", "Kubernetes", "CI/CD", "AWS", "Terraform", "Bash", "Jenkins", "Ansible", "Linux", "Cloud Infrastructure"],
    "User Experience (UX) Designer": ["Figma", "Adobe XD", "Wireframing", "User Research", "UI Design", "Prototyping", "Interaction Design", "Usability Testing", "Sketch", "Design Systems"],
    "Cloud Engineer": ["AWS", "Azure", "Google Cloud", "Terraform", "Kubernetes", "CI/CD", "Cloud Security", "Infrastructure as Code", "Linux", "Containerization"],
    "Product Manager": ["Agile", "Scrum", "Market Research", "Product Roadmap", "Product Lifecycle", "Stakeholder Management", "User Stories", "Project Management", "UX/UI Design", "Data Analysis"],
    "Systems Analyst": ["Business Analysis", "SQL", "System Design", "Technical Documentation", "Requirements Gathering", "Software Design", "Agile Methodology", "UML", "Process Improvement", "Risk Management"],
    "Security Engineer": ["Cybersecurity", "Ethical Hacking", "Firewalls", "Penetration Testing", "Network Security", "Incident Response", "Cryptography", "Risk Assessment", "Security Audits", "Compliance"],
    "Machine Learning Engineer": ["Python", "TensorFlow", "Keras", "Scikit-learn", "Pandas", "Numpy", "Model Deployment", "Deep Learning", "Neural Networks", "Cloud ML Services"],
    "Artificial Intelligence Engineer": ["AI", "Neural Networks", "Deep Learning", "TensorFlow", "PyTorch", "NLP", "Computer Vision", "Reinforcement Learning", "Speech Recognition", "Big Data"],
    "Blockchain Developer": ["Ethereum", "Smart Contracts", "Solidity", "Blockchain Architecture", "Cryptography", "Web3", "Decentralized Applications", "IPFS", "NFTs", "DeFi"],
    "Game Developer": ["C++", "Unity", "Unreal Engine", "Game Design", "C#", "3D Modeling", "Animation", "Game Physics", "AI for Games", "Multiplayer Systems"],
    "Mobile App Developer": ["Swift", "Kotlin", "Flutter", "React Native", "Java", "Android Development", "iOS Development", "UI/UX Design", "Mobile APIs", "Cross-platform Development"],
    "Network Engineer": ["Networking", "Cisco", "TCP/IP", "VPN", "Routing", "Network Security", "Wi-Fi Configuration", "LAN/WAN", "Firewall Configuration", "Cloud Networking"],
    "Embedded Systems Engineer": ["C", "C++", "Embedded C", "RTOS", "Microcontrollers", "IoT", "Sensor Integration", "Embedded Linux", "FPGA", "VHDL"],
    "Site Reliability Engineer": ["Linux", "Monitoring Tools", "Automation", "Kubernetes", "Terraform", "Cloud Infrastructure", "Incident Management", "System Scalability", "Scripting", "Networking"],
    "Product Designer": ["UI Design", "UX Design", "Wireframing", "Prototyping", "Adobe XD", "Figma", "Sketch", "User Testing", "Responsive Design", "Design Thinking"],
    "Salesforce Developer": ["Salesforce", "Apex", "Lightning", "Visualforce", "Salesforce Configuration", "SOQL", "Salesforce Integration", "Salesforce Architecture", "Data Migration", "Process Automation"],
    "Digital Marketing Specialist": ["SEO", "Google Analytics", "Social Media", "Content Marketing", "PPC", "Email Campaigns", "Social Media Ads", "Content Strategy", "Marketing Automation", "Brand Strategy"],
    "Business Intelligence Analyst": ["SQL", "Power BI", "Tableau", "Data Visualization", "Data Warehousing", "ETL", "Business Analysis", "Reporting Tools", "Data Modeling", "Forecasting"],
    "IT Support Specialist": ["Troubleshooting", "Windows OS", "Mac OS", "Networking", "Hardware Support", "Customer Service", "Active Directory", "Ticketing Systems", "Remote Support", "System Maintenance"],
    "SEO Specialist": ["SEO", "Google Analytics", "Content Strategy", "Keyword Research", "Link Building", "Technical SEO", "On-page Optimization", "Off-page Optimization", "Google Search Console", "Local SEO"]
}


UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        return f"Error extracting text: {str(e)}"

# Extract skills
def extract_skills(text):
    all_skills = {skill.lower() for skills in job_role_skills.values() for skill in skills}
    found = [skill for skill in all_skills if skill in text.lower()]
    return found if found else ["No skills listed."]

# Extract experience
def extract_experience(text):
    match = re.search(r'(Work Experience|Professional Experience)(.*?)(?=(Skills|Education|Projects|$))',
                      text, re.DOTALL | re.IGNORECASE)
    if match:
        return [line.strip() for line in match.group(2).split("\n") if line.strip()]
    return ["No experience listed."]

# Extract projects
def extract_projects(text):
    match = re.search(r'(Projects?|Personal Projects?)(.*?)(?=(Experience|Skills|Education|$))',
                      text, re.DOTALL | re.IGNORECASE)
    if match:
        return [line.strip() for line in match.group(2).split("\n") if line.strip()]
    return ["No projects listed."]

# Calculate ATS score based on skills and experience
def calculate_ats_score(resume_skills, job_role, experience_text):
    required = job_role_skills.get(job_role, [])
    matched_skills = [skill for skill in required if skill.lower() in resume_skills]
    missing_skills = [skill for skill in required if skill.lower() not in resume_skills]

    # Calculate skill-based ATS score
    skill_score = round((len(matched_skills) / len(required)) * 100, 2) if required else 0
    
    # Experience-based scoring logic
    experience_score = calculate_experience_score(experience_text)
    
    # Combine both scores (weighted average of 70% skill score, 30% experience score)
    ats_score = round(0.7 * skill_score + 0.3 * experience_score, 2)

    return ats_score, matched_skills, missing_skills

# Calculate experience score
def calculate_experience_score(experience_text):
    # We check for keywords indicating the experience duration
    experience_patterns = {
        "Less than 6 months": (0, 6),
        "6 months to 1 year": (6, 12),
        "1 year to 2 years": (12, 24),
        "2 years to 3 years": (24, 36),
        "3 to 5 years": (36, 60),
        "More than 5 years": (60, 999)
    }
    
    score = 0
    for duration, (min_months, max_months) in experience_patterns.items():
        if re.search(rf"\b{duration}\b", experience_text, re.IGNORECASE):
            months = (min_months + max_months) // 2  # Average months
            score = map_experience_to_score(months)
            break
    
    return score

# Map experience duration to score
def map_experience_to_score(months):
    if months < 6:
        return 5
    elif 6 <= months < 12:
        return 10
    elif 12 <= months < 24:
        return 15
    elif 24 <= months < 36:
        return 20
    elif 36 <= months < 60:
        return 25
    else:
        return 30

# Feedback Generator
def generate_feedback(score, job_role, missing_skills):
    if score >= 70:
        return f"✅ Great! Your resume is well aligned with the {job_role} role."
    elif 50 <= score < 70:
        return (
            f"⚠️ Your resume matches the {job_role} role moderately well.\n"
            f"Try adding or emphasizing these skills: {', '.join(missing_skills)}"
        )
    else:
        return (
            f"❌ Your resume has a low match score for the {job_role} role.\n"
            f"Consider adding: {', '.join(missing_skills)}\n"
            "Also improve formatting, keywords, and alignment with job responsibilities."
        )

# Route to home page
@app.route('/')
def index():
    return render_template('index.html', job_roles=job_role_skills.keys())

# Resume analysis route
@app.route('/analyze', methods=['POST'])
def analyze_resume():
    file = request.files.get('resume')
    job_role = request.form.get('job_role')

    if not file or not job_role:
        return jsonify({"error": "Missing resume file or job role."}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # Extract text from PDF
    resume_text = extract_text_from_pdf(filepath)

    # Extract relevant information
    extracted_skills = extract_skills(resume_text)
    experience = extract_experience(resume_text)
    projects = extract_projects(resume_text)

    # Calculate ATS score and match skills
    ats_score, matched_skills, missing_skills = calculate_ats_score(extracted_skills, job_role, resume_text)

    # Generate feedback based on ATS score and missing skills
    ats_feedback = generate_feedback(ats_score, job_role, missing_skills)

    return jsonify({
        "job_role": job_role,
        "ats_score": ats_score,
        "skills_found": matched_skills,
        "skills_extracted": extracted_skills,
        "experience": experience,
        "projects": projects,
        "ats_feedback": ats_feedback
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
