from nlp.resume_analyzer import analyze_resume
from nlp.skill_extractor import extract_skills


sample_resume = """
John Doe

Python Developer

Skills:
Python, Java, SQL, Flask, Machine Learning,
Pandas, NumPy, TensorFlow, Git, MongoDB

Education:
Bachelor of Technology in Computer Science

Experience:
Software Developer at ABC Technologies for 2 years.

Projects:
Built a machine learning based resume analyzer
using Python, Flask, NLP and SQL.
"""


# ==============================
# NLP ANALYSIS
# ==============================

result = analyze_resume(sample_resume)


print("\n================================")
print("          NLP ANALYSIS")
print("================================")


print("\nWord Count:")
print(result["word_count"])


print("\nSentences:")

for sentence in result["sentences"]:
    print("-", sentence)


print("\nNamed Entities:")

for entity in result["entities"]:

    print(
        entity["text"],
        "->",
        entity["label"]
    )


# ==============================
# SKILL EXTRACTION
# ==============================

skills = extract_skills(sample_resume)


print("\n================================")
print("        EXTRACTED SKILLS")
print("================================")


for skill in skills:

    print(
        "✓",
        skill
    )


print("\nTotal Skills:")
print(len(skills))