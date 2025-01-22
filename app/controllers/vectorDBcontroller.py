from flask import current_app
from typing import List,Dict,Union
from werkzeug.datastructures import FileStorage
import io

# Simplified style guides
STYLE_GUIDES = {
    'cinematic': "cinematic, 8k",
    'fantasy': "fantasy art, vibrant",
    'historical': "historical, detailed",
    'artistic': "digital art, stylized"
}

def retriveContext(topic:str)->list:
    ContextModel = current_app.config['contextModel']

    context = ContextModel.retrieve_context(
                topic
            )

    # print("Generated Context:",context[0]['text'])
    context = '.'.join(context[0]['text'].split(".")[:30])
    
    return {
        context
    }

def uploadDocument(files: List[Union[FileStorage, io.BytesIO]], filenames: List[str]):
    ContextModel = current_app.config['contextModel']
    status = ContextModel.upload_context(files, filenames)
    return status