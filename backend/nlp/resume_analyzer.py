import re
import spacy


# Load spaCy English model
nlp = spacy.load("en_core_web_sm")


# ---------------------------------------------------------
# Contact Information
# ---------------------------------------------------------

def extract_email(text):
    """Extract email address from resume text."""

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    match = re.search(pattern, text)

    return match.group(0) if match else ""


def extract_phone(text):
    """Extract Indian phone number from resume text."""

    pattern = r"(?:\+91[\s-]?)?[6-9]\d{9}\b"

    match = re.search(pattern, text)

    return match.group(0) if match else ""


def extract_linkedin(text):
    """Extract LinkedIn profile URL."""

    pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9._-]+"

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(0) if match else ""


def extract_github(text):
    """Extract GitHub profile URL."""

    pattern = r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9._-]+"

    match = re.search(pattern, text, re.IGNORECASE)

    return match.group(0) if match else ""


# ---------------------------------------------------------
# Name Extraction
# ---------------------------------------------------------

def extract_name(text):
    """
    Extract a probable candidate name.

    The first few non-empty lines of a resume commonly
    contain the candidate's name.
    """

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return ""

    # Check the first few lines for a likely name
    for line in lines[:5]:

        # Ignore lines containing common resume/contact information
        if any(char.isdigit() for char in line):
            continue

        if "@" in line:
            continue

        if "linkedin" in line.lower():
            continue

        if "github" in line.lower():
            continue

        # Avoid obvious section headings
        if line.upper() in {
            "RESUME",
            "CURRICULUM VITAE",
            "CV",
            "PROFILE",
            "SUMMARY",
            "OBJECTIVE"
        }:
            continue

        words = line.split()

        # A reasonable name usually has 2-4 words
        if 2 <= len(words) <= 4:

            if all(word.replace(".", "").isalpha() for word in words):
                return line

    return ""


# ---------------------------------------------------------
# Section Extraction
# ---------------------------------------------------------

def extract_section(text, section_names):
    """
    Extract text belonging to a resume section.

    Example:
        EDUCATION
        B.Tech ...
        Class XII ...

        EXPERIENCE
        Software Intern ...

    The function stops when another major section begins.
    """

    lines = text.splitlines()

    section_start = -1

    # Find the requested section
    for i, line in enumerate(lines):

        cleaned = line.strip().lower()

        if cleaned in [section.lower() for section in section_names]:
            section_start = i + 1
            break

    if section_start == -1:
        return ""

    # Common resume section headings
    all_sections = {
        "education",
        "experience",
        "work experience",
        "professional experience",
        "projects",
        "academic projects",
        "certifications",
        "certificates",
        "skills",
        "technical skills",
        "achievements",
        "awards",
        "languages",
        "interests",
        "summary",
        "objective",
        "profile",
        "internship",
        "internships"
    }

    section_lines = []

    for line in lines[section_start:]:

        cleaned = line.strip().lower()

        if cleaned in all_sections:
            break

        if line.strip():
            section_lines.append(line.strip())

    return "\n".join(section_lines)


# ---------------------------------------------------------
# Resume Sections
# ---------------------------------------------------------

def extract_education(text):
    """Extract education section."""

    return extract_section(
        text,
        [
            "Education",
            "Educational Qualification",
            "Academic Qualification",
            "Academic Background"
        ]
    )


def extract_experience(text):
    """Extract professional/work experience."""

    return extract_section(
        text,
        [
            "Experience",
            "Work Experience",
            "Professional Experience",
            "Internship",
            "Internships"
        ]
    )


def extract_projects(text):
    """Extract projects section."""

    return extract_section(
        text,
        [
            "Projects",
            "Academic Projects",
            "Personal Projects",
            "Project"
        ]
    )


def extract_certifications(text):
    """Extract certifications section."""

    return extract_section(
        text,
        [
            "Certifications",
            "Certificates",
            "Certification"
        ]
    )


# ---------------------------------------------------------
# Main Resume Analyzer
# ---------------------------------------------------------

def analyze_resume(text):
    """
    Analyze resume text using spaCy and structured
    information extraction.

    Returns:
        dict containing NLP information and
        structured resume information.
    """

    doc = nlp(text)

    # -----------------------------------------------------
    # Sentence Extraction
    # -----------------------------------------------------

    sentences = []

    for sentence in doc.sents:

        cleaned_sentence = sentence.text.strip()

        if cleaned_sentence:
            sentences.append(cleaned_sentence)

    # -----------------------------------------------------
    # Named Entity Extraction
    # -----------------------------------------------------

    entities = []

    for entity in doc.ents:

        entities.append({
            "text": entity.text,
            "label": entity.label_
        })

    # -----------------------------------------------------
    # Token Extraction
    # -----------------------------------------------------

    tokens = []

    for token in doc:

        if not token.is_space and not token.is_punct:

            tokens.append({
                "text": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_
            })

    # -----------------------------------------------------
    # Structured Resume Information
    # -----------------------------------------------------

    name = extract_name(text)

    email = extract_email(text)

    phone = extract_phone(text)

    linkedin = extract_linkedin(text)

    github = extract_github(text)

    education = extract_education(text)

    experience = extract_experience(text)

    projects = extract_projects(text)

    certifications = extract_certifications(text)

    # -----------------------------------------------------
    # Final Result
    # -----------------------------------------------------

    return {

        # Existing NLP information
        "sentences": sentences,
        "entities": entities,
        "tokens": tokens,
        "word_count": len(doc),

        # Structured resume information
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "education": education,
        "experience": experience,
        "projects": projects,
        "certifications": certifications
    }


# ---------------------------------------------------------
# Standalone Test
# ---------------------------------------------------------

if __name__ == "__main__":

    sample_text = """
    Unnati Negi
    unnati@example.com
    +91 9876543210
    linkedin.com/in/unnati
    github.com/unnati

    EDUCATION

    B.Tech in Computer Science and Engineering
    2023 - Present

    EXPERIENCE

    Software Development Intern
    Developed web applications using Python and Flask.

    PROJECTS

    AI Resume Analyzer
    Developed an NLP-based resume analysis system.

    CERTIFICATIONS

    Python Programming Certificate
    """

    result = analyze_resume(sample_text)

    print("\n===== RESUME INFORMATION =====")

    print("Name:", result["name"])
    print("Email:", result["email"])
    print("Phone:", result["phone"])
    print("LinkedIn:", result["linkedin"])
    print("GitHub:", result["github"])

    print("\n===== EDUCATION =====")
    print(result["education"])

    print("\n===== EXPERIENCE =====")
    print(result["experience"])

    print("\n===== PROJECTS =====")
    print(result["projects"])

    print("\n===== CERTIFICATIONS =====")
    print(result["certifications"])

    print("\n===== NLP INFORMATION =====")
    print("Sentences:", len(result["sentences"]))
    print("Entities:", len(result["entities"]))
    print("Tokens:", len(result["tokens"]))
    print("Word Count:", result["word_count"])