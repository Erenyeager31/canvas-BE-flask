from flask import render_template, Blueprint, jsonify, request, current_app
from app.controllers.scriptController import genNewScript,genImgPrompts
from app.controllers.imageGenController import genImagefn
from app.controllers.vectorDBcontroller import uploadDocument
from app.controllers.voiceGenController import genAudioController
from app.controllers.videoGenController import videoGenController
import re
import os

from app.utils.cloudinaryUploader import upload_audio_to_cloudinary

main_bp = Blueprint('main', __name__)

# UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
os.makedirs("uploads", exist_ok=True)

# command to run
# flask --app run.py --debug run

@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('index.html')

@main_bp.route('/api/newScript',methods=['POST'])
def newScriptRoute():
    bodyJson = request.get_json()
    response = genNewScript(bodyJson)
    # generated_text = response['generated_text']
    # match = re.search(r'\{.*?\}', generated_text)
    return response


@main_bp.route('/api/prompts',methods=['POST'])
def newImgPrompts():
    bodyJson = request.get_json()
    print(bodyJson)
    response = genImgPrompts(bodyJson['story'])
    return response

@main_bp.route('/api/genImage',methods=['POST'])
def genImage():
    bodyJson = request.get_json()
    response = genImagefn(prompts=bodyJson['prompts'])
    return response


@main_bp.route('/api/genAudio',methods=['POST'])
def genAudio():
    bodyJson = request.get_json()
    texts, url = bodyJson['texts'], bodyJson['url']
    response = genAudioController(texts, url)
    return response

@main_bp.route('/api/upload', methods=['GET'])
def upload():
    response = uploadDocument()
    return response

# import os

# def demofn():
#     current_dir = os.getcwd()  # Gets the current working directory
#     file_path = os.path.join(current_dir, "app/data/upload/demo.wav")  # Constructs the path
    
#     url = upload_audio_to_cloudinary([file_path])  # Use the dynamically constructed file path
#     print(url)

# demofn()
@main_bp.route('/api/genVideo', methods=['POST'])
def genVideo():
    bodyJson = request.get_json()
    # post items : story, image_urls, audio_urls
    story,image_urls,audio_urls = bodyJson['story'],bodyJson['image_urls'],bodyJson['audio_urls']
    response = videoGenController(story,image_urls,audio_urls)
    return {
        "url":response
        }