from flask import current_app
from app.utils.audioProcessor import process_audio

def genAudioController(texts, url,lang="en"):
    TTSModel = current_app.config['TTSModel']

    print(url)
    # filteredAudioUrl = process_audio(url)

    # returns a list
    audioUrls = TTSModel.synthesize_and_upload(
                texts.split("."), url=url, language=lang
            )

    print("Inside controller, process has finished")
    print(audioUrls)

    return audioUrls