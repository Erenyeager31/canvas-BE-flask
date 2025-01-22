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

@main_bp.route('/api/upload',methods=['POST'])
def upload():
    # List to store file data and filenames
    uploaded_files = []
    filenames = []

    # Retrieve multiple files from the request
    if 'files' not in request.files:
        return {"error": "No files part in the request"}, 400

    files = request.files.getlist('files')  # Get all files as a list

    for file in files:
        if file.filename != '':
            # Save file to a directory (e.g., 'uploads/')
            file_path = f"uploads/{file.filename}"
            file.save(file_path)

            # Append file path and filename to lists
            uploaded_files.append(file_path)
            filenames.append(file.filename)

    # Process the files and filenames (if needed)
    response = uploadDocument(uploaded_files, filenames)
    return response