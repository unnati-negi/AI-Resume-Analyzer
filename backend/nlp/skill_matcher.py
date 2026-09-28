# =========================================================
# HIRELENS
# Skill Matcher
# =========================================================


# =========================================================
# SKILL NORMALIZATION
# =========================================================

def normalize_skill(skill):
    """
    Normalize a skill so that comparisons are consistent.
    """

    skill = skill.lower().strip()

    aliases = {

        # REST API variations
        "rest api": "rest api",
        "rest": "rest api",
        "restful api": "rest api",

        # JavaScript variations
        "js": "javascript",

        # Python variations
        "python3": "python",

        # PostgreSQL variations
        "postgres": "postgresql",

        # Machine Learning variations
        "ml": "machine learning",

        # Deep Learning variations
        "dl": "deep learning",

        # Scikit-learn variations
        "sklearn": "scikit-learn",
        "scikit learn": "scikit-learn",

        # NLP variations
        "natural language processing":
            "nlp"

    }


    return aliases.get(
        skill,
        skill
    )


# =========================================================
# NORMALIZE SKILL LIST
# =========================================================

def normalize_skill_list(skills):
    """
    Normalize and remove duplicate skills.
    """

    normalized = set()


    for skill in skills:

        if not skill:
            continue


        normalized.add(
            normalize_skill(skill)
        )


    return normalized


# =========================================================
# MATCH RESUME WITH JOB
# =========================================================

def match_skills(
    resume_skills,
    job_skills
):
    """
    Compare resume skills with required job skills.

    Returns:
        matched skills
        missing skills
        match percentage
        total required skills
    """

    # -----------------------------------------------------
    # Normalize both lists
    # -----------------------------------------------------

    resume_set = normalize_skill_list(
        resume_skills
    )

    job_set = normalize_skill_list(
        job_skills
    )


    # -----------------------------------------------------
    # Find matched skills
    # -----------------------------------------------------

    matched_skills = (
        resume_set
        .intersection(job_set)
    )


    # -----------------------------------------------------
    # Find missing skills
    # -----------------------------------------------------

    missing_skills = (
        job_set
        .difference(resume_set)
    )


    # -----------------------------------------------------
    # Calculate compatibility
    # -----------------------------------------------------

    total_required = len(job_set)


    if total_required == 0:

        match_percentage = 0

    else:

        match_percentage = (
            len(matched_skills)
            / total_required
        ) * 100


    # -----------------------------------------------------
    # Sort results
    # -----------------------------------------------------

    matched_skills = sorted(
        matched_skills
    )


    missing_skills = sorted(
        missing_skills
    )


    # -----------------------------------------------------
    # Return result
    # -----------------------------------------------------

    return {

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "match_percentage":
            round(
                match_percentage,
                2
            ),

        "total_required":
            total_required,

        "total_matched":
            len(matched_skills),

        "total_missing":
            len(missing_skills)

    }