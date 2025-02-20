from flask import current_app
from app.utils.audioProcessor import process_audio
from app.utils.translateToHindi import translator

import asyncio

def genAudioController(texts, url, lang="en"):
    try:
        TTSModel = current_app.config['TTSModel']

        # Use asyncio.run() to call the async translator function
        textsinModifiedlanguage = (
            asyncio.run(translator(texts)) if lang == "hi" else texts
        )

        if textsinModifiedlanguage is None:
            raise ValueError("Translation failed, received None")

        # Filter out empty strings after splitting
        sentences = [s.strip() for s in textsinModifiedlanguage.split(".") if s.strip()]
        print(f"Number of sentences to process: {len(sentences)}")

        audioUrls = TTSModel.synthesize_and_upload(
            sentences, 
            url=url, 
            language=lang
        )

        return audioUrls or []

    except Exception as e:
        print(f"Error in genAudioController: {str(e)}")
        return []