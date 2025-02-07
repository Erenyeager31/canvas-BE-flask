from flask import current_app
from app.utils.audioProcessor import process_audio
from app.utils.translateToHindi import translator

# def genAudioController(texts, url,lang="en"):
#     TTSModel = current_app.config['TTSModel']

#     print(url)
#     # filteredAudioUrl = process_audio(url)
    
#     textsinModifiedlanguage = ""
#     if lang == "hi":
#         textsinModifiedlanguage = translator(texts,lang)
#     else:
#         textsinModifiedlanguage = texts

#     # returns a list
#     audioUrls = TTSModel.synthesize_and_upload(
#                 textsinModifiedlanguage.split("."), url=url, language=lang
#             )

#     print("Inside controller, process has finished")
#     print(audioUrls)

#     return audioUrls

def genAudioController(texts, url, lang="en"):
    try:
        TTSModel = current_app.config['TTSModel']
        
        textsinModifiedlanguage = translator(texts) if lang == "hi" else texts
        print(len(textsinModifiedlanguage.split(".")))
        
        audioUrls = TTSModel.synthesize_and_upload(
            textsinModifiedlanguage.split("."), 
            url=url, 
            language=lang
        )
        
        return audioUrls or []

        # return [
        #     textsinModifiedlanguage
        # ]
        
    except Exception as e:
        print(f"Error in genAudioController: {str(e)}")
        return []