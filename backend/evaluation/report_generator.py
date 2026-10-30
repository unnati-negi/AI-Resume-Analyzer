# =========================================================
# HIRELENS - EVALUATION REPORT GENERATOR
# =========================================================

import csv
import json
from pathlib import Path


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_DIR = (
    PROJECT_ROOT
    / "backend"
    / "evaluation"
    / "reports"
)


# =========================================================
# GENERATE JSON REPORT
# =========================================================

def generate_json_report(methods):

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "evaluation_results.json"

    with json_path.open("w", encoding="utf-8") as file:

        json.dump(
            methods,
            file,
            indent=4
        )

    return json_path


# =========================================================
# GENERATE SUMMARY CSV
# =========================================================

def generate_summary_csv(methods):

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = REPORT_DIR / "evaluation_summary.csv"

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Method",
            "Threshold",
            "Accuracy",
            "Precision",
            "Recall",
            "F1 Score",
            "True Positive",
            "True Negative",
            "False Positive",
            "False Negative",
            "Total Samples"
        ])

        for method_name, result in methods.items():

            metrics = result.get("metrics", {})

            writer.writerow([
                method_name,
                result.get("threshold", 0),
                metrics.get("accuracy", 0),
                metrics.get("precision", 0),
                metrics.get("recall", 0),
                metrics.get(
                    "f1_score",
                    metrics.get("f1", 0)
                ),
                metrics.get("true_positive", 0),
                metrics.get("true_negative", 0),
                metrics.get("false_positive", 0),
                metrics.get("false_negative", 0),
                metrics.get("total_samples", 0)
            ])

    return csv_path


# =========================================================
# GENERATE INDIVIDUAL PREDICTIONS CSV
# =========================================================

def generate_predictions_csv(methods):

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = (
        REPORT_DIR / "individual_predictions.csv"
    )

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Method",
            "Resume Job ID",
            "Score",
            "Actual Label",
            "Predicted Label",
            "Correct Prediction"
        ])

        for method_name, result in methods.items():

            for item in result.get("details", []):

                writer.writerow([
                    method_name,
                    item.get("id"),
                    item.get("score"),
                    item.get("actual"),
                    item.get("predicted"),
                    item.get("correct")
                ])

    return csv_path


# =========================================================
# MAIN REPORT GENERATOR
# =========================================================

def generate_reports(methods):
    """
    Generate all HireLens evaluation reports.

    Returns the paths of generated reports.
    """

    if not isinstance(methods, dict) or not methods:
        raise ValueError(
            "Evaluation results are empty or invalid."
        )

    json_path = generate_json_report(methods)

    summary_path = generate_summary_csv(methods)

    predictions_path = generate_predictions_csv(methods)

    print("\n===================================")
    print("HIRELENS REPORTS GENERATED")
    print("===================================")

    print("\nReport directory:")
    print(REPORT_DIR)

    print("\nGenerated files:")

    print("1.", json_path.name)
    print("2.", summary_path.name)
    print("3.", predictions_path.name)

    return {
        "json": str(json_path),
        "summary_csv": str(summary_path),
        "predictions_csv": str(predictions_path)
    }


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    print("HireLens Evaluation Report Generator")
    print("Module loaded successfully.")
    print("Function available:", callable(generate_reports))