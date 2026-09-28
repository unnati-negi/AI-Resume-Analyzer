from flask import Flask, request, jsonify, send_from_directory
from services.resume_parser import extract_text_from_pdf
from nlp.skill_extractor import extract_skills
from nlp.job_analyzer import analyze_job_description

import os
from werkzeug.utils import secure_filename


# =========================================================
# HIRELENS APPLICATION
# =========================================================

app = Flask(__name__)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

FRONTEND_FOLDER = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "..",
        "frontend"
    )
)


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# FRONTEND
# =========================================================

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_FOLDER,
        "index.html"
    )


@app.route("/style.css")
def style():

    return send_from_directory(
        FRONTEND_FOLDER,
        "style.css"
    )


@app.route("/script.js")
def script():

    return send_from_directory(
        FRONTEND_FOLDER,
        "script.js"
    )


# =========================================================
# RESUME UPLOAD
# =========================================================

@app.route(
    "/upload-resume",
    methods=["POST"]
)
def upload_resume():

    print("\n==============================")
    print("RESUME UPLOAD REQUEST RECEIVED")
    print("==============================")


    # -----------------------------------------------------
    # Check file
    # -----------------------------------------------------

    if "resume" not in request.files:

        print("ERROR: No resume field found.")

        return jsonify({
            "error": "No resume uploaded."
        }), 400


    file = request.files["resume"]


    print(
        "Uploaded filename:",
        file.filename
    )


    # -----------------------------------------------------
    # Check filename
    # -----------------------------------------------------

    if not file.filename:

        return jsonify({
            "error": "No file selected."
        }), 400

# =========================================================
# JOB DESCRIPTION ANALYSIS
# =========================================================

@app.route(
    "/analyze-job",
    methods=["POST"]
)
def analyze_job():

    print("\n==============================")
    print("JOB DESCRIPTION REQUEST")
    print("==============================")


    # -----------------------------------------------------
    # Get JSON data
    # -----------------------------------------------------

    data = request.get_json()


    if not data:

        return jsonify({
            "error": "No job description provided."
        }), 400


    # -----------------------------------------------------
    # Get job description
    # -----------------------------------------------------

    job_description = data.get(
        "job_description",
        ""
    )


    # -----------------------------------------------------
    # Validate job description
    # -----------------------------------------------------

    if not job_description.strip():

        return jsonify({
            "error": "Please enter a job description."
        }), 400


    # -----------------------------------------------------
    # Analyze job description
    # -----------------------------------------------------

    try:

        result = analyze_job_description(
            job_description
        )


        print(
            "Job skills found:",
            result["skills"]
        )


        # -------------------------------------------------
        # Return result
        # -------------------------------------------------

        return jsonify({

            "message":
                "Job description analyzed successfully.",

            "text":
                result["text"],

            "skills":
                result["skills"],

            "skill_count":
                result["skill_count"],

            "sentences":
                result["sentences"]

        })


    except Exception as error:

        print(
            "Job analysis error:",
            repr(error)
        )


        return jsonify({

            "error":
                f"Could not analyze job description: {str(error)}"

        }), 500
    # -----------------------------------------------------
    # Check extension
    # -----------------------------------------------------

    if not file.filename.lower().endswith(".pdf"):

        return jsonify({
            "error": "Only PDF files are allowed."
        }), 400


    # -----------------------------------------------------
    # Secure filename
    # -----------------------------------------------------

    filename = secure_filename(
        file.filename
    )


    if not filename:

        return jsonify({
            "error": "Invalid filename."
        }), 400


    # -----------------------------------------------------
    # Create complete file path
    # -----------------------------------------------------

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )


    print(
        "Saving file to:",
        file_path
    )


    try:

        # ================================================
        # SAVE FILE
        # ================================================

        file.save(file_path)


        print(
            "File saved successfully."
        )


        # ================================================
        # VERIFY FILE EXISTS
        # ================================================

        if not os.path.exists(file_path):

            raise Exception(
                "Uploaded file was not saved."
            )


        print(
            "File size:",
            os.path.getsize(file_path),
            "bytes"
        )


        # ================================================
        # EXTRACT TEXT
        # ================================================

        print(
            "Extracting text from PDF..."
        )


        resume_text = extract_text_from_pdf(
            file_path
        )


        print(
            "Extracted characters:",
            len(resume_text)
        )


        # ================================================
        # CHECK TEXT
        # ================================================

        if not resume_text or not resume_text.strip():

            print(
                "ERROR: PDF contains no readable text."
            )

            return jsonify({

                "error":
                    "No readable text was found in this PDF."

            }), 400


        # ================================================
        # EXTRACT SKILLS
        # ================================================

        print(
            "Extracting skills..."
        )


        skills = extract_skills(
            resume_text
        )


        print(
            "Skills found:",
            skills
        )


        # ================================================
        # SUCCESS
        # ================================================

        print(
            "Resume analysis completed successfully."
        )


        return jsonify({

            "message":
                "Resume analyzed successfully.",

            "filename":
                filename,

            "text":
                resume_text,

            "skills":
                skills,

            "skill_count":
                len(skills)

        })


    except Exception as error:

        print(
            "\nERROR WHILE PROCESSING RESUME:"
        )

        print(
            repr(error)
        )


        return jsonify({

            "error":
                f"Could not process resume: {str(error)}"

        }), 500


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )