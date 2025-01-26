import os
import requests
from pydub import AudioSegment
from scipy.io import wavfile
import noisereduce as nr
import numpy as np
from app.utils.cloudinaryUploader import upload_audio_to_cloudinary

def process_audio(url):
    """
    Downloads an audio file from the provided URL, reduces noise, 
    and saves the noise-reduced audio to a new file.

    Args:
        url (str): URL of the audio file to process.

    Returns:
        str: Path to the noise-reduced audio file.
    """
    temp_dir = "temp_audio"
    os.makedirs(temp_dir, exist_ok=True)

    temp_input_file = os.path.join(temp_dir, "input_audio.mp3")
    temp_wav_file = os.path.join(temp_dir, "input_audio.wav")
    output_file = os.path.join(temp_dir, "noise_reduced_audio.wav")

    # Download the audio file from the URL
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(temp_input_file, "wb") as f:
            f.write(response.content)
    else:
        raise Exception(f"Failed to download audio file from URL. Status code: {response.status_code}")

    # Convert MP3 to WAV if needed
    if not temp_input_file.lower().endswith('.wav'):
        AudioSegment.from_file(temp_input_file).export(temp_wav_file, format="wav")
    else:
        temp_wav_file = temp_input_file

    # Read audio file
    rate, data = wavfile.read(temp_wav_file)

    # Handle multi-channel audio by taking the first channel
    if len(data.shape) > 1:
        data = data[:, 0]

    # Normalize data
    data = data.astype(np.float32) / np.max(np.abs(data))

    # Perform noise reduction
    reduced_noise = nr.reduce_noise(
        y=data, 
        sr=rate, 
        prop_decrease=0.3,  # Lower noise reduction intensity
        n_std_thresh_stationary=1.5  # Adjust noise threshold
    )

    # Write noise-reduced audio
    wavfile.write(output_file, rate, (reduced_noise * 32767).astype(np.int16))

    # Cleanup temporary files
    os.remove(temp_input_file)
    if temp_input_file != temp_wav_file:
        os.remove(temp_wav_file)

    uploadedUrl = upload_audio_to_cloudinary(output_file)

    return uploadedUrl