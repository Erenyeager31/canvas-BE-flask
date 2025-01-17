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

    # print("Generated Context:",context[0]['text'])
    context = '.'.join(context[0]['text'].split(".")[:30])
    
    return {
        context
    }