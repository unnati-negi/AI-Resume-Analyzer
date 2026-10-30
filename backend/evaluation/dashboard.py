# =========================================================
# HIRELENS - EVALUATION DASHBOARD
# =========================================================

import json
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="HireLens Evaluation Dashboard",
    page_icon=None,
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f5f8fa;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.metric-card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

h1, h2, h3 {
    color: #17324d;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD RESULTS
# =========================================================

@st.cache_data
def load_results():

    if not RESULTS_PATH.exists():
        return None

    with RESULTS_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


results = load_results()


# =========================================================
# HEADER
# =========================================================

st.title("HireLens Evaluation Dashboard")

st.write(
    "Performance analysis of resume-job matching methods "
    "using a labeled evaluation dataset."
)

st.divider()


# =========================================================
# CHECK RESULTS
# =========================================================

if not results:

    st.error(
        "Evaluation results were not found. "
        "Run the evaluation module first."
    )

    st.code(
        "python -m backend.evaluation.evaluator"
    )

    st.stop()


# =========================================================
# PREPARE DATA
# =========================================================

summary_data = []

prediction_data = []

for method, result in results.items():

    metrics = result.get("metrics", {})

    summary_data.append({
        "Method": method,
        "Accuracy": metrics.get("accuracy", 0) * 100,
        "Precision": metrics.get("precision", 0) * 100,
        "Recall": metrics.get("recall", 0) * 100,
        "F1 Score": metrics.get(
            "f1_score",
            metrics.get("f1", 0)
        ) * 100,
        "Threshold": result.get("threshold", 0),
        "Samples": metrics.get("total_samples", 0)
    })

    for item in result.get("details", []):

        prediction_data.append({
            "Method": method,
            "ID": item.get("id"),
            "Score": item.get("score"),
            "Actual": item.get("actual"),
            "Predicted": item.get("predicted"),
            "Correct": item.get("correct")
        })


summary_df = pd.DataFrame(summary_data)

predictions_df = pd.DataFrame(prediction_data)


# =========================================================
# OVERVIEW METRICS
# =========================================================

st.subheader("Evaluation Overview")

total_methods = len(summary_df)

total_samples = (
    summary_df["Samples"].max()
    if not summary_df.empty else 0
)

best_accuracy = (
    summary_df["Accuracy"].max()
    if not summary_df.empty else 0
)

best_f1 = (
    summary_df["F1 Score"].max()
    if not summary_df.empty else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Dataset Size",
    int(total_samples)
)

col2.metric(
    "Methods Evaluated",
    total_methods
)

col3.metric(
    "Best Accuracy",
    f"{best_accuracy:.2f}%"
)

col4.metric(
    "Best F1 Score",
    f"{best_f1:.2f}%"
)

st.divider()


# =========================================================
# MODEL COMPARISON
# =========================================================

st.subheader("Model Performance Comparison")

metric_selection = st.selectbox(
    "Select Evaluation Metric",
    [
        "Accuracy",
        "Precision",
        "Recall",
        "F1 Score"
    ]
)

fig = px.bar(
    summary_df,
    x="Method",
    y=metric_selection,
    color="Method",
    text=metric_selection,
    title=f"{metric_selection} Comparison"
)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig.update_layout(
    yaxis_title="Score (%)",
    xaxis_title="Matching Method",
    yaxis_range=[0, 115],
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =========================================================
# PRECISION, RECALL AND F1
# =========================================================

st.subheader("Detailed Performance Metrics")

performance_df = summary_df.melt(
    id_vars="Method",
    value_vars=[
        "Precision",
        "Recall",
        "F1 Score"
    ],
    var_name="Metric",
    value_name="Score"
)

fig = px.bar(
    performance_df,
    x="Method",
    y="Score",
    color="Metric",
    barmode="group",
    title="Precision, Recall and F1-score"
)

fig.update_layout(
    yaxis_title="Score (%)",
    yaxis_range=[0, 115]
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =========================================================
# CONFUSION MATRIX
# =========================================================

st.subheader("Confusion Matrix Analysis")

selected_method = st.selectbox(
    "Choose Matching Method",
    list(results.keys())
)

selected_result = results[selected_method]

metrics = selected_result.get("metrics", {})

confusion_matrix = [
    [
        metrics.get("true_negative", 0),
        metrics.get("false_positive", 0)
    ],
    [
        metrics.get("false_negative", 0),
        metrics.get("true_positive", 0)
    ]
]

fig = go.Figure(
    data=go.Heatmap(
        z=confusion_matrix,
        x=["Predicted Irrelevant", "Predicted Relevant"],
        y=["Actual Irrelevant", "Actual Relevant"],
        text=confusion_matrix,
        texttemplate="%{text}",
        colorscale="Blues",
        showscale=True
    )
)

fig.update_layout(
    title=f"{selected_method} Confusion Matrix",
    xaxis_title="Predicted Class",
    yaxis_title="Actual Class"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =========================================================
# INDIVIDUAL PREDICTIONS
# =========================================================

st.subheader("Individual Prediction Results")

if not predictions_df.empty:

    method_filter = st.selectbox(
        "Filter by Method",
        ["All Methods"] + list(results.keys())
    )

    if method_filter != "All Methods":

        filtered_df = predictions_df[
            predictions_df["Method"] == method_filter
        ]

    else:

        filtered_df = predictions_df

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# COMPLETE SUMMARY TABLE
# =========================================================

st.subheader("Evaluation Summary")

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# DOWNLOAD REPORT
# =========================================================

st.subheader("Download Evaluation Results")

col1, col2 = st.columns(2)

with col1:

    st.download_button(
        "Download JSON Report",
        data=json.dumps(results, indent=4),
        file_name="hirelens_evaluation.json",
        mime="application/json"
    )

with col2:

    st.download_button(
        "Download CSV Summary",
        data=summary_df.to_csv(index=False),
        file_name="hirelens_evaluation_summary.csv",
        mime="text/csv"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "HireLens | Resume Analysis and Job Matching Evaluation"
)