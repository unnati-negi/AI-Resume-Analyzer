# =========================================================
# HIRELENS
# Recommendation Engine
# =========================================================


# =========================================================
# SKILL LEARNING SUGGESTIONS
# =========================================================

SKILL_SUGGESTIONS = {

    "python":
        "Strengthen Python programming through projects "
        "in automation, data processing, or backend development.",

    "java":
        "Practice Java with object-oriented programming, "
        "DSA, and backend development projects.",

    "javascript":
        "Build interactive web applications using JavaScript "
        "and modern frontend development practices.",

    "react":
        "Build a React-based frontend project to gain "
        "practical component and state-management experience.",

    "sql":
        "Practice SQL queries, joins, subqueries, indexing, "
        "and database design using practical datasets.",

    "postgresql":
        "Work with PostgreSQL databases and practice "
        "database design, queries, indexing, and optimization.",

    "mongodb":
        "Build an application using MongoDB to gain experience "
        "with document-based database design.",

    "flask":
        "Develop a Flask REST API project involving routing, "
        "database integration, and authentication.",

    "rest api":
        "Build a REST API project covering HTTP methods, "
        "API design, authentication, and JSON responses.",

    "docker":
        "Containerize an existing application with Docker "
        "and practice creating Dockerfiles and images.",

    "aws":
        "Deploy a project on AWS and practice fundamental "
        "cloud services such as EC2, S3, and IAM.",

    "git":
        "Use Git regularly and practice branching, merging, "
        "pull requests, and collaborative workflows.",

    "machine learning":
        "Build an end-to-end machine learning project "
        "covering preprocessing, training, and evaluation.",

    "deep learning":
        "Develop a deep learning project using CNNs, "
        "transfer learning, or another suitable architecture.",

    "nlp":
        "Build an NLP project involving text preprocessing, "
        "embeddings, classification, or information extraction.",

    "scikit-learn":
        "Practice machine learning workflows using "
        "scikit-learn and standard evaluation metrics.",

    "data structures":
        "Practice arrays, linked lists, stacks, queues, trees, "
        "hashing, graphs, and their common algorithms.",

    "algorithms":
        "Practice algorithmic problem solving and analyze "
        "time and space complexity."
}


# =========================================================
# GENERIC RECOMMENDATION
# =========================================================

def generate_skill_recommendation(skill):
    """
    Generate a recommendation for a missing skill.

    Uses a predefined recommendation when available.
    Otherwise returns a general recommendation.
    """

    normalized_skill = skill.lower().strip()

    if normalized_skill in SKILL_SUGGESTIONS:

        return SKILL_SUGGESTIONS[
            normalized_skill
        ]

    return (
        f"Gain practical experience with {skill} "
        f"through a relevant project, course, or "
        f"hands-on implementation."
    )


# =========================================================
# RECOMMENDATION PRIORITY
# =========================================================

def priority_score(priority):
    """
    Convert priority into a numeric value.

    Higher value = higher recommendation priority.
    """

    priorities = {

        "High": 3,

        "Medium": 2,

        "Low": 1
    }

    return priorities.get(
        priority,
        0
    )


# =========================================================
# GENERATE RECOMMENDATIONS
# =========================================================

def generate_recommendations(gap_result):
    """
    Generate actionable recommendations from
    the skill-gap analysis.
    """

    if not gap_result:

        return {
            "recommendations": [],
            "total_recommendations": 0
        }

    skill_gaps = gap_result.get(
        "skill_gaps",
        []
    )

    recommendations = []

    for gap in skill_gaps:

        skill = gap.get(
            "skill",
            ""
        )

        gap_type = gap.get(
            "type",
            "unspecified"
        )

        priority = gap.get(
            "priority",
            "Low"
        )

        if not skill:
            continue

        recommendation = generate_skill_recommendation(
            skill
        )

        recommendations.append({

            "skill": skill,

            "type": gap_type,

            "priority": priority,

            "priority_score":
                priority_score(priority),

            "recommendation":
                recommendation
        })

    # -----------------------------------------------------
    # Highest priority recommendations first
    # -----------------------------------------------------

    recommendations.sort(
        key=lambda item: (
            -item["priority_score"],
            item["skill"]
        )
    )

    return {

        "recommendations":
            recommendations,

        "total_recommendations":
            len(recommendations)
    }


# =========================================================
# GENERATE SUMMARY
# =========================================================

def generate_recommendation_summary(
    recommendation_result
):
    """
    Generate a short summary of recommendations.
    """

    if not recommendation_result:

        return "No recommendations available."

    recommendations = recommendation_result.get(
        "recommendations",
        []
    )

    if not recommendations:

        return (
            "No additional skill recommendations are "
            "required based on the analyzed job description."
        )

    high_priority = [
        item["skill"]
        for item in recommendations
        if item["priority"] == "High"
    ]

    medium_priority = [
        item["skill"]
        for item in recommendations
        if item["priority"] == "Medium"
    ]

    summary = []

    if high_priority:

        summary.append(
            "Focus first on: "
            + ", ".join(high_priority)
        )

    if medium_priority:

        summary.append(
            "Then consider: "
            + ", ".join(medium_priority)
        )

    return " | ".join(summary)


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    sample_gap_result = {

        "skill_gaps": [

            {
                "skill": "rest api",
                "type": "required",
                "priority": "High"
            },

            {
                "skill": "aws",
                "type": "preferred",
                "priority": "Medium"
            },

            {
                "skill": "react",
                "type": "preferred",
                "priority": "Medium"
            }
        ]
    }

    result = generate_recommendations(
        sample_gap_result
    )

    print("\n===== HIRELENS RECOMMENDATIONS =====")

    for item in result["recommendations"]:

        print(
            f"\nSkill: {item['skill']}"
        )

        print(
            f"Type: {item['type']}"
        )

        print(
            f"Priority: {item['priority']}"
        )

        print(
            f"Recommendation: "
            f"{item['recommendation']}"
        )

    print(
        "\n===== SUMMARY ====="
    )

    print(
        generate_recommendation_summary(
            result
        )
    )