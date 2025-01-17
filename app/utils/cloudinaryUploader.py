import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure Cloudinary credentials
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_SECRET"),
)

def upload_images_to_cloudinary(image_paths: list) -> list:
    """
    Uploads a list of image files to Cloudinary using the 'canvas-upload' preset
    and returns a list of uploaded URLs.

    :param image_paths: List of local image file paths to upload.
    :return: List of URLs of the uploaded images.
    """
    uploaded_urls = []
    for image_path in image_paths:
        try:
            # Upload the image to Cloudinary using the 'canvas-upload' preset
            response = cloudinary.uploader.upload(
                image_path,
                upload_preset="canvas-upload"
            )

            # Extract the secure URL from the response
            uploaded_urls.append(response.get("secure_url"))
            print(f"Uploaded {image_path} successfully.")
        except Exception as e:
            print(f"Failed to upload {image_path}: {e}")

    return uploaded_urls

# # Example usage
# image_paths = ["../data/images/mgboss.jpg"]
# uploaded_urls = upload_images_to_cloudinary(image_paths)
# for url in uploaded_urls:
#     print(url)