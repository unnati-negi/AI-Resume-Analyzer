import spacy


# Load spaCy English model
nlp = spacy.load("en_core_web_sm")


def analyze_resume(text):
    """
    Analyze resume text using spaCy.

    Returns:
        dict containing basic NLP information.
    """

    doc = nlp(text)

    # Extract sentences
    sentences = []

    for sentence in doc.sents:
        cleaned_sentence = sentence.text.strip()

        if cleaned_sentence:
            sentences.append(cleaned_sentence)


    # Extract named entities
    entities = []

    for entity in doc.ents:

        entities.append({
            "text": entity.text,
            "label": entity.label_
        })


    # Extract important tokens
    tokens = []

    for token in doc:

        if not token.is_space and not token.is_punct:

            tokens.append({
                "text": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_
            })


    return {
        "sentences": sentences,
        "entities": entities,
        "tokens": tokens,
        "word_count": len(doc)
    }