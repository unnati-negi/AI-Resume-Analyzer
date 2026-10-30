# =========================================================
# HIRELENS - EVALUATION VISUALIZER
# =========================================================

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


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

RESULTS_PATH = REPORT_DIR / "evaluation_results.json"

CHART_DIR = REPORT_DIR / "charts"


# =========================================================
# LOAD EVALUATION RESULTS
# =========================================================

def load_results():

    if not RESULTS_PATH.exists():
        raise FileNotFoundError(
            "Evaluation results not found. "
            "Run the evaluator first."
        )

    with RESULTS_PATH.open("r", encoding="utf-8") as file:
        results = json.load(file)

    if not results:
        raise ValueError("Evaluation results are empty.")

    return results


# =========================================================
# ACCURACY COMPARISON
# =========================================================

def plot_accuracy(results):

    methods = list(results.keys())

    accuracies = [
        results[name]["metrics"].get("accuracy", 0) * 100
        for name in methods
    ]

    plt.figure(figsize=(9, 5))

    bars = plt.bar(methods, accuracies)

    plt.title("Accuracy Comparison of Matching Methods")
    plt.xlabel("Matching Method")
    plt.ylabel("Accuracy (%)")
    plt.ylim(0, 110)

    for bar, value in zip(bars, accuracies):

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{value:.2f}%",
            ha="center"
        )

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / "accuracy_comparison.png",
        dpi=300
    )

    plt.close()


# =========================================================
# PRECISION, RECALL AND F1 COMPARISON
# =========================================================

def plot_performance_metrics(results):

    methods = list(results.keys())

    metric_names = [
        "precision",
        "recall",
        "f1_score"
    ]

    metric_values = []

    for metric in metric_names:

        values = []

        for method in methods:

            metrics = results[method]["metrics"]

            if metric == "f1_score":
                value = metrics.get(
                    "f1_score",
                    metrics.get("f1", 0)
                )
            else:
                value = metrics.get(metric, 0)

            values.append(float(value) * 100)

        metric_values.append(values)

    x = np.arange(len(methods))
    width = 0.24

    plt.figure(figsize=(11, 6))

    for index, (name, values) in enumerate(
        zip(
            ["Precision", "Recall", "F1-score"],
            metric_values
        )
    ):

        positions = x + (index - 1) * width

        bars = plt.bar(
            positions,
            values,
            width,
            label=name
        )

        for bar, value in zip(bars, values):

            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{value:.1f}",
                ha="center",
                fontsize=8
            )

    plt.title("Precision, Recall and F1-score Comparison")
    plt.xlabel("Matching Method")
    plt.ylabel("Score (%)")
    plt.xticks(x, methods)
    plt.ylim(0, 115)
    plt.legend()

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / "performance_comparison.png",
        dpi=300
    )

    plt.close()


# =========================================================
# CONFUSION MATRIX
# =========================================================

def plot_confusion_matrices(results):

    for method, result in results.items():

        metrics = result["metrics"]

        tp = metrics.get("true_positive", 0)
        tn = metrics.get("true_negative", 0)
        fp = metrics.get("false_positive", 0)
        fn = metrics.get("false_negative", 0)

        matrix = np.array([
            [tn, fp],
            [fn, tp]
        ])

        plt.figure(figsize=(6, 5))

        plt.imshow(matrix, cmap="Blues")

        plt.title(f"{method} - Confusion Matrix")

        plt.xlabel("Predicted Label")
        plt.ylabel("Actual Label")

        plt.xticks([0, 1], ["Irrelevant", "Relevant"])
        plt.yticks([0, 1], ["Irrelevant", "Relevant"])

        for row in range(2):

            for col in range(2):

                plt.text(
                    col,
                    row,
                    str(matrix[row, col]),
                    ha="center",
                    va="center"
                )

        plt.colorbar()

        plt.tight_layout()

        safe_name = method.lower().replace(" ", "_")

        plt.savefig(
            CHART_DIR / f"{safe_name}_confusion_matrix.png",
            dpi=300
        )

        plt.close()


# =========================================================
# GENERATE ALL CHARTS
# =========================================================

def generate_visualizations():

    CHART_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    results = load_results()

    plot_accuracy(results)

    plot_performance_metrics(results)

    plot_confusion_matrices(results)

    print("\n===================================")
    print("HIRELENS VISUALIZATION COMPLETED")
    print("===================================")

    print("\nCharts saved in:")
    print(CHART_DIR)

    for chart in sorted(CHART_DIR.glob("*.png")):
        print(chart.name)


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    generate_visualizations()