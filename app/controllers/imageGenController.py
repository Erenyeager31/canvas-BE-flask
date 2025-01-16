from flask import current_app

def genImagefn(prompts:list)->list:
    ImageGenModel = current_app.config['ImageGenModel']
    # returns a list
    images = ImageGenModel.generate_images(
                prompts=prompts,
            )
    
    return images