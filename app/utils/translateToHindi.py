from deep_translator import GoogleTranslator

def translator(story: str,lang='en') -> str:
    modifiedStory = GoogleTranslator(source='en', target=lang).translate(story)
    modifiedStory = modifiedStory.replace('।','.')
    print(modifiedStory)
    return modifiedStory
