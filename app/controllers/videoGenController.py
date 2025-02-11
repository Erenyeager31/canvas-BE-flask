from app.utils.generateVideo import VideoGenerator
from app.utils.translateToHindi import translator

def videoGenController(story:str,image_urls:list,audio_urls:list,caption_lang='en'):
    storyInModifiedLanguage = ""
    if caption_lang == "hi":
        storyInModifiedLanguage = translator(story)
    else:
        storyInModifiedLanguage = story

    print(storyInModifiedLanguage)
    print(image_urls)
    print(audio_urls)
    video_gen = VideoGenerator(image_urls, audio_urls,story=storyInModifiedLanguage)

    videoUrl = video_gen.generateVideo()
    return videoUrl
