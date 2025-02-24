from flask import current_app
from app.controllers.vectorDBcontroller import retriveContext, retriveUserContextController
from app.utils.cloudinaryDeleteFiles import delete_files_from_cloudinary
from app.utils.subjectExtractor import extract_subject
from app.utils.subjectReplacer import replace_pronouns_or_nouns

# Simplified style guides
STYLE_GUIDES = {
    'cinematic': "cinematic, 8k",
    'fantasy': "fantasy art, vibrant",
    'historical': "historical, detailed",
    'artistic': "digital art, stylized"
}

useless_words = [
    "Solution", "solution",
    "Answer", "answer",
    "Response", "response",
    "Explanation", "explanation",
    "Statement", "statement",
    "Query", "query",
    "Clarification", "clarification",
    "Insight", "insight",
    "Task", "task",
    "Objective", "objective",
    "Challenge", "challenge",
    "Instruction", "instruction",
    "Process", "process",
    "Steps", "steps",
    "Guidelines", "guidelines",
    "Compute", "compute",
    "Algorithm", "algorithm",
    "Execution", "execution",
    "Function", "function",
    "Output", "output",
    "Variable", "variable",
    "Parameter", "parameter",
    "*", "#", "-", "_", ">", "\\n", "\\t",
    "{", "}", "[", "]", "(", ")",
    "=>", "::", "\"\"\"",
    "Σ", "∫", "≈", "→", "⊆"
]


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

def genImgPrompts(story:str)->list:
    ScriptGenModel = current_app.config['ScriptGenModel']
    # returns a list
    style_guide = story.split("#")[1]
    story = story.split("#")[0]

    subject = extract_subject(story)

    prompts = ScriptGenModel.generate_concise_image_prompts(
                story=story,
                # subject=subject,
                style_guide=style_guide
            )
    
    final_prompt = []
    
    for text in story.split("."):
        if not text.strip(): continue

        prompts = ScriptGenModel.generate_concise_image_prompts(
                story=text+".",
                # subject=subject,
                style_guide=style_guide
            )

        prompt = ScriptGenModel.generate_concise_image_prompts(text+".",style_guide="Biography")[0].replace('"',"")
        prompt = ScriptGenModel.generate_concise_image_prompts(text+".",style_guide="Biography")[0].replace("'","")
        prompt = ScriptGenModel.generate_concise_image_prompts(text+".",style_guide="Biography")[0].replace('`',"")
        prompt.replace("\n","")

        pos = prompt.find("```")
        prompt = prompt[:pos] if pos != -1 else prompt

        pos = prompt.find("-")
        prompt = prompt[:pos] if pos != -1 else prompt

        pos = prompt.find("*")
        prompt = prompt[:pos] if pos != -1 else prompt

        pos = prompt.find("_")
        prompt = prompt[:pos] if pos != -1 else prompt

        pos = prompt.find("import")
        prompt = prompt[:pos] if pos != -1 else prompt

        pos = prompt.find("def")
        prompt = prompt[:pos] if pos != -1 else prompt

        print("Obtained prompt :",prompt,"\n\n")
        useless_list = [w for w in useless_words if w in prompt]
        while len(useless_list) != 0 or len(prompt.split(" ")) < 10:
            prompt = ScriptGenModel.generate_concise_image_prompts(text+".",style_guide="Biography")[0].replace('"',"")
            prompt = ScriptGenModel.generate_concise_image_prompts(text+".",style_guide="Biography")[0].replace("'","")
            prompt = ScriptGenModel.generate_concise_image_prompts(text+".",style_guide="Biography")[0].replace('`',"")
            prompt.replace("\n","")

            pos = prompt.find("```")
            prompt = prompt[:pos] if pos != -1 else prompt

            pos = prompt.find("-")
            prompt = prompt[:pos] if pos != -1 else prompt

            pos = prompt.find("*")
            prompt = prompt[:pos] if pos != -1 else prompt

            pos = prompt.find("_")
            prompt = prompt[:pos] if pos != -1 else prompt

            pos = prompt.find("import")
            prompt = prompt[:pos] if pos != -1 else prompt

            pos = prompt.find("def")
            prompt = prompt[:pos] if pos != -1 else prompt

            print("Obtained prompt :",prompt,"\n\n")  
            # print(prompt,"\n\n")
            useless_list = [w for w in useless_words if w in prompt]
            final_prompt.append(prompt)
    
    # replacing with subject
    prompts = replace_pronouns_or_nouns(final_prompt,subject)

    return prompts