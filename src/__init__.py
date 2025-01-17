from flask import Flask
from flask_minify import Minify
from flask_cors import CORS
from .utils import slugify
from .views import cache, home, leaderboard, autocomplete, substance, category
from re import match


def create_app():
    app = Flask(__name__)
    CORS(app, resources={
        r"/autocomplete": {
            "origins": [
                "http://localhost:5000",  # Development
                "http://1.stg.substancesearch.com"  # Staging
                "https://substancesearch.org",  # Production
                "https://search.dedgrl.com"  # Production
            ],
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
