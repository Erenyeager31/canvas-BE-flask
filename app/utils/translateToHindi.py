# # from deep_translator import GoogleTranslator

# # def translator(story: str,lang='en') -> str:
# #     story_chunks = story.split('.')
# #     translatedChunks = []

# #     for chunk in story_chunks:
# #         modifiedStoryChunk = GoogleTranslator(source='en', target='hi').translate(chunk)
# #         modifiedStoryChunk = modifiedStoryChunk.replace('।','.')
# #         translatedChunks.append(modifiedStoryChunk)
    
# #     modifiedStory = " ".join(translatedChunks)

# #     return modifiedStory

# import mtranslate

# def translator(story: str, source_lang='en', target_lang='hi') -> str:
#     print("Inside translator :",story)
#     story_chunks = story.split('.')
#     print(len(story_chunks))
#     translated_chunks = []

#     for index,chunk in enumerate(story_chunks):
#         try:
#             translated_chunk = mtranslate.translate(chunk, target_lang, source_lang)
#             # translated_chunk = translated_chunk.replace('।', '.')  # Replace Hindi full stops
#             translated_chunks.append(translated_chunk)
#             print(f"Original {index}:",chunk)
#             print(f"Translated {index}:",translated_chunk)
#         except Exception:
#             translated_chunks.append("[Translation Failed]")  # Handle errors gracefully

#     return ".".join(translated_chunks)

from googletrans import Translator
from typing import Optional

def translator(story: str) -> Optional[str]:
    try:
        # Input validation
        if not isinstance(story, str) or not story.strip():
            raise ValueError("Input must be a non-empty string")
            
        # Initialize translator
        translator = Translator()
        
        # Split the story into sentences
        sentences = [sent.strip() for sent in story.split('.') if sent.strip()]
        
        # Translate each sentence
        translated_sentences = []
        for sentence in sentences:
            try:
                translation = translator.translate(sentence, src='en', dest='hi')
                translated_sentences.append(translation.text)
                print(f"Og : {sentence}")
                print(f"T : {translation.text}")
            except Exception as e:
                print(f"Error translating sentence '{sentence}': {str(e)}")
                continue
        
        # If no sentences were translated successfully
        if not translated_sentences:
            return None
            
        # Join the translated sentences
        translated_story = '. '.join(translated_sentences) + '.'
        
        return translated_story
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None