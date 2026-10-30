# =========================================================
# HIRELENS
# Skill Gap Analyzer
# =========================================================


# =========================================================
# PRIORITY CALCULATION
# =========================================================

def determine_priority(
    skill_type,
    total_required,
    total_preferred
):
    """
    Determine the priority of a missing skill.

    Required skills are given higher priority than
    preferred skills.
    """

    if skill_type == "required":

        return "High"

    if skill_type == "preferred":

        return "Medium"

    return "Low"


# =========================================================
# SKILL GAP ANALYSIS
# =========================================================

def analyze_skill_gaps(match_result):
    """
    Analyze missing skills from the matching result.

    Required missing skills are treated as high-priority gaps.
    Preferred missing skills are treated as medium-priority gaps.
    """

    if not match_result:

        return {
            "skill_gaps": [],
            "required_gaps": [],
            "preferred_gaps": [],
            "high_priority_gaps": [],
            "medium_priority_gaps": [],
            "low_priority_gaps": [],
            "total_gaps": 0
        }

    missing_required = match_result.get(
        "missing_required_skills",
        []
    )

    missing_preferred = match_result.get(
        "missing_preferred_skills",
        []
    )

    missing_unspecified = match_result.get(
        "missing_unspecified_skills",
        []
    )

    total_required = match_result.get(
        "total_required",
        0
    )

    total_preferred = match_result.get(
        "total_preferred",
        0
    )

    skill_gaps = []

    # -----------------------------------------------------
    # Required skill gaps
    # -----------------------------------------------------

    for skill in missing_required:

        priority = determine_priority(
            "required",
            total_required,
            total_preferred
        )

        skill_gaps.append({

            "skill": skill,

            "type": "required",

            "priority": priority,

            "reason":
                "This skill is required by the job "
                "but was not identified in the resume."
        })

    # -----------------------------------------------------
    # Preferred skill gaps
    # -----------------------------------------------------

    for skill in missing_preferred:

        priority = determine_priority(
            "preferred",
            total_required,
            total_preferred
        )

        skill_gaps.append({

            "skill": skill,

            "type": "preferred",

            "priority": priority,

            "reason":
                "This skill is preferred by the job "
                "but was not identified in the resume."
        })

    # -----------------------------------------------------
    # Unspecified skill gaps
    # -----------------------------------------------------

    for skill in missing_unspecified:

        priority = determine_priority(
            "unspecified",
            total_required,
            total_preferred
        )

        skill_gaps.append({

            "skill": skill,

            "type": "unspecified",

            "priority": priority,

            "reason":
                "This skill appears in the job description "
                "but its requirement level was not explicitly "
                "classified."
        })

    # -----------------------------------------------------
    # Categorize gaps by priority
    # -----------------------------------------------------

    high_priority_gaps = [

        gap["skill"]

        for gap in skill_gaps

        if gap["priority"] == "High"
    ]

    medium_priority_gaps = [

        gap["skill"]

        for gap in skill_gaps

        if gap["priority"] == "Medium"
    ]

    low_priority_gaps = [

        gap["skill"]

        for gap in skill_gaps

        if gap["priority"] == "Low"
    ]

    return {

        "skill_gaps":
            skill_gaps,

        "required_gaps":
            missing_required,

        "preferred_gaps":
            missing_preferred,

        "high_priority_gaps":
            sorted(high_priority_gaps),

        "medium_priority_gaps":
            sorted(medium_priority_gaps),

        "low_priority_gaps":
            sorted(low_priority_gaps),

        "total_gaps":
            len(skill_gaps)
    }


# =========================================================
# GAP SUMMARY
# =========================================================

def generate_gap_summary(gap_result):
    """
    Generate a simple human-readable summary
    of the candidate's skill gaps.
    """

    if not gap_result:

        return "No skill-gap information available."

    total_gaps = gap_result.get(
        "total_gaps",
        0
    )

    high_priority = gap_result.get(
        "high_priority_gaps",
        []
    )

    medium_priority = gap_result.get(
        "medium_priority_gaps",
        []
    )

    low_priority = gap_result.get(
        "low_priority_gaps",
        []
    )

    if total_gaps == 0:

        return (
            "No significant skill gaps were identified "
            "against the analyzed job requirements."
        )

    summary_parts = []

    if high_priority:

        summary_parts.append(
            "High-priority gaps: "
            + ", ".join(high_priority)
        )

    if medium_priority:

        summary_parts.append(
            "Medium-priority gaps: "
            + ", ".join(medium_priority)
        )

    if low_priority:

        summary_parts.append(
            "Low-priority gaps: "
            + ", ".join(low_priority)
        )

    return " | ".join(summary_parts)


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    sample_match_result = {

        "missing_required_skills": [
            "rest api"
        ],

        "missing_preferred_skills": [
            "aws",
            "react"
        ],

        "missing_unspecified_skills": [],

        "total_required": 5,

        "total_preferred": 3
    }

    result = analyze_skill_gaps(
        sample_match_result
    )

    print("\n===== HIRELENS SKILL GAP ANALYSIS =====")

    print(
        "\nTotal Gaps:",
        result["total_gaps"]
    )

    print(
        "\nHigh Priority:",
        result["high_priority_gaps"]
    )

    print(
        "Medium Priority:",
        result["medium_priority_gaps"]
    )

    print(
        "Low Priority:",
        result["low_priority_gaps"]
    )

    print("\n===== GAP DETAILS =====")

    for gap in result["skill_gaps"]:

        print(
            f"{gap['skill']} "
            f"-> {gap['type']} "
            f"-> {gap['priority']}"
        )

        print(
            "Reason:",
            gap["reason"]
        )

    print("\n===== SUMMARY =====")

    print(
        generate_gap_summary(result)
    )