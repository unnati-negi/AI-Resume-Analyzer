
# =========================================================
# HIRELENS
# Evaluation Metrics
# =========================================================

def calculate_metrics(y_true, y_pred):
    """
    Calculate classification evaluation metrics.

    y_true: Actual labels (0 or 1).
    y_pred: Predicted labels (0 or 1).

    1 = relevant/match
    0 = not relevant/non-match
    """

    if len(y_true) != len(y_pred):
        raise ValueError(
            "y_true and y_pred must have the same length."
        )

    if not y_true:
        raise ValueError(
            "Evaluation data cannot be empty."
        )

    if any(label not in (0, 1) for label in y_true):
        raise ValueError("y_true labels must be 0 or 1.")

    if any(label not in (0, 1) for label in y_pred):
        raise ValueError("y_pred labels must be 0 or 1.")

    true_positive = sum(
        actual == 1 and predicted == 1
        for actual, predicted in zip(y_true, y_pred)
    )

    true_negative = sum(
        actual == 0 and predicted == 0
        for actual, predicted in zip(y_true, y_pred)
    )

    false_positive = sum(
        actual == 0 and predicted == 1
        for actual, predicted in zip(y_true, y_pred)
    )

    false_negative = sum(
        actual == 1 and predicted == 0
        for actual, predicted in zip(y_true, y_pred)
    )

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive else 0.0
    )

    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative else 0.0
    )

    f1_score = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    accuracy = (
        (true_positive + true_negative) / len(y_true)
    )

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1_score, 4),
        "true_positive": true_positive,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "total_samples": len(y_true)
    }


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    # Illustrative labels for testing the metric functions.
    # Replace these with real, independently labeled
    # resume-job relevance examples for actual evaluation.

    actual_labels = [1, 1, 0, 1, 0, 0, 1, 0]

    predicted_labels = [1, 1, 0, 0, 0, 1, 1, 0]

    results = calculate_metrics(
        actual_labels,
        predicted_labels
    )

    print("\n===== HIRELENS EVALUATION METRICS =====")

    for metric, value in results.items():
        print(f"{metric}: {value}")
