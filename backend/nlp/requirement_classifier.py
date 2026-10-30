import re


# =========================================================
# REQUIREMENT CLASSIFICATION KEYWORDS
# =========================================================

REQUIRED_KEYWORDS = [
    "required",
    "must have",
    "must-have",
    "mandatory",
    "essential",
    "necessary",
    "should have",
    "strong knowledge",
    "strong understanding",
    "proficiency in",
    "proficient in",
    "experience with",
    "experience in",
    "hands-on experience",
    "minimum",
]


PREFERRED_KEYWORDS = [
    "preferred",
    "preferably",
    "nice to have",
    "nice-to-have",
    "good to have",
    "good-to-have",
    "plus",
    "bonus",
    "desirable",
    "desired",
    "advantage",
    "additional",
]


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text):
    """
    Normalize job description text.
    """

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# FIND SENTENCE CONTAINING A SKILL
# =========================================================

def find_skill_context(job_description, skill):
    """
    Find the sentence or text segment containing a skill.

    Returns:
        The surrounding text containing the skill.
    """

    sentences = re.split(
        r"[.!?;\n]+",
        job_description
    )

    skill_pattern = re.compile(
        r"(?<!\w)"
        + re.escape(skill)
        + r"(?!\w)",
        re.IGNORECASE
    )

    for sentence in sentences:

        sentence = sentence.strip()

        if skill_pattern.search(sentence):
            return sentence

    return ""


# =========================================================
# CLASSIFY SINGLE SKILL
# =========================================================

def classify_skill(skill, context):
    """
    Classify a skill as required or preferred
    based on its surrounding context.

    Returns:
        'required', 'preferred', or 'unspecified'
    """

    normalized_context = normalize_text(context)

    # -----------------------------------------------------
    # Check preferred indicators first
    # -----------------------------------------------------

    for keyword in PREFERRED_KEYWORDS:

        if keyword in normalized_context:
            return "preferred"

    # -----------------------------------------------------
    # Check required indicators
    # -----------------------------------------------------

    for keyword in REQUIRED_KEYWORDS:

        if keyword in normalized_context:
            return "required"

    # -----------------------------------------------------
    # No explicit classification
    # -----------------------------------------------------

    return "unspecified"


# =========================================================
# CLASSIFY ALL JOB SKILLS
# =========================================================

def classify_requirements(job_description, skills):
    """
    Classify extracted job skills into:

        required_skills
        preferred_skills
        unspecified_skills

    Args:
        job_description: Original job description text.
        skills: Skills extracted by job_analyzer.py.

    Returns:
        Dictionary containing classified skills.
    """

    required_skills = []
    preferred_skills = []
    unspecified_skills = []

    skill_details = []

    for skill in skills:

        context = find_skill_context(
            job_description,
            skill
        )

        classification = classify_skill(
            skill,
            context
        )

        # -------------------------------------------------
        # Store skill according to classification
        # -------------------------------------------------

        if classification == "required":

            required_skills.append(skill)

        elif classification == "preferred":

            preferred_skills.append(skill)

        else:

            unspecified_skills.append(skill)

        # -------------------------------------------------
        # Detailed information for explanation
        # -------------------------------------------------

        skill_details.append({
            "skill": skill,
            "classification": classification,
            "context": context
        })

    return {

        "required_skills":
            sorted(
                list(
                    set(required_skills)
                )
            ),

        "preferred_skills":
            sorted(
                list(
                    set(preferred_skills)
                )
            ),

        "unspecified_skills":
            sorted(
                list(
                    set(unspecified_skills)
                )
            ),

        "skill_details":
            skill_details,

        "required_count":
            len(set(required_skills)),

        "preferred_count":
            len(set(preferred_skills)),

        "unspecified_count":
            len(set(unspecified_skills))
    }


# =========================================================
# COMPLETE REQUIREMENT ANALYSIS
# =========================================================

def analyze_requirements(job_description, skills):
    """
    Perform complete requirement classification.

    This function is the main entry point for this module.
    """

    if not job_description:

        return {
            "required_skills": [],
            "preferred_skills": [],
            "unspecified_skills": [],
            "skill_details": [],
            "required_count": 0,
            "preferred_count": 0,
            "unspecified_count": 0
        }

    return classify_requirements(
        job_description,
        skills
    )


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    sample_job_description = """
    We are looking for a Software Engineer with strong knowledge
    of Python, SQL and Flask.

    Candidates must have experience with REST API development
    and Git.

    Knowledge of AWS is preferred.

    Experience with Docker is a nice to have.

    React experience is a bonus.
    """

    sample_skills = [
        "python",
        "sql",
        "flask",
        "rest api",
        "git",
        "aws",
        "docker",
        "react"
    ]

    result = analyze_requirements(
        sample_job_description,
        sample_skills
    )

    print("\n===== REQUIRED SKILLS =====")

    for skill in result["required_skills"]:
        print("-", skill)

    print("\n===== PREFERRED SKILLS =====")

    for skill in result["preferred_skills"]:
        print("-", skill)

    print("\n===== UNSPECIFIED SKILLS =====")

    for skill in result["unspecified_skills"]:
        print("-", skill)

    print("\n===== SKILL DETAILS =====")

    for item in result["skill_details"]:

        print(
            f"{item['skill']} "
            f"-> {item['classification']}"
        )

        print(
            f"   Context: {item['context']}"
        )