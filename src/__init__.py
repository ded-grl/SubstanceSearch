from flask import Flask
from flask_minify import Minify
from flask_cors import CORS
from src.utils import slugify
from src.views import cache, home, leaderboard, autocomplete, substance, category
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
        }
    })
    Minify(app=app, html=True, js=True, cssless=True)

    cache.init_app(app, config={"CACHE_TYPE": "SimpleCache"})

    # modify jinja environment
    app.jinja_env.globals.update(slugify=slugify, match=match)

    # register app views
    app.add_url_rule("/", view_func=home)
    app.add_url_rule("/leaderboard", view_func=leaderboard)
    app.add_url_rule("/autocomplete", view_func=autocomplete)
    app.add_url_rule("/substance/<path:slug>", view_func=substance)
    app.add_url_rule("/category/<path:category_slug>", view_func=category)

    return app
