# import os
# import requests
# from tempfile import NamedTemporaryFile
# # import torch
# # import torchaudio
# from TTS.api import TTS
# from app.utils.cloudinaryUploader import upload_audio_to_cloudinary

# class HuggingFaceTTS:
#     def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2"):
#         # Initialize TTS model without language parameter
#         self.tts = TTS(model_name=model_name)
    
#     def download_audio(self, url):
#         with NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
#             response = requests.get(url, stream=True)
#             if response.status_code == 200:
#                 temp_file.write(response.content)
#                 temp_file.flush()
#                 return temp_file.name
#             else:
#                 raise ValueError(f"Failed to download audio. Status code: {response.status_code}")
    
#     def synthesize_and_upload(self, texts:list, url, language="en"):
#         audio_files = []
        
#         # Download custom voice if URL provided
#         reference_wav = self.download_audio(url) if url else None
        
#         print("Audio generation has started.")
#         print(len(texts))
#         for i, text in enumerate(texts):
#             if(len(text) == 0): continue
#             output_path = f"output_{i}.wav"
            
#             # Generate speech with custom voice if available
#             if reference_wav:
#                 self.tts.tts_to_file(
#                     text=text, 
#                     file_path=output_path, 
#                     speaker_wav=reference_wav,
#                     language=language,
#                 )
#             else:
#                 self.tts.tts_to_file(
#                     text=text, 
#                     file_path=output_path,
#                     language=language
#                 )
            
#             audio_files.append(output_path)
        
#         print("Audio generation has end.")

#         # Upload to Cloudinary
#         uploaded_urls = upload_audio_to_cloudinary(audio_files)
        
#         # Clean temporary files
#         for temp_audio_file in audio_files:
#             os.remove(temp_audio_file)

#         print(uploaded_urls)
        
#         return uploaded_urls

# import os
# import requests
# from tempfile import NamedTemporaryFile
# from TTS.api import TTS
# from app.utils.cloudinaryUploader import upload_audio_to_cloudinary
# from concurrent.futures import ThreadPoolExecutor
# from functools import partial

# class HuggingFaceTTS:
#     def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2"):
#         self.tts = TTS(model_name=model_name)
#         self.max_workers = 3
    
#     def download_audio(self, url):
#         with NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
#             response = requests.get(url, stream=True)
#             if response.status_code == 200:
#                 temp_file.write(response.content)
#                 temp_file.flush()
#                 return temp_file.name
#             else:
#                 raise ValueError(f"Failed to download audio. Status code: {response.status_code}")
    
#     def generate_single_audio(self, text, i, reference_wav, language):
#         try:
#             if not isinstance(text, str) or len(text.strip()) == 0:
#                 print(f"Skipping empty text at index {i}")
#                 return None
                
#             # Clean the text while preserving the period
#             text = text.strip()
#             if not text.endswith('.'):
#                 text = text + '.'
                
#             print(f"Processing text {i}: {text}")
#             output_path = f"output_{i}.wav"
            
#             if reference_wav:
#                 self.tts.tts_to_file(
#                     text=text, 
#                     file_path=output_path, 
#                     speaker_wav=reference_wav,
#                     language=language,
#                 )
#             else:
#                 self.tts.tts_to_file(
#                     text=text, 
#                     file_path=output_path,
#                     language=language
#                 )
            
#             if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
#                 print(f"Successfully generated audio for text {i}")
#                 return output_path
#             else:
#                 print(f"Failed to generate audio for text {i}")
#                 return None
                
#         except Exception as e:
#             print(f"Error generating audio for text {i}: {str(e)}")
#             return None
    
#     def synthesize_and_upload(self, texts, url, language="en"):
#         try:
#             audio_files = []
            
#             # Download custom voice if URL provided
#             reference_wav = self.download_audio(url) if url else None
            
#             print("Audio generation has started.")
#             print(f"Number of text segments: {len(texts)}")
            
#             # Filter out empty texts while preserving order
#             texts = [t for t in texts if isinstance(t, str) and t.strip()]
#             print(f"Number of valid text segments: {len(texts)}")
            
#             # Process texts in parallel
#             with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
#                 process_func = partial(
#                     self.generate_single_audio,
#                     reference_wav=reference_wav,
#                     language=language
#                 )
                
#                 # Submit all tasks and get futures
#                 futures = []
#                 for i, text in enumerate(texts):
#                     future = executor.submit(process_func, text, i)
#                     futures.append((i, future))
                
#                 # Collect results in order
#                 results = [None] * len(texts)
#                 for i, future in futures:
#                     try:
#                         result = future.result(timeout=300)  # 5 minute timeout
#                         if result:
#                             results[i] = result
#                     except Exception as e:
#                         print(f"Error processing future {i}: {str(e)}")
                
#                 # Filter out None values while maintaining order
#                 audio_files = [f for f in results if f is not None]
            
#             print(f"Audio generation complete. Generated {len(audio_files)} files.")

#             if not audio_files:
#                 print("No audio files were generated successfully")
#                 return []

#             # Upload to Cloudinary
#             uploaded_urls = upload_audio_to_cloudinary(audio_files)
#             print(f"Uploaded {len(uploaded_urls)} files to Cloudinary")
            
#             # Clean temporary files
#             for temp_audio_file in audio_files:
#                 try:
#                     os.remove(temp_audio_file)
#                 except Exception as e:
#                     print(f"Error removing temp file {temp_audio_file}: {str(e)}")
            
#             # Clean up reference wav if it exists
#             if reference_wav:
#                 try:
#                     os.remove(reference_wav)
#                 except Exception as e:
#                     print(f"Error removing reference wav: {str(e)}")

#             return uploaded_urls
            
#         except Exception as e:
#             print(f"Error in synthesize_and_upload: {str(e)}")
#             return []

# ---------------------------------------------------------------------------- #
#                              Latest code for TTS                             #
# ---------------------------------------------------------------------------- #

import os
import requests
from tempfile import NamedTemporaryFile
from TTS.api import TTS
from app.utils.cloudinaryUploader import upload_audio_to_cloudinary
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import time

class HuggingFaceTTS:
    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2"):
        self.tts = TTS(model_name=model_name)
        self.max_workers = 3
        self.max_retries = 3
        self.timeout = 300  # 5 minutes
    
    def download_audio(self, url):
        try:
            with NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                temp_file.write(response.content)
                temp_file.flush()
                return temp_file.name
        except requests.exceptions.RequestException as e:
            print(f"Error downloading audio: {str(e)}")
            return None
    
    def generate_single_audio(self, text, i, reference_wav, language):
        for attempt in range(self.max_retries):
            try:
                if not isinstance(text, str) or len(text.strip()) == 0:
                    print(f"Skipping empty text at index {i}")
                    return None
                
                # Normalize text
                text = text.strip()
                if not text.endswith('.'):
                    text = text + '.'
                
                # Check text length
                if len(text) > 500:  # Adjust limit as needed
                    print(f"Text {i} exceeds maximum length. Truncating...")
                    text = text[:497] + "..."
                
                print(f"Attempt {attempt + 1} - Processing text {i}: {text}")
                output_path = f"output_{i}_{attempt}.wav"
                
                # Generate audio with appropriate parameters
                kwargs = {
                    "text": text,
                    "file_path": output_path,
                    "language": language
                }
                if reference_wav:
                    kwargs["speaker_wav"] = reference_wav
                
                self.tts.tts_to_file(**kwargs)
                
                # Verify output
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1024:  # Min 1KB
                    print(f"Successfully generated audio for text {i}")
                    return output_path
                else:
                    raise ValueError("Generated file is too small or invalid")
                    
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for text {i}: {str(e)}")
                if attempt == self.max_retries - 1:
                    print(f"All attempts failed for text {i}")
                    return None
                time.sleep(1)  # Wait before retry
    
    def synthesize_and_upload(self, texts, url, language="en"):
        try:
            audio_files = []
            reference_wav = None
            
            if url:
                reference_wav = self.download_audio(url)
                if not reference_wav:
                    print("Warning: Failed to download reference audio, proceeding without it")
            
            print(f"Audio generation started with {len(texts)} segments")
            
            # Filter and clean texts
            valid_texts = []
            for text in texts:
                if isinstance(text, str) and text.strip():
                    cleaned_text = text.strip()
                    if not cleaned_text.endswith('.'):
                        cleaned_text += '.'
                    valid_texts.append(cleaned_text)
            
            print(f"Processing {len(valid_texts)} valid text segments")
            
            # Process texts with better error handling
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_index = {
                    executor.submit(
                        self.generate_single_audio,
                        text,
                        i,
                        reference_wav,
                        language
                    ): i for i, text in enumerate(valid_texts)
                }
                
                for future in future_to_index:
                    try:
                        result = future.result(timeout=self.timeout)
                        if result:
                            audio_files.append(result)
                    except Exception as e:
                        print(f"Error processing future {future_to_index[future]}: {str(e)}")
            
            if not audio_files:
                print("No audio files were generated successfully")
                return []
            
            print(f"Uploading {len(audio_files)} files to Cloudinary")
            uploaded_urls = upload_audio_to_cloudinary(audio_files)
            
            # Cleanup
            self._cleanup_files(audio_files + ([reference_wav] if reference_wav else []))
            
            return uploaded_urls
            
        except Exception as e:
            print(f"Error in synthesize_and_upload: {str(e)}")
            return []
    
    def _cleanup_files(self, files):
        for file in files:
            try:
                if file and os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                print(f"Error removing file {file}: {str(e)}")