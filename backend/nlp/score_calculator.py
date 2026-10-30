# =========================================================
# HIRELENS
# Match Score Calculator
# =========================================================


# =========================================================
# SCORE CALCULATION
# =========================================================

def calculate_match_score(match_result):
    """
    Calculate an explainable resume-job match score.

    The score is based on:
        - Required skill match
        - Preferred skill match

    The actual matching is performed by skill_matcher.py.
    This module is responsible only for scoring and explanation.
    """

    required_percentage = match_result.get(
        "required_match_percentage",
        0
    )

    preferred_percentage = match_result.get(
        "preferred_match_percentage",
        0
    )

    required_count = match_result.get(
        "total_required",
        0
    )

    preferred_count = match_result.get(
        "total_preferred",
        0
    )

    # -----------------------------------------------------
    # Determine weights
    # -----------------------------------------------------

    if required_count > 0 and preferred_count > 0:

        required_weight = 0.80
        preferred_weight = 0.20

    elif required_count > 0:

        required_weight = 1.00
        preferred_weight = 0.00

    elif preferred_count > 0:

        required_weight = 0.00
        preferred_weight = 1.00

    else:

        required_weight = 0.00
        preferred_weight = 0.00

    # -----------------------------------------------------
    # Calculate weighted components
    # -----------------------------------------------------

    required_contribution = (
        required_percentage
        * required_weight
    )

    preferred_contribution = (
        preferred_percentage
        * preferred_weight
    )

    overall_score = (
        required_contribution
        + preferred_contribution
    )

    # -----------------------------------------------------
    # Generate explanation
    # -----------------------------------------------------

    explanation = []

    if required_count > 0:

        explanation.append({
            "component": "Required Skills",
            "score": round(required_percentage, 2),
            "weight": round(required_weight * 100, 2),
            "contribution": round(
                required_contribution,
                2
            ),
            "description":
                "Measures how many required job skills "
                "are present in the resume."
        })

    if preferred_count > 0:

        explanation.append({
            "component": "Preferred Skills",
            "score": round(preferred_percentage, 2),
            "weight": round(preferred_weight * 100, 2),
            "contribution": round(
                preferred_contribution,
                2
            ),
            "description":
                "Measures how many preferred job skills "
                "are present in the resume."
        })

    # -----------------------------------------------------
    # Match interpretation
    # -----------------------------------------------------

    if overall_score >= 80:

        interpretation = "Strong Match"

    elif overall_score >= 60:

        interpretation = "Good Match"

    elif overall_score >= 40:

        interpretation = "Moderate Match"

    else:

        interpretation = "Low Match"

    # -----------------------------------------------------
    # Return complete scoring result
    # -----------------------------------------------------

    return {

        "overall_score": round(
            overall_score,
            2
        ),

        "interpretation":
            interpretation,

        "required_skill_score":
            round(
                required_percentage,
                2
            ),

        "preferred_skill_score":
            round(
                preferred_percentage,
                2
            ),

        "required_weight":
            round(
                required_weight * 100,
                2
            ),

        "preferred_weight":
            round(
                preferred_weight * 100,
                2
            ),

        "required_contribution":
            round(
                required_contribution,
                2
            ),

        "preferred_contribution":
            round(
                preferred_contribution,
                2
            ),

        "explanation":
            explanation,

        "matched_skills":
            match_result.get(
                "matched_skills",
                []
            ),

        "missing_skills":
            match_result.get(
                "missing_skills",
                []
            ),

        "matched_required_skills":
            match_result.get(
                "matched_required_skills",
                []
            ),

        "missing_required_skills":
            match_result.get(
                "missing_required_skills",
                []
            ),

        "matched_preferred_skills":
            match_result.get(
                "matched_preferred_skills",
                []
            ),

        "missing_preferred_skills":
            match_result.get(
                "missing_preferred_skills",
                []
            )
    }


# =========================================================
# COMPLETE SCORING PIPELINE
# =========================================================

def generate_score(match_result):
    """
    Main entry point for generating the explainable
    resume-job compatibility score.
    """

    if not match_result:

        return {
            "overall_score": 0,
            "interpretation": "No Match",
            "required_skill_score": 0,
            "preferred_skill_score": 0,
            "required_weight": 0,
            "preferred_weight": 0,
            "required_contribution": 0,
            "preferred_contribution": 0,
            "explanation": [],
            "matched_skills": [],
            "missing_skills": [],
            "matched_required_skills": [],
            "missing_required_skills": [],
            "matched_preferred_skills": [],
            "missing_preferred_skills": []
        }

    return calculate_match_score(
        match_result
    )


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    sample_match_result = {

        "required_match_percentage": 80.0,

        "preferred_match_percentage": 33.33,

        "total_required": 5,

        "total_preferred": 3,

        "matched_skills": [
            "docker",
            "flask",
            "git",
            "python",
            "sql"
        ],

        "missing_skills": [
            "aws",
            "react",
            "rest api"
        ],

        "matched_required_skills": [
            "flask",
            "git",
            "python",
            "sql"
        ],

        "missing_required_skills": [
            "rest api"
        ],

        "matched_preferred_skills": [
            "docker"
        ],

        "missing_preferred_skills": [
            "aws",
            "react"
        ]
    }

    result = generate_score(
        sample_match_result
    )

    print("\n===== HIRELENS MATCH SCORE =====")

    print(
        "Overall Score:",
        result["overall_score"],
        "%"
    )

    print(
        "Interpretation:",
        result["interpretation"]
    )

    print(
        "\nRequired Skill Score:",
        result["required_skill_score"],
        "%"
    )

    print(
        "Required Weight:",
        result["required_weight"],
        "%"
    )

    print(
        "Required Contribution:",
        result["required_contribution"]
    )

    print(
        "\nPreferred Skill Score:",
        result["preferred_skill_score"],
        "%"
    )

    print(
        "Preferred Weight:",
        result["preferred_weight"],
        "%"
    )

    print(
        "Preferred Contribution:",
        result["preferred_contribution"]
    )

    print("\n===== EXPLANATION =====")

    for item in result["explanation"]:

        print(
            f"{item['component']}: "
            f"{item['score']}%"
        )

        print(
            f"Weight: {item['weight']}%"
        )

        print(
            f"Contribution: "
            f"{item['contribution']}"
        )

        print(
            f"Description: "
            f"{item['description']}"
        )