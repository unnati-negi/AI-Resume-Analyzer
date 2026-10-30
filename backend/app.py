# =========================================================
# HIRELENS - COMPLETE FLASK BACKEND
# =========================================================

import os
import uuid

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# IMPORTS
# Supports both:
# python -m backend.app       (project root)
# python app.py               (backend folder)
# =========================================================

try:
    from backend.services.resume_parser import extract_text_from_pdf
    from backend.nlp.skill_extractor import extract_skills
    from backend.nlp.job_analyzer import analyze_job_description
    from backend.nlp.skill_matcher import (
        match_skills,
        match_classified_skills
    )
    from backend.nlp.requirement_classifier import analyze_requirements

except ModuleNotFoundError as import_error:
    # Fallback for running app.py directly from backend.
    # Only fall back if the package prefix itself is missing.
    if import_error.name not in ("backend", "backend.services", "backend.nlp"):
        raise

    from services.resume_parser import extract_text_from_pdf
    from nlp.skill_extractor import extract_skills
    from nlp.job_analyzer import analyze_job_description
    from nlp.skill_matcher import (
        match_skills,
        match_classified_skills
    )
    from nlp.requirement_classifier import analyze_requirements


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def safe_list(value):
    """Ensure a value is returned as a list."""
    return value if isinstance(value, list) else []


def get_score_interpretation(score):
    if score >= 80:
        return "Strong Match"
    if score >= 60:
        return "Good Match"
    if score >= 40:
        return "Moderate Match"
    return "Low Match"


def get_optional_analysis(resume_text, job_description, matching_result):
    """Run optional gap, recommendation, and semantic modules safely."""

    gap_result = {}
    gap_summary = ""
    recommendation_result = {}
    recommendation_summary = ""

    semantic_result = {
        "status": "unavailable",
        "semantic_similarity": None
    }

    # Skill gap and recommendation analysis
    try:
        from backend.nlp.skill_gap import (
            analyze_skill_gaps,
            generate_gap_summary
        )
        from backend.nlp.recommender import (
            generate_recommendations,
            generate_recommendation_summary
        )

        gap_result = analyze_skill_gaps(matching_result)
        gap_summary = generate_gap_summary(gap_result)

        recommendation_result = generate_recommendations(
            gap_result
        )

        recommendation_summary = generate_recommendation_summary(
            recommendation_result
        )

    except ModuleNotFoundError as error:
        if error.name not in (
            "backend",
            "backend.nlp",
            "nlp",
            "backend.nlp.skill_gap",
            "backend.nlp.recommender"
        ):
            app.logger.exception("Optional analysis dependency failed.")
        else:
            app.logger.warning("Optional gap analysis module unavailable.")

    except Exception:
        app.logger.exception("Skill gap or recommendation analysis failed.")

    # Semantic matching is optional because it may require an ML model.
    try:
        from backend.nlp.semantic_matcher import analyze_semantic_match

        semantic_result = analyze_semantic_match(
            resume_text,
            job_description
        )

    except Exception:
        app.logger.warning(
            "Semantic matching is unavailable; continuing with skill matching."
        )

    return (
        gap_result,
        gap_summary,
        recommendation_result,
        recommendation_summary,
        semantic_result
    )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


# =========================================================
# CSS
# =========================================================

@app.route("/style.css")
def style():
    return send_from_directory(FRONTEND_DIR, "style.css")


# =========================================================
# JAVASCRIPT
# =========================================================

@app.route("/script.js")
def script():
    return send_from_directory(FRONTEND_DIR, "script.js")


# =========================================================
# 1. UPLOAD AND ANALYZE RESUME
# =========================================================

@app.route("/upload-resume", methods=["POST"])
def upload_resume():

    if "resume" not in request.files:
        return jsonify({"error": "No resume file was uploaded."}), 400

    uploaded_file = request.files["resume"]

    if not uploaded_file.filename:
        return jsonify({"error": "Please select a file."}), 400

    if not uploaded_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    filename = secure_filename(uploaded_file.filename)

    if not filename:
        return jsonify({"error": "Invalid filename."}), 400

    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    try:
        uploaded_file.save(file_path)

        # Extract text from the PDF.
        resume_text = extract_text_from_pdf(file_path)

        if not resume_text or not resume_text.strip():
            return jsonify({
                "error": (
                    "No readable text was extracted. "
                    "The PDF may be scanned or image-based."
                )
            }), 400

        # Extract skills using the existing NLP module.
        skills = safe_list(extract_skills(resume_text))

        return jsonify({
            "message": "Resume analyzed successfully.",
            "filename": filename,
            "text": resume_text,
            "skills": skills,
            "skill_count": len(skills)
        }), 200

    except Exception:
        app.logger.exception("Resume upload or parsing failed.")

        return jsonify({
            "error": (
                "Could not process the resume. "
                "Check the Flask terminal for details."
            )
        }), 500

    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                app.logger.warning("Temporary PDF could not be deleted.")


# =========================================================
# 2. ANALYZE JOB DESCRIPTION
# =========================================================

@app.route("/analyze-job", methods=["POST"])
def analyze_job():

    data = request.get_json(silent=True) or {}
    job_description = data.get("job_description", "")

    if not isinstance(job_description, str):
        return jsonify({"error": "Job description must be text."}), 400

    job_description = job_description.strip()

    if not job_description:
        return jsonify({"error": "Please enter a job description."}), 400

    try:
        job_result = analyze_job_description(job_description)

        job_skills = safe_list(job_result.get("skills", []))

        requirement_result = {}

        try:
            requirement_result = analyze_requirements(
                job_description,
                job_skills
            )
        except Exception:
            app.logger.exception("Job requirement classification failed.")

        return jsonify({
            "message": "Job description analyzed successfully.",
            "text": job_result.get("text", job_description),
            "skills": job_skills,
            "skill_count": len(job_skills),
            "sentences": job_result.get("sentences", []),

            "required_skills": safe_list(
                requirement_result.get("required_skills", [])
            ),
            "preferred_skills": safe_list(
                requirement_result.get("preferred_skills", [])
            ),
            "unspecified_skills": safe_list(
                requirement_result.get("unspecified_skills", [])
            ),

            "requirements": requirement_result
        }), 200

    except Exception:
        app.logger.exception("Job description analysis failed.")

        return jsonify({
            "error": (
                "Could not analyze the job description. "
                "Check the Flask terminal for details."
            )
        }), 500


# =========================================================
# 3. MATCH RESUME WITH JOB DESCRIPTION
# =========================================================

@app.route("/match-resume", methods=["POST"])
def match_resume():

    data = request.get_json(silent=True) or {}

    resume_text = data.get("resume_text", "")
    job_description = data.get("job_description", "")

    if not isinstance(resume_text, str):
        return jsonify({"error": "Resume text must be text."}), 400

    if not isinstance(job_description, str):
        return jsonify({"error": "Job description must be text."}), 400

    resume_text = resume_text.strip()
    job_description = job_description.strip()

    if not resume_text:
        return jsonify({"error": "Resume text is required."}), 400

    if not job_description:
        return jsonify({"error": "Job description is required."}), 400

    try:
        # -------------------------------------------------
        # STEP 1: Extract skills
        # -------------------------------------------------

        resume_skills = safe_list(extract_skills(resume_text))

        job_result = analyze_job_description(job_description)
        job_skills = safe_list(job_result.get("skills", []))

        # -------------------------------------------------
        # STEP 2: Basic matching
        # -------------------------------------------------

        basic_result = match_skills(
            resume_skills,
            job_skills
        )

        # -------------------------------------------------
        # STEP 3: Classify requirements
        # -------------------------------------------------

        requirement_result = analyze_requirements(
            job_description,
            job_skills
        )

        required_skills = safe_list(
            requirement_result.get("required_skills", [])
        )

        preferred_skills = safe_list(
            requirement_result.get("preferred_skills", [])
        )

        unspecified_skills = safe_list(
            requirement_result.get("unspecified_skills", [])
        )

        # -------------------------------------------------
        # STEP 4: Requirement-aware matching
        # -------------------------------------------------

        matching_result = match_classified_skills(
            resume_skills,
            required_skills,
            preferred_skills,
            unspecified_skills
        )

        # -------------------------------------------------
        # STEP 5: Calculate overall score
        # -------------------------------------------------

        required_score = float(
            matching_result.get("required_match_percentage", 0) or 0
        )

        preferred_score = float(
            matching_result.get("preferred_match_percentage", 0) or 0
        )

        total_required = int(
            matching_result.get("total_required", 0) or 0
        )

        total_preferred = int(
            matching_result.get("total_preferred", 0) or 0
        )

        if total_required and total_preferred:
            overall_score = (
                0.80 * required_score
                + 0.20 * preferred_score
            )
        elif total_required:
            overall_score = required_score
        elif total_preferred:
            overall_score = preferred_score
        else:
            # Fallback if classification produced no skills.
            overall_score = float(
                basic_result.get("match_percentage", 0) or 0
            )

        overall_score = round(
            max(0.0, min(100.0, overall_score)),
            2
        )

        score_result = {
            "overall_score": overall_score,
            "interpretation": get_score_interpretation(overall_score),
            "required_score": round(required_score, 2),
            "preferred_score": round(preferred_score, 2),
            "weights": {
                "required": 80,
                "preferred": 20
            }
        }

        # -------------------------------------------------
        # STEP 6: Combine matched and missing skills
        # -------------------------------------------------

        matched_skills = sorted(set(
            matching_result.get("matched_required_skills", [])
            + matching_result.get("matched_preferred_skills", [])
            + matching_result.get("matched_unspecified_skills", [])
        ))

        missing_skills = sorted(set(
            matching_result.get("missing_required_skills", [])
            + matching_result.get("missing_preferred_skills", [])
            + matching_result.get("missing_unspecified_skills", [])
        ))

        # -------------------------------------------------
        # STEP 7: Skill gaps, recommendations, semantic score
        # -------------------------------------------------

        (
            gap_result,
            gap_summary,
            recommendation_result,
            recommendation_summary,
            semantic_result
        ) = get_optional_analysis(
            resume_text,
            job_description,
            matching_result
        )

        recommendations = safe_list(
            recommendation_result.get("recommendations", [])
        )

        # -------------------------------------------------
        # STEP 8: Return response for the frontend
        # -------------------------------------------------

        return jsonify({
            "message": "Resume-job matching completed.",

            "resume_skills": resume_skills,
            "job_skills": job_skills,

            # Frontend compatibility fields
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "match_percentage": overall_score,

            # Detailed matching results
            "matching": {
                **matching_result,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills
            },

            # Compatibility score and interpretation
            "score": score_result,

            # Classified job requirements
            "requirements": requirement_result,

            # Gap analysis and recommendations
            "skill_gaps": gap_result,
            "skill_gap_summary": gap_summary,
            "recommendations": recommendations,
            "recommendation_summary": recommendation_summary,

            # Counts
            "total_required": total_required,
            "total_matched": len(matched_skills),
            "total_missing": len(missing_skills),

            # Optional semantic matching
            "semantic_matching": semantic_result
        }), 200

    except Exception:
        app.logger.exception("Resume-job matching failed.")

        return jsonify({
            "error": (
                "Resume matching failed. "
                "Check the Flask terminal for the full error."
            )
        }), 500


# =========================================================
# FILE TOO LARGE
# =========================================================

@app.errorhandler(413)
def handle_file_too_large(error):
    return jsonify({
        "error": "The uploaded file must be smaller than 10 MB."
    }), 413


# =========================================================
# START FLASK
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)