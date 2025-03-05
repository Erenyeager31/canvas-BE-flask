from flask import current_app
from app.controllers.vectorDBcontroller import retriveContext, retriveUserContextController
from app.utils.cloudinaryDeleteFiles import delete_files_from_cloudinary
from app.utils.subjectExtractor import extract_subject
from app.utils.subjectReplacer import replace_pronouns_or_nouns
from app.utils.uselessWords import useless_words

# Simplified style guides
STYLE_GUIDES = {
    'cinematic': "cinematic, 8k",
    'fantasy': "fantasy art, vibrant",
    'historical': "historical, detailed",
    'artistic': "digital art, stylized"
}

def clean_prompt(prompt: str) -> str:
    """Removes unwanted characters and patterns from the prompt."""
    prompt = prompt.replace('"', '').replace("'", "").replace('`', "").replace("\n", "")
    
    for char in ["```", "-", "*", "_", "import", "def"]:
        pos = prompt.find(char)
        if pos != -1:
            prompt = prompt[:pos]

    return prompt.strip()

def genNewScript(body: dict,userDocURL) -> dict:
    topic = body['topic']

    ScriptGenModel = current_app.config['ScriptGenModel']
    
    # obtain style_guide
    style_guide = topic.split("#")[1]
    topic = topic.split("#")[0]
    
    # based on whether user has provided doc or not, fetch context
    context = ""
    if userDocURL:
        context = retriveUserContextController(topic,userDocURL)
    else:
        context = retriveContext(topic)

    print("Inside controller :",context)

    response = delete_files_from_cloudinary([userDocURL])
    
    # Generate the result
    result = ScriptGenModel.generate_with_custom_instructions(
        context=context,
        query=topic,
        style_guide=style_guide
    )
    useless_list = [w for w in useless_words if w in result['generated_text']]

    while len(result['generated_text'].split(".")) < 5 or len(useless_list) != 0:
        result = ScriptGenModel.generate_with_custom_instructions(context=context,query=topic,style_guide=style_guide)
        useless_list = [w for w in useless_words if w in result['generated_text']]
    
    if 'generated_text' in result:
        # Clean the generated text
        cleaned_text = result['generated_text']
        cleaned_text = cleaned_text.replace('\n', ' ').replace('{', '').replace('}', '').replace('_', '')
        # Update the result with cleaned text
        result['generated_text'] = cleaned_text

    print(result)
    return result

def genImgPrompts(story: str) -> list:
    ScriptGenModel = current_app.config['ScriptGenModel']
    
    parts = story.split("#")
    story_text = parts[0]
    style_guide = parts[1] if len(parts) > 1 else "Historical"
    subject = parts[2] if len(parts) > 2 else ""
    
    final_prompts = []
    
    for sentence in story_text.split("."):
        sentence = sentence.strip()
        if not sentence:
            continue
        
        retries = 5  # Prevent infinite loops
        while retries > 0:
            prompt = ScriptGenModel.generate_concise_image_prompts(sentence + ".", style_guide=style_guide)[0]
            prompt = clean_prompt(prompt)
            
            # Check if prompt is valid
            if not any(w in prompt for w in useless_words) and len(prompt.split()) >= 15:
                break
            retries -= 1
        
        # **Skip invalid prompts**
        if not prompt or "[image]" in prompt or "self." in prompt or "sentences =" in prompt:
            continue  
        
        final_prompts.append(f"{subject}. {prompt}")
    
    final_prompts = replace_pronouns_or_nouns(final_prompts, subject)
    
    print(final_prompts)
    
    return final_prompts