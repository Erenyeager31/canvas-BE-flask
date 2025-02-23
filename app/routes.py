from flask import render_template, Blueprint, jsonify, request, current_app
from flask_cors import CORS
from app.controllers.scriptController import genNewScript, genImgPrompts
from app.controllers.imageGenController import genImagefn
from app.controllers.vectorDBcontroller import uploadDocument
from app.controllers.voiceGenController import genAudioController
from app.controllers.videoGenController import videoGenController
import re
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.utils.cloudinaryUploader import upload_audio_to_cloudinary

main_bp = Blueprint('main', __name__)
CORS(main_bp)  # Allow CORS for all routes in this blueprint

# command to run
# flask --app run.py --debug run
# pip install langchain langchain-community transformers torch accelerate -- run this command

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
    # bodyJson = request.get_json()
    # texts, url, lang = bodyJson['texts'], bodyJson['url'], bodyJson['lang']
    # # audio_lang = bodyJson.get('audio_lang','en')
    # response = genAudioController(texts, url, lang)
    # print(response)
    # print("Api response about to be sent")
    # return response
    # print("Api response sent")
    # return jsonify(response)
    try:
        bodyJson = request.get_json()
        if not bodyJson:
            return jsonify({"error": "No JSON data provided"}), 400
        
        texts = bodyJson.get('texts')
        url = bodyJson.get('url')
        lang = bodyJson.get('lang', 'en')
        
        if not texts:
            return jsonify({"error": "No texts provided"}), 400
        
        logger.info(f"Received request to generate {len(texts.split('.'))} audio files")
        
        response = genAudioController(texts, url, lang)
        logger.info("Controller processing completed")
        
        if "error" in response:
            return jsonify(response), 400
            
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in genAudio endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@main_bp.route('/api/upload', methods=['GET'])
def upload():
    response = uploadDocument()
    return jsonify(response)

@main_bp.route('/api/genVideo', methods=['POST'])
def genVideo():
    bodyJson = request.get_json()
    story, image_urls, audio_urls = bodyJson['story'], bodyJson['image_urls'], bodyJson['audio_urls']
    caption_lang = bodyJson.get('caption_lang','en')
    response = videoGenController(story, image_urls, audio_urls,caption_lang)
    return jsonify({"url": response})

@main_bp.route('/api/getWords', methods=['GET'])
def getWords():
    print("Request received")
    DBInstance = current_app.config['DB']
    fileList = DBInstance.get_all_filenames()
    # DBInstance.close_connection()
    return jsonify({"fileList": fileList})

@main_bp.route('/api/deleteAll', methods=['GET'])
def deleteWords():
    DBInstance = current_app.config['DB']
    DBInstance.delete_all_data()
    # DBInstance.close_connection()
    return jsonify({"message":"DB cleared succesfully" })

