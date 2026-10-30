
# =========================================================
# HIRELENS
# Baseline Matching Methods
# =========================================================

import re


# =========================================================
# TEXT PREPROCESSING
# =========================================================

def clean_text(text):
    """Normalize text for baseline matching."""

    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================================
# BASELINE 1: KEYWORD MATCHING
# =========================================================

def keyword_match(resume_text, job_description):
    """
    Calculate the percentage of unique job-description
    keywords found in the resume.

    This is a simple word-overlap baseline, not the same
    as the project's structured skill matcher.
    """

    resume_text = clean_text(resume_text)
    job_description = clean_text(job_description)

    if not resume_text or not job_description:
        return {
            "method": "keyword",
            "score": 0.0,
            "matched_terms": [],
            "missing_terms": []
        }

    # Extract words containing at least two characters.
    resume_terms = set(
        re.findall(r"\b[a-z0-9+#.]+\b", resume_text)
    )

    job_terms = set(
        re.findall(r"\b[a-z0-9+#.]+\b", job_description)
    )

    # Remove common words that add little value.
    stop_words = {
        "the", "and", "for", "with", "from",
        "are", "was", "were", "this", "that",
        "have", "has", "had", "will", "you",
        "your", "our", "their", "into", "using",
        "ability", "experience", "knowledge",
        "skills", "work", "working"
    }

    job_terms -= stop_words
    resume_terms -= stop_words

    matched = resume_terms & job_terms
    missing = job_terms - resume_terms

    score = (
        len(matched) / len(job_terms) * 100
        if job_terms else 0.0
    )

    return {
        "method": "keyword",
        "score": round(score, 2),
        "matched_terms": sorted(matched),
        "missing_terms": sorted(missing)
    }


# =========================================================
# BASELINE 2: TF-IDF COSINE SIMILARITY
# =========================================================

def tfidf_match(resume_text, job_description):
    """
    Compare resume and job-description text using
    TF-IDF vectors and cosine similarity.
    """

    resume_text = clean_text(resume_text)
    job_description = clean_text(job_description)

    if not resume_text or not job_description:
        return {
            "method": "tfidf",
            "score": 0.0,
            "status": "insufficient_text"
        }

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

    except ImportError as exc:
        raise ImportError(
            "Install scikit-learn to use the TF-IDF baseline: "
            "python -m pip install scikit-learn"
        ) from exc

    vectorizer = TfidfVectorizer()

    try:
        vectors = vectorizer.fit_transform([
            resume_text,
            job_description
        ])

    except ValueError:
        # For example, both texts may contain only
        # tokens that the vectorizer cannot use.
        return {
            "method": "tfidf",
            "score": 0.0,
            "status": "no_comparable_terms"
        }

    similarity = cosine_similarity(
        vectors[0:1],
        vectors[1:2]
    )[0][0]

    return {
        "method": "tfidf",
        "score": round(float(similarity) * 100, 2),
        "status": "success"
    }


# =========================================================
# RUN ALL BASELINES
# =========================================================

def compare_baselines(resume_text, job_description):
    """
    Run keyword and TF-IDF baselines on the same inputs.
    """

    keyword_result = keyword_match(
        resume_text,
        job_description
    )

    tfidf_result = tfidf_match(
        resume_text,
        job_description
    )

    return {
        "keyword_matching": keyword_result,
        "tfidf_matching": tfidf_result
    }


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    resume_text = """
    Developed machine learning models using Python.
    Built REST APIs with Flask and worked with SQL databases.
    """

    job_description = """
    We require Python programming, machine learning,
    Flask API development, and SQL database experience.
    """

    results = compare_baselines(
        resume_text,
        job_description
    )

    print("\n===== HIRELENS BASELINE EVALUATION =====")

    for method, result in results.items():

        print(f"\n{method.upper()}")

        for key, value in result.items():
            print(f"{key}: {value}")
