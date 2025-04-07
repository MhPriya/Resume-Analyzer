from flask import Flask, render_template, request
from utils import extract_text_from_pdf,verify_bullet_alignment,verify_font_sizes,extract_layout_info, match_resume_with_job,extract_keywords,extract_links,validate_links, extract_bullet_points

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    analysis = None  # Clear previous results on refresh
    job_desc = None
    if request.method == "POST":
        if "resume" in request.files:
            resume = request.files["resume"]
            if resume.filename.endswith(".pdf"):
                text = extract_text_from_pdf(resume)
                links = extract_links(text)
                link_statuses = validate_links(links)

                resume.seek(0)
                
                # Extract layout info for alignment and font-size analysis
                layout_data = extract_layout_info(resume)
                bullet_feedback = verify_bullet_alignment(layout_data)
                font_feedback = verify_font_sizes(layout_data, expected_size=12)
                

                # Get job description from text area
                job_description = request.form.get("job_description", "").lower()

                # Calculate match percentage and missing keywords
                match_percentage, missing_keywords = match_resume_with_job(text, job_description)
                top_skills = extract_keywords(text)
                links = extract_links(text)
                link_statuses = validate_links(links)
                analysis = {
                    "total_words": len(text.split()),
                    "top_skills": top_skills,
                    "match_percentage": match_percentage,
                    "missing_keywords": missing_keywords,
                    "bullet_points" : extract_bullet_points(text),
                    "link_statuses": validate_links(extract_links(text)),
                    "bullet_feedback": bullet_feedback,
                    "font_feedback": font_feedback,
                    "link_statuses": link_statuses,
                     }

    return render_template("index.html", analysis=analysis)

@app.route("/feedback", methods=["POST"])
def feedback():
    job_desc = request.form.get("job_desc")
    # Process feedback if needed; for now, simply return a placeholder.
    return "Feedback processing coming soon!"

if __name__ == "__main__":
    app.run(debug=True)
