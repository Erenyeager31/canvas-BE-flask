import os
import requests
from tempfile import NamedTemporaryFile
import torch
import torchaudio
from TTS.api import TTS
from app.utils.cloudinaryUploader import upload_audio_to_cloudinary

class HuggingFaceTTS:
    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2"):
        # Initialize TTS model without language parameter
        self.tts = TTS(model_name=model_name)
    
    def download_audio(self, url, file_path="temp_voice_sample.wav"):
        response = requests.get(url)
        with open(file_path, "wb") as f:
            f.write(response.content)
        return file_path
    
    def synthesize_and_upload(self, texts, url=None, language="en"):
        audio_files = []
        
        # Download custom voice if URL provided
        reference_wav = self.download_audio(url) if url else None
        
        for i, text in enumerate(texts):
            output_path = f"output_{i}.wav"
            
            # Generate speech with custom voice if available
            if reference_wav:
                self.tts.tts_to_file(
                    text=text, 
                    file_path=output_path, 
                    speaker_wav=reference_wav,
                    language=language
                )
            else:
                self.tts.tts_to_file(
                    text=text, 
                    file_path=output_path,
                    language=language
                )
            
            audio_files.append(output_path)
        
        # Upload to Cloudinary
        uploaded_urls = upload_audio_to_cloudinary(audio_files)
        
        # Clean temporary files
        for temp_audio_file in audio_files:
            os.remove(temp_audio_file)
        
        return uploaded_urls