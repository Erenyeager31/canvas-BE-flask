from flask import current_app
from app.utils.audioProcessor import process_audio

def genAudioController(texts, url=None):
    TTSModel = current_app.config['TTSModel']

    filteredAudioUrl = process_audio(url)

    # returns a list
    audioUrls = TTSModel.synthesize_and_upload(
                texts, url=filteredAudioUrl
            )

    return audioUrls