# app/__init__.py

from flask import Flask
from .routes import main_bp
from .models.phi2textgen import Phi2Generator
from .models.sdxlImageGen import ImageGenerator
from .models.contextRetrival import ContextRetriever

def create_app():
    app = Flask(__name__)

    app.config['ScriptGenModel'] = Phi2Generator()
    app.config['ImageGenModel'] = ImageGenerator()
    app.config['contextModel'] = ContextRetriever()

    app.register_blueprint(main_bp)
    return app
