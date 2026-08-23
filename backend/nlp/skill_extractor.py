import re

from .skills import SKILLS


def normalize_text(text):
    """
    Convert text to lowercase and normalize spaces.
    """

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def extract_skills(text):
    """
    Extract known skills from resume text.
    """

    normalized_text = normalize_text(text)

    found_skills = []


    for skill in SKILLS:

        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, normalized_text):

            found_skills.append(skill)


    return sorted(
        list(set(found_skills))
    )