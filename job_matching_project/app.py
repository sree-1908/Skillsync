from flask import Flask, render_template, request, jsonify
import pdfplumber
import json
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "resume_uploads"

# Load job data
with open("jobs.json") as f:
    jobs = json.load(f)

# Sample skill list for matching
skills_list = ["Python", "SQL", "JavaScript", "React", "HTML", "CSS", "Data Analysis"]

def extract_skills_from_resume(filepath):
    extracted_skills = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for skill in skills_list:
                if skill.lower() in text.lower():
                    extracted_skills.append(skill)
    return list(set(extracted_skills))

def match_jobs(user_skills):
    matched_jobs = []
    for job in jobs:
        job_skills = set(job["skills"])
        overlap = job_skills.intersection(set(user_skills))
        match_score = len(overlap) / len(job_skills)
        if match_score > 0.5:  # Adjust the threshold as necessary
            matched_jobs.append({**job, "score": match_score})
    matched_jobs.sort(key=lambda x: x["score"], reverse=True)
    return matched_jobs

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'resume' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        resume = request.files["resume"]
        if resume.filename == '':
            return jsonify({"error": "No selected file"}), 400

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
        resume.save(filepath)

        user_skills = extract_skills_from_resume(filepath)
        matched_jobs = match_jobs(user_skills)
        return jsonify(matched_jobs)

    return render_template("index1.html")

if __name__ == "__main__":
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])
    app.run(debug=True)
