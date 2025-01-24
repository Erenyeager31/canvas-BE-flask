from app.utils.generateVideo import VideoGenerator

def videoGenController(story:str,image_urls:list,audio_urls:list):
    video_gen = VideoGenerator(story, image_urls, audio_urls)
    videoUrl = video_gen.generateVideo()
    return videoUrl
