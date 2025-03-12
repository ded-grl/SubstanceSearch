from flask import Flask
from flask_minify import Minify
from flask_cors import CORS
from src.utils import slugify
from src.blueprints.views.utils import cache
from src.blueprints.views import views_bp
from src.blueprints.api import api_bp
from src.config import DefaultConfig
from re import match


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(DefaultConfig)

    # override config with any environment variables prefixed with `FLASK_`
    app.config.from_prefixed_env()

    CORS(app, resources={
        r"/autocomplete": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET"],
            "allow_headers": ["Content-Type"]
        },
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET"],
            "allow_headers": ["Content-Type"]
        }
    })
    Minify(app=app, html=True, js=True, cssless=True)

    cache.init_app(app, config={"CACHE_TYPE": "SimpleCache"})

    # modify jinja environment
    app.jinja_env.globals.update(slugify=slugify, match=match)

    # register blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)

    return app
