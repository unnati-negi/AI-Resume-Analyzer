import re

from .skills import SKILLS


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text):
    """
    Convert text to lowercase and normalize whitespace.
    """

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# SKILL EXTRACTION FROM JOB DESCRIPTION
# =========================================================

def extract_job_skills(job_description):
    """
    Extract technical skills from a job description.

    Returns:
        A sorted list of skills found in the job description.
    """

    normalized_text = normalize_text(
        job_description
    )

    found_skills = []


    for skill in SKILLS:

        pattern = (
            r"(?<!\w)"
            + re.escape(skill)
            + r"(?!\w)"
        )


        if re.search(
            pattern,
            normalized_text
        ):

            found_skills.append(
                skill
            )


    return sorted(
        list(
            set(found_skills)
        )
    )


# =========================================================
# JOB DESCRIPTION ANALYSIS
# =========================================================

def analyze_job_description(job_description):
    """
    Analyze a job description.

    Returns:
        Dictionary containing:
        - cleaned text
        - extracted skills
        - skill count
        - sentences
    """

    if not job_description:

        return {
            "text": "",
            "skills": [],
            "skill_count": 0,
            "sentences": []
        }


    cleaned_text = normalize_text(
        job_description
    )


    skills = extract_job_skills(
        job_description
    )


    # -----------------------------------------------------
    # Split into sentences
    # -----------------------------------------------------

    sentences = re.split(
        r"[.!?]+",
        job_description
    )


    sentences = [

        sentence.strip()

        for sentence in sentences

        if sentence.strip()

    ]


    return {

        "text":
            cleaned_text,

        "skills":
            skills,

        "skill_count":
            len(skills),

        "sentences":
            sentences

    }