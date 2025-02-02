from flask import render_template, Blueprint, jsonify, request, current_app
from flask_cors import CORS
from app.controllers.scriptController import genNewScript, genImgPrompts
from app.controllers.imageGenController import genImagefn
from app.controllers.vectorDBcontroller import uploadDocument
from app.controllers.voiceGenController import genAudioController
from app.controllers.videoGenController import videoGenController
import re
import os

from app.utils.cloudinaryUploader import upload_audio_to_cloudinary

main_bp = Blueprint('main', __name__)
CORS(main_bp)  # Allow CORS for all routes in this blueprint

# command to run
# flask --app run.py --debug run

os.makedirs("uploads", exist_ok=True)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('index.html')

@main_bp.route('/api/newScript', methods=['POST'])
def newScriptRoute():
    bodyJson = request.get_json()
    userDocURL = bodyJson.get('userDocURL',None)
    response = genNewScript(bodyJson,userDocURL)
    return response

@main_bp.route('/api/prompts', methods=['POST'])
def newImgPrompts():
    bodyJson = request.get_json()
    print(bodyJson)
    response = genImgPrompts(bodyJson['story'])
    return jsonify({'prompts': response})

@main_bp.route('/api/genImage', methods=['POST'])
def genImage():
    bodyJson = request.get_json()
    response = genImagefn(prompts=bodyJson['prompts'])
    return jsonify(response)

@main_bp.route('/api/genAudio', methods=['POST'])
def genAudio():
    bodyJson = request.get_json()
    texts, url, lang = bodyJson['texts'], bodyJson['url'], bodyJson['lang']
    response = genAudioController(texts, url, lang)
    print(response)
    return jsonify(response)

@main_bp.route('/api/upload', methods=['GET'])
def upload():
    response = uploadDocument()
    return jsonify(response)

@main_bp.route('/api/genVideo', methods=['POST'])
def genVideo():
    bodyJson = request.get_json()
    story, image_urls, audio_urls = bodyJson['story'], bodyJson['image_urls'], bodyJson['audio_urls']
    response = videoGenController(story, image_urls, audio_urls)
    return jsonify({"url": response})
