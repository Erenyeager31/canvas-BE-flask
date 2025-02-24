from optimum.intel.openvino.modeling_diffusion import OVStableDiffusionXLPipeline
from app.utils.cloudinaryUploader import upload_images_to_cloudinary

class ImageGenerator:
    def __init__(self):
        """
        Initializes the image generation pipeline with a predefined model path.
        """
        model_path = "rupeshs/sdxl-turbo-openvino-int8"
        # model_path = "rupeshs/SDXL-Lightning-2steps-openvino-int8"
        self.pipeline = OVStableDiffusionXLPipeline.from_pretrained(
            model_path,
            ov_config={"CACHE_DIR": ""},
        )

    def generate_images(self, prompts: list, width: int = 1024, height: int = 576, 
                        num_inference_steps: int = 5, guidance_scale: float = 1.0, 
                        output_dir: str = "./"):
        
        # w --> 512, h --> 384, inf --> 3
        """
        Generates images for a list of prompts and saves each to a file.
        
        :param prompts: List of text prompts to guide image generation.
        :param width: Width of the generated images.
        :param height: Height of the generated images.
        :param num_inference_steps: Number of inference steps for image generation.
        :param guidance_scale: Scale for guidance during generation.
        :param output_dir: Directory to save the generated images.
        """
        image_paths = []
        for idx, prompt in enumerate(prompts):
            output_path = f"{output_dir}/image_{idx + 1}.png"
            images = self.pipeline(
                prompt=prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
            ).images
            images[0].save(output_path)
            image_paths.append(output_path)
            print(f"Image for prompt {idx + 1} saved to {output_path}")
        
        # upload images to cloudinary and obtain the urls
        cloudinary_urls = upload_images_to_cloudinary(image_paths)
        return cloudinary_urls