import os
import json
import requests
import subprocess
from pydub.utils import mediainfo
from app.utils.cloudinaryUploader import upload_video_to_cloudinary

class VideoGenerator:
    def __init__(self, story, image_urls, audio_urls, output_filename="output.mp4"):
        # # Ensure data directories exist
        self.data_temp_dir = "data/temp"
        # self.data_temp_audio_dir = os.path.join(self.data_temp_dir, "audio")
        # self.data_temp_clips_dir = os.path.join(self.data_temp_dir, "clips")
        # print(self.data_temp_audio_dir,self.data_temp_clips_dir)
        # os.makedirs(self.data_temp_audio_dir, exist_ok=True)
        # os.makedirs(self.data_temp_clips_dir, exist_ok=True)

        # Store input parameters
        self.story = story
        self.image_urls = image_urls
        self.audio_urls = audio_urls
        self.output_filename = os.path.join(self.data_temp_dir, "output.mp4")
        
        # Metadata paths
        # self.audio_metadata_path = os.path.join(self.data_temp_dir, "audioMetadata.json")
        # self.subtitles_path = os.path.join(self.data_temp_dir, "subtitles.ssa")
        # print(self.subtitles_path)
        self.data_temp_dir = os.path.normpath("data/temp")
        self.data_temp_audio_dir = os.path.normpath(os.path.join(self.data_temp_dir, "audio"))
        self.data_temp_clips_dir = os.path.normpath(os.path.join(self.data_temp_dir, "clips"))
        
        # Ensure directories exist with full path
        os.makedirs(self.data_temp_audio_dir, exist_ok=True)
        os.makedirs(self.data_temp_clips_dir, exist_ok=True)

        # Use normpath for all file paths
        self.output_filename = os.path.normpath(os.path.join(self.data_temp_dir, "output.mp4"))
        self.audio_metadata_path = os.path.normpath(os.path.join(self.data_temp_dir, "audioMetadata.json"))
        self.subtitles_path = os.path.normpath(os.path.join(self.data_temp_dir, "subtitles.ssa"))        

    def fetch_audio_metadata(self):
        """
        Downloads audio files from URLs, saves them locally,
        extracts their durations, and stores metadata in a JSON file.
        """
        audio_metadata = []

        for i, url in enumerate(self.audio_urls):
            try:
                # Download the audio file
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    temp_path = os.path.join(self.data_temp_audio_dir, f"audio_{i + 1}.mp3")
                    
                    # Save the file locally
                    with open(temp_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            f.write(chunk)
                    
                    # Get audio duration using pydub
                    audio_info = mediainfo(temp_path)
                    duration = float(audio_info["duration"])
                    
                    # Append metadata to the list
                    audio_metadata.append({
                        "file_path": temp_path,
                        "duration": duration
                    })
                else:
                    print(f"Failed to download audio from URL: {url}")
            except Exception as e:
                print(f"Error processing URL {url}: {e}")
        
        # Save metadata to a JSON file
        with open(self.audio_metadata_path, "w") as json_file:
            json.dump(audio_metadata, json_file, indent=4)
        
        print(f"Audio metadata saved to {self.audio_metadata_path}")
        return audio_metadata

    def create_ass_subtitles(self, audio_metadata):
        """
        Create subtitle file based on story and audio metadata.
        """
        sentences = [sentence.strip() for sentence in self.story.split('.') if sentence.strip()]
        
        total_duration = sum(item["duration"] for item in audio_metadata)
        
        if len(sentences) == 0:
            print("Error: No sentences found in the story.")
            return None

        duration_per_sentence = total_duration / len(sentences)
        
        def format_time(seconds):
            cs = int((seconds % 1) * 100)  # centiseconds
            seconds = int(seconds)
            hh = seconds // 3600
            mm = (seconds % 3600) // 60
            ss = seconds % 60
            return f"{hh:01}:{mm:02}:{ss:02}.{cs:02}"

        ass_header = """[Script Info]
Title: Example Subtitle File
Original Script: User
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Hack Nerd Font Propo,12,&H33ffffff,&H00000000,&H00000000,&H88000000,1,0,4,1.0,0.0,2,10,10,10,1
Style: Highlighted,Arial,12,&H00FFFF00,&H00000000,&H00000000,&H80000000,1,1,1,2.0,1.0,2,20,20,10,1

[Events]
Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        ass_events = []
        current_time = 0.0
        for sentence in sentences:
            start_time = format_time(current_time)
            end_time = format_time(current_time + duration_per_sentence)
            ass_events.append(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{sentence}")
            current_time += duration_per_sentence

        with open(self.subtitles_path, "w", encoding="utf-8") as ass_file:
            print(self.subtitles_path)
            ass_file.write(ass_header)
            ass_file.write("\n".join(ass_events))
        
        print("Subtitles generated successfully.")
        return self.subtitles_path

    def create_video_with_audio(self, audio_metadata):
        """
        Create video by combining images and audio with subtitles.
        """
        try:
            if len(self.image_urls) != len(audio_metadata):
                raise ValueError("The number of images and audio metadata entries must be the same.")
            
            temp_video_clips = []

            # Process each image and corresponding audio
            for i, (image_url, metadata) in enumerate(zip(self.image_urls, audio_metadata)):
                image_path = os.path.join(self.data_temp_clips_dir, f"image_{i + 1}.png")
                audio_path = metadata["file_path"]
                duration = metadata["duration"]
                temp_output = os.path.join(self.data_temp_clips_dir, f"clip_{i + 1}.mp4")
                
                # Download the image
                subprocess.run(["curl", "-o", image_path, image_url], check=True)

                # Combine image and audio into a video clip with fade-in and fade-out effects
                fade_duration = min(1, duration / 2)  # Ensure fade duration does not exceed half the clip duration
                command = [
                    "ffmpeg",
                    "-loop", "1",
                    "-i", image_path,
                    "-i", audio_path,
                    "-filter_complex", 
                    f"[0:v]fade=t=in:st=0:d={fade_duration},fade=t=out:st={duration - fade_duration}:d={fade_duration}[v];[1:a]anull[a]",
                    "-map", "[v]",
                    "-map", "[a]",
                    "-c:v", "libx264",
                    "-t", str(duration),
                    "-pix_fmt", "yuv420p",
                    "-shortest",
                    temp_output
                ]
                subprocess.run(command, check=True)
                temp_video_clips.append(temp_output)

            # Concatenate all video clips
            concat_file = os.path.join(self.data_temp_clips_dir, "concat_list.txt")
            with open(concat_file, "w") as f:
                for clip in temp_video_clips:
                    f.write(f"file '{os.path.abspath(clip)}'\n")
            
            # Final video assembly with subtitles
            print('place of error :',self.subtitles_path)
            subPath = self.subtitles_path.replace('\\','/')
            concat_command = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-vf", f"subtitles={subPath}",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                self.output_filename
            ]
            subprocess.run(concat_command, check=True)
            
            print(f"Video successfully created: {self.output_filename}")
        
        except Exception as e:
            print(f"Error occurred: {e}")

    def clean_temp_files(self):
        """
        Remove all temporary files and directories.
        """
        try:
            import shutil
            if os.path.exists(self.data_temp_dir):
                shutil.rmtree(self.data_temp_dir)
                print("Temporary files cleaned up successfully.")
        except Exception as e:
            print(f"Error cleaning up temporary files: {e}")

    def generateVideo(self):
        """
        Main method to generate video with audio and subtitles.
        """
        try:
            # Fetch audio metadata
            audio_metadata = self.fetch_audio_metadata()
            
            # Create subtitles
            subtitles_path = self.create_ass_subtitles(audio_metadata)
            
            # Create video with audio and subtitles
            self.create_video_with_audio(audio_metadata)

            uploaded_url = upload_video_to_cloudinary(self.output_filename)
            return uploaded_url
        
        except Exception as e:
            print(f"Video generation failed: {e}")
        finally:
            # Clean up temporary files
            self.clean_temp_files()
            pass