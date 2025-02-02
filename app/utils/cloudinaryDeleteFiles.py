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

def delete_files_from_cloudinary(file_urls: list):
    """
    Deletes files from Cloudinary given their URLs.

    :param file_urls: List of Cloudinary file URLs to delete.
    :return: Dictionary with deletion results.
    """
    deletion_results = {}

    for file_url in file_urls:
        try:
            # Extract the public_id from the URL
            public_id = file_url.split("/")[-1].split(".")[0]  # Extracts filename without extension
            folder = "/".join(file_url.split("/")[-3:-1])  # Extracts folder path if exists
            public_id = f"{folder}/{public_id}" if folder else public_id  # Include folder if applicable

            # Delete the file from Cloudinary
            response = cloudinary.uploader.destroy(public_id, resource_type="auto")
            deletion_results[file_url] = response

            if response.get("result") == "ok":
                print(f"Deleted {file_url} successfully.")
            else:
                print(f"Failed to delete {file_url}: {response}")

        except Exception as e:
            print(f"Error deleting {file_url}: {e}")
            deletion_results[file_url] = {"error": str(e)}

    return deletion_results
