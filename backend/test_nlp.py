# =========================================================
# HIRELENS
# NLP TEST
# =========================================================

from nlp.skill_extractor import extract_skills
from nlp.job_analyzer import analyze_job_description
from nlp.skill_matcher import match_skills


# =========================================================
# SAMPLE RESUME
# =========================================================

sample_resume = """

Unnati Negi

Aspiring Software Engineer.

Technical Skills:
Python, Java, SQL, Flask, Machine Learning,
NLP, NumPy, Pandas, TensorFlow, Git,
PyTorch, Scikit-learn, JavaScript.

Projects:
Built an AI Resume Analyzer using Python,
Flask, NLP and SQL.

"""


# =========================================================
# SAMPLE JOB DESCRIPTION
# =========================================================

sample_job_description = """

We are looking for a Python Developer with
experience in Python, Flask, SQL, REST API
and Machine Learning.

The candidate should have knowledge of
Docker, AWS, Git and PostgreSQL.

Experience with React and JavaScript is a plus.

Strong knowledge of Data Structures and
Algorithms is required.

"""


# =========================================================
# EXTRACT RESUME SKILLS
# =========================================================

resume_skills = extract_skills(
    sample_resume
)


print("\n========================================")
print("           RESUME SKILLS")
print("========================================")


for skill in resume_skills:

    print(
        "✓",
        skill
    )


# =========================================================
# ANALYZE JOB DESCRIPTION
# =========================================================

job_result = analyze_job_description(
    sample_job_description
)


job_skills = job_result["skills"]


print("\n========================================")
print("         JOB REQUIRED SKILLS")
print("========================================")


for skill in job_skills:

    print(
        "✓",
        skill
    )


# =========================================================
# MATCH SKILLS
# =========================================================

result = match_skills(
    resume_skills,
    job_skills
)


# =========================================================
# DISPLAY MATCHED SKILLS
# =========================================================

print("\n========================================")
print("          MATCHED SKILLS")
print("========================================")


for skill in result["matched_skills"]:

    print(
        "✓",
        skill
    )


# =========================================================
# DISPLAY MISSING SKILLS
# =========================================================

print("\n========================================")
print("          MISSING SKILLS")
print("========================================")


for skill in result["missing_skills"]:

    print(
        "✗",
        skill
    )


# =========================================================
# DISPLAY SCORE
# =========================================================

print("\n========================================")
print("          COMPATIBILITY")
print("========================================")


print(
    "Matched:",
    result["total_matched"]
)


print(
    "Missing:",
    result["total_missing"]
)


print(
    "Required:",
    result["total_required"]
)


print(
    "Match Percentage:",
    f'{result["match_percentage"]}%'
)