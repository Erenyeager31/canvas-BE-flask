from flask import current_app

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
    
    return {
        topic,context
    }