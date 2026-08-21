from flask import Flask, request, jsonify, send_from_directory
from services.resume_parser import extract_text_from_pdf
import os


app = Flask(__name__)

UPLOAD_FOLDER = "backend/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------
# Serve frontend
# -----------------------------

@app.route("/")
def home():
    return send_from_directory("../frontend", "index.html")


@app.route("/style.css")
def style():
    return send_from_directory("../frontend", "style.css")


@app.route("/script.js")
def script():
    return send_from_directory("../frontend", "script.js")


# -----------------------------
# Resume upload API
# -----------------------------

@app.route("/upload-resume", methods=["POST"])
def upload_resume():

    if "resume" not in request.files:
        return jsonify({
            "error": "No resume uploaded"
        }), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({
            "error": "No file selected"
        }), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({
            "error": "Only PDF files are allowed"
        }), 400

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    file.save(file_path)

    try:
        text = extract_text_from_pdf(file_path)

        return jsonify({
            "message": "Resume uploaded successfully",
            "filename": file.filename,
            "text": text
        })

    except Exception as error:

        return jsonify({
            "error": f"Could not process PDF: {str(error)}"
        }), 500


# -----------------------------
# Start application
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)