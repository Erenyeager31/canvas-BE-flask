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

import os
import requests
from tempfile import NamedTemporaryFile
from TTS.api import TTS
from app.utils.cloudinaryUploader import upload_audio_to_cloudinary
from concurrent.futures import ThreadPoolExecutor
from functools import partial

class HuggingFaceTTS:
    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2"):
        self.tts = TTS(model_name=model_name)
        self.max_workers = 3
    
    def download_audio(self, url):
        with NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                temp_file.write(response.content)
                temp_file.flush()
                return temp_file.name
            else:
                raise ValueError(f"Failed to download audio. Status code: {response.status_code}")
    
    def generate_single_audio(self, text, i, reference_wav, language):
        try:
            if not isinstance(text, str) or len(text.strip()) == 0:
                print(f"Skipping empty text at index {i}")
                return None
                
            # Clean the text while preserving the period
            text = text.strip()
            if not text.endswith('.'):
                text = text + '.'
                
            print(f"Processing text {i}: {text}")
            output_path = f"output_{i}.wav"
            
            if reference_wav:
                self.tts.tts_to_file(
                    text=text, 
                    file_path=output_path, 
                    speaker_wav=reference_wav,
                    language=language,
                )
            else:
                self.tts.tts_to_file(
                    text=text, 
                    file_path=output_path,
                    language=language
                )
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"Successfully generated audio for text {i}")
                return output_path
            else:
                print(f"Failed to generate audio for text {i}")
                return None
                
        except Exception as e:
            print(f"Error generating audio for text {i}: {str(e)}")
            return None
    
    def synthesize_and_upload(self, texts, url, language="en"):
        try:
            audio_files = []
            
            # Download custom voice if URL provided
            reference_wav = self.download_audio(url) if url else None
            
            print("Audio generation has started.")
            print(f"Number of text segments: {len(texts)}")
            
            # Filter out empty texts while preserving order
            texts = [t for t in texts if isinstance(t, str) and t.strip()]
            print(f"Number of valid text segments: {len(texts)}")
            
            # Process texts in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                process_func = partial(
                    self.generate_single_audio,
                    reference_wav=reference_wav,
                    language=language
                )
                
                # Submit all tasks and get futures
                futures = []
                for i, text in enumerate(texts):
                    future = executor.submit(process_func, text, i)
                    futures.append((i, future))
                
                # Collect results in order
                results = [None] * len(texts)
                for i, future in futures:
                    try:
                        result = future.result(timeout=300)  # 5 minute timeout
                        if result:
                            results[i] = result
                    except Exception as e:
                        print(f"Error processing future {i}: {str(e)}")
                
                # Filter out None values while maintaining order
                audio_files = [f for f in results if f is not None]
            
            print(f"Audio generation complete. Generated {len(audio_files)} files.")

            if not audio_files:
                print("No audio files were generated successfully")
                return []

            # Upload to Cloudinary
            uploaded_urls = upload_audio_to_cloudinary(audio_files)
            print(f"Uploaded {len(uploaded_urls)} files to Cloudinary")
            
            # Clean temporary files
            for temp_audio_file in audio_files:
                try:
                    os.remove(temp_audio_file)
                except Exception as e:
                    print(f"Error removing temp file {temp_audio_file}: {str(e)}")
            
            # Clean up reference wav if it exists
            if reference_wav:
                try:
                    os.remove(reference_wav)
                except Exception as e:
                    print(f"Error removing reference wav: {str(e)}")

            return uploaded_urls
            
        except Exception as e:
            print(f"Error in synthesize_and_upload: {str(e)}")
            return []