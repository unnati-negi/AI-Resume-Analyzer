
# =========================================================
# HIRELENS
# Semantic Matcher
# =========================================================

import re
from functools import lru_cache


# =========================================================
# MODEL LOADING
# =========================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def load_semantic_model():
    """
    Load the sentence-transformer model once and reuse it.
    """

    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


# =========================================================
# TEXT PREPROCESSING
# =========================================================

def clean_text(text):
    """Clean and normalize input text."""

    if not isinstance(text, str):
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_into_sentences(text):
    """Split text into basic sentence-like segments."""

    text = clean_text(text)

    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# =========================================================
# SEMANTIC SIMILARITY
# =========================================================

def calculate_similarity(text1, text2):
    """
    Calculate semantic similarity between two text strings.

    Returns a similarity percentage from 0 to 100.

    This percentage measures embedding similarity; it is
    not a probability that the candidate is qualified.
    """

    text1 = clean_text(text1)
    text2 = clean_text(text2)

    if not text1 or not text2:
        return 0.0

    model = load_semantic_model()

    embeddings = model.encode(
        [text1, text2],
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    # Normalized embeddings allow cosine similarity
    # to be calculated using the dot product.
    similarity = float(embeddings[0] @ embeddings[1])

    # Cosine similarity can be negative, so map it to
    # a bounded 0-100 display scale.
    similarity_percentage = (
        max(0.0, min(1.0, similarity)) * 100
    )

    return round(similarity_percentage, 2)


# =========================================================
# SENTENCE-LEVEL MATCHING
# =========================================================

def match_resume_sentences(resume_text, job_description):
    """
    Find the most semantically similar resume sentence
    for each job-description sentence.

    Useful for explaining which resume statements
    relate to individual job requirements.
    """

    resume_sentences = split_into_sentences(resume_text)
    job_sentences = split_into_sentences(job_description)

    if not resume_sentences or not job_sentences:
        return {
            "sentence_matches": [],
            "average_similarity": 0.0
        }

    model = load_semantic_model()

    # Encode each sentence only once per call.
    resume_embeddings = model.encode(
        resume_sentences,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    job_embeddings = model.encode(
        job_sentences,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    # Each row contains similarities between one JD
    # sentence and all resume sentences.
    similarity_matrix = job_embeddings @ resume_embeddings.T

    sentence_matches = []

    for index, job_sentence in enumerate(job_sentences):

        best_index = int(
            similarity_matrix[index].argmax()
        )

        raw_similarity = float(
            similarity_matrix[index, best_index]
        )

        similarity_percentage = round(
            max(0.0, min(1.0, raw_similarity)) * 100,
            2
        )

        sentence_matches.append({
            "job_sentence": job_sentence,
            "resume_sentence": resume_sentences[best_index],
            "similarity": similarity_percentage
        })

    average_similarity = round(
        sum(
            item["similarity"]
            for item in sentence_matches
        ) / len(sentence_matches),
        2
    )

    return {
        "sentence_matches": sentence_matches,
        "average_similarity": average_similarity
    }


# =========================================================
# COMPLETE SEMANTIC ANALYSIS
# =========================================================

def analyze_semantic_match(resume_text, job_description):
    """
    Perform semantic matching between a resume and a
    job description.

    Returns:
        overall semantic similarity
        sentence-level matches
        average sentence similarity
    """

    resume_text = clean_text(resume_text)
    job_description = clean_text(job_description)

    if not resume_text or not job_description:
        return {
            "semantic_similarity": 0.0,
            "sentence_matches": [],
            "average_sentence_similarity": 0.0,
            "status": "insufficient_text"
        }

    overall_similarity = calculate_similarity(
        resume_text,
        job_description
    )

    sentence_result = match_resume_sentences(
        resume_text,
        job_description
    )

    return {
        "semantic_similarity": overall_similarity,
        "sentence_matches": sentence_result[
            "sentence_matches"
        ],
        "average_sentence_similarity": sentence_result[
            "average_similarity"
        ],
        "status": "success",
        "model": MODEL_NAME
    }


# =========================================================
# STANDALONE TEST
# =========================================================

if __name__ == "__main__":

    resume_text = """
    Developed predictive machine learning models using Python.
    Built data processing pipelines and evaluated model performance.
    Created REST APIs using Flask.
    """

    job_description = """
    Experience developing predictive analytics solutions.
    Ability to prepare data and assess machine learning models.
    Knowledge of backend API development.
    """

    try:
        result = analyze_semantic_match(
            resume_text,
            job_description
        )

        print("\n===== HIRELENS SEMANTIC MATCHING =====")

        print(
            "Overall Semantic Similarity:",
            result["semantic_similarity"],
            "%"
        )

        print(
            "Average Sentence Similarity:",
            result["average_sentence_similarity"],
            "%"
        )

        print("\n===== SENTENCE MATCHES =====")

        for item in result["sentence_matches"]:

            print("\nJob requirement:")
            print(item["job_sentence"])

            print("\nRelated resume sentence:")
            print(item["resume_sentence"])

            print(
                "Similarity:",
                item["similarity"],
                "%"
            )

    except ImportError:
        print(
            "Missing dependency. Install sentence-transformers "
            "before running this module."
        )
