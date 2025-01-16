from flask import current_app

# Simplified style guides
STYLE_GUIDES = {
    'cinematic': "cinematic, 8k",
    'fantasy': "fantasy art, vibrant",
    'historical': "historical, detailed",
    'artistic': "digital art, stylized"
}

def genNewScript(body:dict)->dict:
    topic = body['topic']
    ScriptGenModel = current_app.config['ScriptGenModel']

    result = ScriptGenModel.generate_with_custom_instructions(
                context="",
                query=topic,
                # words_per_sentence=words_per_sentence
            )
    
    return {
        'topic':topic,
        'script':result
    }

def genImgPrompts(story:str)->list:
    ScriptGenModel = current_app.config['ScriptGenModel']
    # returns a list
    prompts = ScriptGenModel.generate_concise_image_prompts(
                story='',
                max_words=20,  # Adjust this for desired length
                style_guide=STYLE_GUIDES['cinematic']
            )

    # print("Generated Image Prompts:")
    # for i, prompt in enumerate(prompts, 1):
        # words = len(prompt.split())
        # print(f"\n{i}. ({words} words) {prompt}")
    return prompts