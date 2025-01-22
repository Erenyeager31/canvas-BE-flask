from flask import render_template, Blueprint, jsonify, request, current_app
from app.controllers.scriptController import genNewScript,genImgPrompts
from app.controllers.imageGenController import genImagefn
from app.controllers.vectorDBcontroller import uploadDocument
import re
import os

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
    generated_text = response['generated_text']
    match = re.search(r'\{.*?\}', generated_text)
    return generated_text


@main_bp.route('/api/prompts',methods=['POST'])
def newImgPrompts():
    bodyJson = request.get_json()
    response = genImgPrompts(bodyJson['story'])
    return response

@main_bp.route('/api/genImage',methods=['POST'])
def genImage():
    bodyJson = request.get_json()
    response = genImagefn(prompts=bodyJson['prompts'])
    return response

@main_bp.route('/api/upload', methods=['GET'])
def upload():
    # upload_dir = 'app/data/upload'

    # if not os.path.exists(upload_dir):
    #     return {"error": "Upload directory does not exist"}, 400
    
    # uploaded_files = []
    # filenames = []

    # files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]

    # if not files:
    #     return {"error": "No files found in the upload directory"}, 400

    # for file in files:
    #     file_path = os.path.join(upload_dir, file)
    #     uploaded_files.append(file_path)
    #     filenames.append(file)

    # response = uploadDocument(uploaded_files, filenames)
    response = uploadDocument()
    return response