from flask import Flask

from Birdwatching.utils.databases import init_db
from .blueprints.auth import auth_bp
from .blueprints.posts import posts_bp
from .blueprints.users import users_bp
from .blueprints.admin import admin_bp
from .blueprints.main import main_bp
from .blueprints.aichatbot import chatbot_bp
from Birdwatching.utils.middlewares import is_blacklisted, create_presigned_url
from .config import Config
import os
from dotenv import load_dotenv

def create_app():
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

    app = Flask(__name__)
    app.secret_key = os.environ("SECRET_KEY")
    app.config.from_object(Config)
    app.jinja_env.globals['create_presigned_url'] = create_presigned_url

    init_db(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(posts_bp, url_prefix="/posts")
    app.register_blueprint(users_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(chatbot_bp)

    @app.before_request
    def before_request():
        resp = is_blacklisted()
        if resp:
            return resp

    return app
