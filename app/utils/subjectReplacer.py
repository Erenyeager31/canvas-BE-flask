import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

def replace_pronouns_and_nouns(sentences, subject):
    """
    Replace pronouns and common person-describing nouns with the specified subject.

    Args:
        sentences (list): List of sentences to process
        subject (str): The subject name to replace pronouns and common nouns with

    Returns:
        list: Updated sentences with pronouns and common nouns replaced
    """
    # Download NLTK data with proper resource names
    try:
        nltk.download('punkt_tab', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
    except Exception as e:
        print(f"Warning: NLTK download issue: {e}")
        print("Continuing with basic processing...")

    # Define target words to replace
    pronouns = {
        "he", "she", "it", "they", "him", "her", "them", "his", "hers", "theirs",
        "himself", "herself", "themself", "themselves"
    }

    common_nouns = {
        "person", "man", "woman", "boy", "girl", "child", "kid", "teen", "teenager",
        "individual", "character", "figure", "guy", "lady", "gentleman", "male", "female",
        "youth", "youngster", "adult", "citizen", "human", "inhabitant", "resident"
    }

    updated_sentences = []

    for sentence in sentences:
        try:
            # Try NLTK tokenization and tagging
            words = word_tokenize(sentence)
            tagged_words = pos_tag(words)

            new_words = []
            for i, (word, tag) in enumerate(tagged_words):
                lower_word = word.lower()

                # Check if word is a pronoun or a common noun with noun POS tag
                if lower_word in pronouns or (lower_word in common_nouns and tag.startswith('NN')):
                    # Preserve capitalization pattern
                    if word[0].isupper():
                        new_words.append(subject[0].upper() + subject[1:])
                    else:
                        new_words.append(subject)
                else:
                    new_words.append(word)

        except Exception as e:
            # Fallback to simple word replacement if NLTK fails
            print(f"Falling back to simple replacement: {e}")
            words = sentence.split()
            new_words = []

            for word in words:
                # Simple word matching for fallback
                word_clean = word.lower().strip(".,!?;:()'\"")
                if word_clean in pronouns or word_clean in common_nouns:
                    # Preserve punctuation
                    prefix = ""
                    suffix = ""
                    for char in word:
                        if char in ".,!?;:()'\"" and char == word[0]:
                            prefix += char
                        elif char in ".,!?;:()'\"":
                            suffix += char

                    # Preserve capitalization
                    if word[0].isupper():
                        new_words.append(prefix + subject[0].upper() + subject[1:] + suffix)
                    else:
                        new_words.append(prefix + subject + suffix)
                else:
                    new_words.append(word)

        # Reconstruct sentence with proper spacing
        reconstructed = " ".join(new_words)
        # Fix spacing around punctuation
        for punct in ".,;:!?":
            reconstructed = reconstructed.replace(f" {punct}", punct)

        updated_sentences.append(reconstructed)

    return updated_sentences