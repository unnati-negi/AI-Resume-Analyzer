# =========================================================
# HIRELENS - SKILL MATCHER
# =========================================================


# =========================================================
# SKILL NORMALIZATION
# =========================================================

def normalize_skill(skill):
    """Normalize skill names and common aliases."""

    skill = str(skill).lower().strip()

    aliases = {
        "rest": "rest api",
        "restful api": "rest api",
        "js": "javascript",
        "python3": "python",
        "postgres": "postgresql",
        "ml": "machine learning",
        "dl": "deep learning",
        "sklearn": "scikit-learn",
        "scikit learn": "scikit-learn",
        "natural language processing": "nlp"
    }

    return aliases.get(skill, skill)


def normalize_skill_list(skills):
    """Normalize skills and remove duplicates."""

    normalized = set()

    for skill in skills or []:
        if skill:
            normalized.add(normalize_skill(skill))

    return normalized


# =========================================================
# BASIC SKILL MATCHING
# =========================================================

def match_skills(resume_skills, job_skills):
    """Match resume skills against all detected job skills."""

    resume_set = normalize_skill_list(resume_skills)
    job_set = normalize_skill_list(job_skills)

    matched_skills = sorted(resume_set & job_set)
    missing_skills = sorted(job_set - resume_set)

    total_required = len(job_set)

    match_percentage = (
        len(matched_skills) / total_required * 100
        if total_required else 0
    )

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": round(match_percentage, 2),
        "total_required": total_required,
        "total_matched": len(matched_skills),
        "total_missing": len(missing_skills)
    }


# =========================================================
# REQUIREMENT-AWARE SKILL MATCHING
# =========================================================

def match_classified_skills(
    resume_skills,
    required_skills,
    preferred_skills,
    unspecified_skills=None
):
    """
    Match skills by requirement category.

    Required skills contribute 80% and preferred skills 20%
    when both categories contain skills.

    Unspecified skills are reported separately and do not
    contribute to the weighted score.
    """

    resume_set = normalize_skill_list(resume_skills)

    required_set = normalize_skill_list(required_skills)
    preferred_set = normalize_skill_list(preferred_skills)

    unspecified_set = normalize_skill_list(
        unspecified_skills or []
    )

    # Avoid counting the same skill in multiple categories.
    preferred_set -= required_set
    unspecified_set -= required_set | preferred_set

    # Required skills
    matched_required = sorted(resume_set & required_set)
    missing_required = sorted(required_set - resume_set)

    # Preferred skills
    matched_preferred = sorted(resume_set & preferred_set)
    missing_preferred = sorted(preferred_set - resume_set)

    # Unspecified skills
    matched_unspecified = sorted(resume_set & unspecified_set)
    missing_unspecified = sorted(unspecified_set - resume_set)

    # Category scores
    required_percentage = (
        len(matched_required) / len(required_set) * 100
        if required_set else 0
    )

    preferred_percentage = (
        len(matched_preferred) / len(preferred_set) * 100
        if preferred_set else 0
    )

    # Weighted overall score
    if required_set and preferred_set:
        overall_percentage = (
            0.80 * required_percentage
            + 0.20 * preferred_percentage
        )
    elif required_set:
        overall_percentage = required_percentage
    elif preferred_set:
        overall_percentage = preferred_percentage
    else:
        overall_percentage = 0

    matched_all = sorted(
        set(
            matched_required
            + matched_preferred
            + matched_unspecified
        )
    )

    missing_all = sorted(
        set(
            missing_required
            + missing_preferred
            + missing_unspecified
        )
    )

    return {
        "matched_required_skills": matched_required,
        "missing_required_skills": missing_required,

        "matched_preferred_skills": matched_preferred,
        "missing_preferred_skills": missing_preferred,

        "matched_unspecified_skills": matched_unspecified,
        "missing_unspecified_skills": missing_unspecified,

        "matched_skills": matched_all,
        "missing_skills": missing_all,

        "required_match_percentage": round(
            required_percentage, 2
        ),

        "preferred_match_percentage": round(
            preferred_percentage, 2
        ),

        "overall_match_percentage": round(
            overall_percentage, 2
        ),

        "total_required": len(required_set),
        "total_preferred": len(preferred_set),
        "total_unspecified": len(unspecified_set),

        "total_matched": len(matched_all),
        "total_missing": len(missing_all),

        "total_matched_required": len(matched_required),
        "total_missing_required": len(missing_required),

        "total_matched_preferred": len(matched_preferred),
        "total_missing_preferred": len(missing_preferred),

        "scoring_weights": {
            "required": 80,
            "preferred": 20
        }
    }


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    resume_skills = [
        "python",
        "sql",
        "flask",
        "git",
        "react",
        "javascript"
    ]

    required_skills = [
        "python",
        "sql",
        "flask",
        "rest api",
        "git"
    ]

    preferred_skills = [
        "aws",
        "docker",
        "react"
    ]

    result = match_classified_skills(
        resume_skills,
        required_skills,
        preferred_skills
    )

    print("\n===== HIRELENS SKILL MATCHING =====")

    for key, value in result.items():
        print(f"{key}: {value}")