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

def upload_audio_to_cloudinary(audio_paths: list, upload_preset="canvas-upload") -> list:
    """
    Uploads a list of audio files to Cloudinary using a specified preset
    and returns a list of uploaded URLs.

    :param audio_paths: List of local audio file paths (e.g., MP3, WAV).
    :param upload_preset: Cloudinary upload preset (default is 'audio-upload').
    :return: List of URLs of the uploaded audio files.
    """
    uploaded_urls = []
    for audio_path in audio_paths:
        try:
            # Upload the audio file to Cloudinary using the specified upload preset
            response = cloudinary.uploader.upload(
                audio_path,
                upload_preset=upload_preset,
                resource_type="auto"  # Automatically detects the file type (audio or video)
            )

            # Extract the secure URL from the response
            uploaded_urls.append(response.get("secure_url"))
            print(f"Uploaded {audio_path} successfully.")
        except Exception as e:
            print(f"Failed to upload {audio_path}: {e}")

    return uploaded_urls

def upload_video_to_cloudinary(video_path: str, upload_preset="canvas-upload") -> str:
    """
    Uploads a video file to Cloudinary using a specified preset
    and returns the uploaded video's URL.

    :param video_path: Local video file path (e.g., MP4, AVI).
    :param upload_preset: Cloudinary upload preset (default is 'canvas-upload').
    :return: URL of the uploaded video.
    """
    try:
        # Upload the video file to Cloudinary using the specified upload preset
        response = cloudinary.uploader.upload(
            video_path,
            upload_preset=upload_preset,
            resource_type="video"  # Explicitly specify the resource type as video
        )

        # Extract the secure URL from the response
        uploaded_url = response.get("secure_url")
        print(f"Uploaded {video_path} successfully.")
        return uploaded_url

    except Exception as e:
        print(f"Failed to upload {video_path}: {e}")
        return ""