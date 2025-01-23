from flask import current_app
from app.controllers.vectorDBcontroller import retriveContext

def genAudioController(texts, url=None):
    TTSModel = current_app.config['TTSModel']
    # returns a list
    audioUrls = TTSModel.synthesize_and_upload(
                texts, url
            )

    return audioUrls