from app.utils.generateVideo import VideoGenerator
from app.utils.translateToHindi import translator
import asyncio

def videoGenController(story:str,image_urls:list,audio_urls:list,caption_lang='en'):
    storyInModifiedLanguage = ""
    if caption_lang == "hi":
        storyInModifiedLanguage = asyncio.run(translator(story))
        if storyInModifiedLanguage is None:
            # Fallback to original story if translation fails
            print("Translation failed, using original text")
            storyInModifiedLanguage = story
    else:
        storyInModifiedLanguage = story

    print(storyInModifiedLanguage)
    print(image_urls)
    print(audio_urls)
    video_gen = VideoGenerator(image_urls, audio_urls,story=storyInModifiedLanguage)

    videoUrl = video_gen.generateVideo()
    return videoUrl
