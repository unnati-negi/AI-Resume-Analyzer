# =========================================================
# HIRELENS - EVALUATION RUNNER
# =========================================================

import json
import math
from pathlib import Path

from backend.evaluation.baseline_matcher import (
    keyword_match,
    tfidf_match
)

from backend.evaluation.metrics import calculate_metrics

from backend.evaluation.report_generator import generate_reports

from backend.nlp.skill_extractor import extract_skills
from backend.nlp.job_analyzer import analyze_job_description
from backend.nlp.requirement_classifier import analyze_requirements
from backend.nlp.skill_matcher import (
    match_skills,
    match_classified_skills
)


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "evaluation_dataset"
    / "resume_job_pairs.json"
)

KEYWORD_THRESHOLD = 30.0
TFIDF_THRESHOLD = 20.0
HIRELENS_THRESHOLD = 50.0
SEMANTIC_THRESHOLD = 50.0


# =========================================================
# LOAD DATASET
# =========================================================

def load_dataset(dataset_path=DATASET_PATH):

    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}"
        )

    with dataset_path.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    if not isinstance(dataset, list) or not dataset:
        raise ValueError(
            "Dataset must be a non-empty JSON list."
        )

    required_fields = {
        "id",
        "resume_text",
        "job_description",
        "relevant"
    }

    seen_ids = set()

    for index, item in enumerate(dataset, start=1):

        if not isinstance(item, dict):
            raise ValueError(
                f"Dataset row {index} must be an object."
            )

        missing = required_fields - item.keys()

        if missing:
            raise ValueError(
                f"Dataset row {index} is missing: {sorted(missing)}"
            )

        if item["id"] in seen_ids:
            raise ValueError(
                f"Duplicate dataset ID: {item['id']}"
            )

        seen_ids.add(item["id"])

        if not isinstance(item["resume_text"], str):
            raise ValueError(
                f"Resume text in row {index} must be a string."
            )

        if not isinstance(item["job_description"], str):
            raise ValueError(
                f"Job description in row {index} must be a string."
            )

        if not item["resume_text"].strip():
            raise ValueError(
                f"Resume text in row {index} is empty."
            )

        if not item["job_description"].strip():
            raise ValueError(
                f"Job description in row {index} is empty."
            )

        if (
            type(item["relevant"]) is not int
            or item["relevant"] not in (0, 1)
        ):
            raise ValueError(
                f"Relevant label in row {index} must be 0 or 1."
            )

    return dataset


# =========================================================
# HIRELENS REQUIREMENT-AWARE MATCHING
# =========================================================

def hirelens_match(resume_text, job_description):

    resume_skills = extract_skills(resume_text)

    job_result = analyze_job_description(job_description)

    job_skills = job_result.get("skills", [])

    requirements = analyze_requirements(
        job_description,
        job_skills
    )

    matching = match_classified_skills(
        resume_skills,
        requirements.get("required_skills", []),
        requirements.get("preferred_skills", []),
        requirements.get("unspecified_skills", [])
    )

    required_count = matching.get("total_required", 0)
    preferred_count = matching.get("total_preferred", 0)

    if required_count or preferred_count:

        score = matching.get(
            "overall_match_percentage", 0
        )

    else:

        basic_result = match_skills(
            resume_skills,
            job_skills
        )

        score = basic_result.get(
            "match_percentage", 0
        )

    return {
        "score": round(float(score), 2),
        "matched_skills": matching.get("matched_skills", []),
        "missing_skills": matching.get("missing_skills", [])
    }


# =========================================================
# EVALUATE ONE METHOD
# =========================================================

def evaluate_method(
    dataset,
    scoring_function,
    threshold,
    score_key="score"
):

    actual_labels = []
    predicted_labels = []
    detailed_results = []

    for item in dataset:

        result = scoring_function(
            item["resume_text"],
            item["job_description"]
        )

        if score_key not in result:
            raise KeyError(
                f"Scoring function did not return {score_key}."
            )

        score = float(result[score_key])

        if not math.isfinite(score):
            raise ValueError(
                f"Invalid score for dataset ID {item['id']}."
            )

        prediction = int(score >= threshold)

        actual_labels.append(item["relevant"])
        predicted_labels.append(prediction)

        detailed_results.append({
            "id": item["id"],
            "actual": item["relevant"],
            "predicted": prediction,
            "score": round(score, 2),
            "correct": prediction == item["relevant"]
        })

    metrics = calculate_metrics(
        actual_labels,
        predicted_labels
    )

    return {
        "threshold": threshold,
        "metrics": metrics,
        "details": detailed_results
    }


# =========================================================
# SEMANTIC MATCHING
# =========================================================

def semantic_match(resume_text, job_description):

    from backend.nlp.semantic_matcher import (
        analyze_semantic_match
    )

    result = analyze_semantic_match(
        resume_text,
        job_description
    )

    if result.get("status") == "unavailable":
        raise RuntimeError(
            "Semantic model is unavailable."
        )

    similarity = result.get("semantic_similarity")

    if similarity is None:
        raise ValueError(
            "Semantic similarity score was not returned."
        )

    similarity = float(similarity)

    if not math.isfinite(similarity):
        raise ValueError(
            "Invalid semantic similarity score."
        )

    if 0 <= similarity <= 1:
        similarity *= 100

    if not 0 <= similarity <= 100:
        raise ValueError(
            "Semantic score must be between 0 and 100."
        )

    return {
        "score": round(similarity, 2)
    }


# =========================================================
# RUN EVALUATION
# =========================================================

def run_evaluation():

    dataset = load_dataset()

    methods = {}

    print("\n===================================")
    print("HIRELENS - MODEL EVALUATION")
    print("===================================")

    print("Dataset size:", len(dataset))

    # -----------------------------------------------------
    # 1. KEYWORD MATCHING
    # -----------------------------------------------------

    methods["Keyword"] = evaluate_method(
        dataset,
        keyword_match,
        KEYWORD_THRESHOLD
    )

    # -----------------------------------------------------
    # 2. TF-IDF MATCHING
    # -----------------------------------------------------

    methods["TF-IDF"] = evaluate_method(
        dataset,
        tfidf_match,
        TFIDF_THRESHOLD
    )

    # -----------------------------------------------------
    # 3. HIRELENS MATCHING
    # -----------------------------------------------------

    methods["HireLens"] = evaluate_method(
        dataset,
        hirelens_match,
        HIRELENS_THRESHOLD
    )

    # -----------------------------------------------------
    # 4. SEMANTIC MATCHING
    # -----------------------------------------------------

    try:

        methods["Semantic"] = evaluate_method(
            dataset,
            semantic_match,
            SEMANTIC_THRESHOLD
        )

    except Exception as error:

        print("\nSemantic evaluation skipped:", error)

    # -----------------------------------------------------
    # DISPLAY RESULTS
    # -----------------------------------------------------

    for method_name, result in methods.items():

        print("\n-----------------------------------")
        print("METHOD:", method_name)
        print("-----------------------------------")

        print("Threshold:", result["threshold"])

        print("\nEvaluation metrics:")

        for metric, value in result["metrics"].items():
            print(f"{metric}: {value}")

        print("\nIndividual predictions:")

        for item in result["details"]:

            print(
                f"ID {item['id']} | "
                f"Score: {item['score']}% | "
                f"Actual: {item['actual']} | "
                f"Predicted: {item['predicted']} | "
                f"Correct: {item['correct']}"
            )

    # -----------------------------------------------------
    # COMPARISON TABLE
    # -----------------------------------------------------

    print("\n===================================")
    print("HIRELENS - METHOD COMPARISON")
    print("===================================")

    print(
        f"{'Method':<15}"
        f"{'Accuracy':<12}"
        f"{'Precision':<12}"
        f"{'Recall':<12}"
        f"{'F1 Score':<12}"
    )

    print("-" * 63)

    for name, result in methods.items():

        metrics = result["metrics"]

        print(
            f"{name:<15}"
            f"{metrics.get('accuracy', 0):<12.4f}"
            f"{metrics.get('precision', 0):<12.4f}"
            f"{metrics.get('recall', 0):<12.4f}"
            f"{metrics.get('f1_score', metrics.get('f1', 0)):<12.4f}"
        )

    # -----------------------------------------------------
    # GENERATE REPORTS
    # -----------------------------------------------------

    print("\nGenerating evaluation reports...")

    report_paths = generate_reports(methods)

    print("\nReports generated successfully.")

    for report_name, report_path in report_paths.items():
        print(f"{report_name}: {report_path}")

    return methods


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    run_evaluation()