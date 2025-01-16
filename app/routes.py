from flask import render_template, Blueprint, jsonify, request
from app.controllers.scriptController import genNewScript,genImgPrompts
from app.controllers.imageGenController import generate_images

main_bp = Blueprint('main', __name__)

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
    return response

@main_bp.route('/api/prompts',methods=['POST'])
def newImgPrompts():
    bodyJson = request.get_json()
    response = genImgPrompts(bodyJson['story'])
    return response

@main_bp.route('/api/genImage',methods=['POST'])
def genImage():
    bodyJson = request.get_json()
    response = generate_images(prompts=bodyJson['prompts'])
    return response