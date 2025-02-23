import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

# Ensure necessary NLTK resources are available
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

def replace_pronouns_or_nouns(sentences, subject):
    """
    Replace only the first occurrence of a pronoun or common noun in a sentence 
    with the specified subject, but only if a partial match of the subject is present.

    Args:
        sentences (list): List of sentences to process.
        subject (str): The subject name to replace pronouns and common nouns with.

    Returns:
        list: Updated sentences with replacements applied.
    """

    # Define target words to replace
    pronouns = {
        "he", "she", "it", "they", "him", "her", "them", "his", "hers", "theirs",
        "himself", "herself", "themself", "themselves"
    }

    common_nouns = {
        # General terms
        "person", "man", "woman", "boy", "girl", "child", "kid", "teen", "teenager",
        "individual", "character", "figure", "guy", "lady", "gentleman", "male",
        "female", "youth", "youngster", "adult", "citizen", "human", "inhabitant",
        "resident", "worker", "employee", "boss", "leader", "follower",

        # Titles & Nobility
        "king", "queen", "prince", "princess", "duke", "duchess", "emperor",
        "empress", "lord", "lady", "knight", "baron", "baroness", "noble",
        "czar", "sultan", "chief", "chancellor", "regent",

        # Professional roles
        "teacher", "student", "professor", "doctor", "nurse", "scientist", 
        "engineer", "artist", "writer", "musician", "actor", "director", 
        "player", "athlete", "coach", "driver", "pilot", "singer", "dancer",
        "lawyer", "judge", "chef", "farmer", "soldier", "officer", "detective",
        "minister", "priest", "monk", "nun", "policeman", "firefighter",
        "author", "poet", "journalist", "reporter", "photographer",
        "entrepreneur", "businessperson", "banker", "trader", "merchant",
        "worker", "clerk", "cashier", "guard", "janitor", "tailor", "blacksmith",
        "carpenter", "mechanic", "electrician", "plumber",

        # Mythical & Fictional characters
        "hero", "villain", "wizard", "witch", "elf", "dwarf", "giant", "fairy",
        "vampire", "werewolf", "ghost", "zombie", "mermaid", "dragon", "sorcerer",
        "demon", "angel", "god", "goddess",

        # Miscellaneous
        "nomad", "wanderer", "explorer", "adventurer", "pirate", "thief", 
        "merchant", "trader", "pilgrim", "scholar", "sage", "bard", "seer",
        "prophet", "outlaw", "criminal", "prisoner", "slave", "servant"
    }

    updated_sentences = []

    for sentence in sentences:
        # Check if a partial match of the subject is present in the sentence
        if any(re.search(rf'\b{re.escape(part)}\b', sentence, re.IGNORECASE) for part in subject.split()):
            updated_sentences.append(sentence)
            continue
        
        try:
            # Tokenize and tag words
            words = word_tokenize(sentence)
            tagged_words = pos_tag(words)

            new_words = []
            replaced = False

            for i, (word, tag) in enumerate(tagged_words):
                lower_word = word.lower()

                # Replace only the first pronoun or common noun found
                if not replaced and (lower_word in pronouns or (lower_word in common_nouns and tag.startswith('NN'))):
                    # Preserve capitalization pattern
                    replacement = subject.capitalize() if word[0].isupper() else subject
                    new_words.append(replacement)
                    replaced = True  # Only replace the first match
                else:
                    new_words.append(word)

        except Exception as e:
            # Fallback to simple replacement if NLTK fails
            print(f"Falling back to simple replacement: {e}")
            words = sentence.split()
            new_words = []
            replaced = False

            for word in words:
                word_clean = word.lower().strip(".,!?;:()'\"")

                if not replaced and (word_clean in pronouns or word_clean in common_nouns):
                    # Preserve punctuation
                    prefix = "".join([char for char in word if char in ".,!?;:()'\"" and char == word[0]])
                    suffix = "".join([char for char in word if char in ".,!?;:()'\"" and char != word[0]])

                    # Preserve capitalization
                    replacement = subject.capitalize() if word[0].isupper() else subject
                    new_words.append(prefix + replacement + suffix)
                    replaced = True  # Only replace once
                else:
                    new_words.append(word)

        # Reconstruct sentence with proper spacing
        reconstructed = " ".join(new_words)
        for punct in ".,;:!?":
            reconstructed = reconstructed.replace(f" {punct}", punct)

        updated_sentences.append(reconstructed)

    return updated_sentences
