import spacy

def extract_subject(text):
    """Extracts the main subject (person, place, or entity) from a given text."""

    nlp = spacy.load("en_core_web_sm")  # Load spaCy English model
    doc = nlp(text)

    # Look for named entities that are persons, organizations, or geopolitical
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE"]:
            return ent.text  # Return the first valid entity found

    # If no named entity, find the first noun as a fallback
    for token in doc:
        if token.pos_ == "NOUN" and token.dep_ in ["nsubj", "attr"]:
            return token.text

    return ""  # Default if nothing is found