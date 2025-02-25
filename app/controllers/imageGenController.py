from flask import current_app

def genImagefn(prompts:list,height,width,num_inference_steps,guidance_scale)->list:
    ImageGenModel = current_app.config['ImageGenModel']
    # returns a list
    images = ImageGenModel.generate_images(
                prompts=prompts,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            )
    
    return images