import pdfplumber
import re
from io import BytesIO
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF resume."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def extract_keywords(text):
    """Extract relevant skills and keywords from resume text."""
    skills = [
    "Python", "Django", "Flask", "FastAPI", "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", 
    "JavaScript", "TypeScript", "React.js", "Next.js", "Vue.js", "Angular", "Node.js", "Express.js", 
    "HTML", "CSS", "Bootstrap", "Tailwind CSS", "REST API", "GraphQL", "Microservices", "Docker", 
    "Kubernetes", "AWS", "Azure", "Google Cloud", "CI/CD", "Jenkins", "Git", "GitHub", "GitLab", 
    "Agile", "Scrum", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-Learn", 
    "NLP", "Computer Vision", "Data Science", "Big Data", "Pandas", "NumPy", "Matplotlib", "Seaborn", 
    "Hadoop", "Spark", "Kafka", "RabbitMQ", "Celery", "FastAPI", "WebSockets", "GraphQL", "JWT", 
    "OAuth", "Web Security", "Unit Testing", "Selenium", "Cypress", "Linux", "Bash Scripting", 
    "Serverless", "Terraform", "Ansible", "TDD", "DDD", "SOLID Principles", "Design Patterns"
]

    extracted = [skill for skill in skills if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE)]
    return extracted

def match_resume_with_job(resume_text, job_description):
    """
    Compare keywords from the resume and the job description.
    Returns a tuple: (match_percentage, missing_keywords)
    """
    # Extract keywords from the resume (e.g., skills)
    resume_keywords = set(extract_keywords(resume_text))
    
    # Extract keywords from the job description.
    # You can use a similar extraction method as the resume or simply split by spaces.
    # For a more refined approach, you might create an extract_keywords function for job descriptions too.
    job_keywords = set(extract_keywords(job_description))
    
    # Avoid division by zero if job_keywords is empty
    if not job_keywords:
        return 0, []
    
    # Calculate the intersection between resume keywords and job keywords
    matched_keywords = resume_keywords & job_keywords
    
    # Calculate match percentage
    match_percentage = round((len(matched_keywords) / len(job_keywords)) * 100, 2)
    
    # Determine which job keywords are missing in the resume
    missing_keywords = list(job_keywords - resume_keywords)
    
    return match_percentage, missing_keywords

def extract_bullet_points(text):
    """
    Extract bullet points from resume text.
    Looks for lines starting with common bullet symbols.
    """
    # Use regex to match lines starting with a bullet (e.g., "-", "•", "*")
    bullet_pattern = re.compile(r'^\s*[\-\*\u2022]\s+(.*)', re.MULTILINE)
    bullet_points = bullet_pattern.findall(text)
    return bullet_points

import requests

def extract_links(text):
    """
    Extract URLs from text using regex.
    """
    url_pattern = re.compile(r'https?://\S+')
    return url_pattern.findall(text)


def verify_bullet_alignment(layout_data, tolerance=5):
    """
    Check bullet alignment by ensuring all bullet lines have similar x_position values.
    """
    bullet_lines = [item for item in layout_data if item["text"].startswith(("-", "•", "*"))]
    if not bullet_lines:
        return "No bullet points found."
    
    positions = [item["x_position"] for item in bullet_lines if item["x_position"] is not None]
    if max(positions) - min(positions) <= tolerance:
        return "Bullet points are properly aligned."
    else:
        return "Bullet point alignment is inconsistent."

def verify_font_sizes(layout_data, expected_size=12, tolerance=1):
    """
    Check whether the average font sizes are within an expected range.
    """
    sizes = [item["avg_font_size"] for item in layout_data if item["avg_font_size"] is not None]
    if sizes and abs((sum(sizes)/len(sizes)) - expected_size) <= tolerance:
        return "Font sizes are within the expected range."
    else:
        return "Font sizes deviate from the expected range."
    
def extract_layout_info(pdf_file):
    """
    Extract layout information (text, x_position, average font size) from a PDF file.
    Handles Flask's FileStorage input by converting it to a BytesIO stream.
    """
    # Convert FileStorage to BytesIO if necessary
    if hasattr(pdf_file, 'read'):
        pdf_stream = BytesIO(pdf_file.read())
        pdf_file.seek(0)  # Reset file pointer for any future operations
    else:
        # If already a file-like object, use it directly
        pdf_stream = pdf_file

    layout_data = []
    for page_layout in extract_pages(pdf_stream):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    line_text = text_line.get_text().strip()
                    if line_text:
                        # Collect x-coordinates and font sizes for each character in the line.
                        x_positions = [char.x0 for char in text_line if isinstance(char, LTChar)]
                        font_sizes = [char.size for char in text_line if isinstance(char, LTChar)]
                        layout_data.append({
                            "text": line_text,
                            "x_position": min(x_positions) if x_positions else None,
                            "avg_font_size": (sum(font_sizes) / len(font_sizes)) if font_sizes else None
                        })
    return layout_data

def validate_links(links):
    """
    Check each link's HTTP status.
    Returns a dictionary with each link's status and a summary.
    """
    results = {}
    all_valid = True  # Flag to track if all links are valid

    for link in links:
        try:
            response = requests.get(link, timeout=3)
            status = response.status_code
            results[link] = status
            if status != 200:
                all_valid = False
        except Exception as e:
            results[link] = str(e)
            all_valid = False

    # Add a summary message based on the validity of all links
    if all_valid:
        results["summary"] = "All links are correct."
    else:
        results["summary"] = "Some links may be invalid or unreachable."
    
    return results
