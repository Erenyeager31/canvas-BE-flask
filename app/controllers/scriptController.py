from flask import current_app
from app.controllers.vectorDBcontroller import retriveContext

# Simplified style guides
STYLE_GUIDES = {
    'cinematic': "cinematic, 8k",
    'fantasy': "fantasy art, vibrant",
    'historical': "historical, detailed",
    'artistic': "digital art, stylized"
}

# def genNewScript(body:dict)->dict:
#     topic = body['topic']
#     ScriptGenModel = current_app.config['ScriptGenModel']
    
#     context = retriveContext(topic)
    
#     # print("Topic:",topic,"Context:",context)

#     result = ScriptGenModel.generate_with_custom_instructions(
#                 context=context,
#                 query=topic,
#                 # words_per_sentence=words_per_sentence
#             )
    
#     print(result)
#     return result
def genNewScript(body: dict) -> dict:
    topic = body['topic']
    ScriptGenModel = current_app.config['ScriptGenModel']
    
    context = retriveContext(topic)
    
    # Generate the result
    result = ScriptGenModel.generate_with_custom_instructions(
        context=context,
        query=topic,
    )
    
    if 'generated_text' in result:
        # Clean the generated text
        cleaned_text = result['generated_text']
        cleaned_text = cleaned_text.replace('\n', ' ').replace('{', '').replace('}', '').replace('_', '')
        # Update the result with cleaned text
        result['generated_text'] = cleaned_text

    print(result)
    return result

def genImgPrompts(story:str)->list:
    ScriptGenModel = current_app.config['ScriptGenModel']
    # returns a list
    prompts = ScriptGenModel.generate_concise_image_prompts(
                story=story,
                max_words=20,  # Adjust this for desired length
                style_guide=STYLE_GUIDES['historical']
            )

    return prompts