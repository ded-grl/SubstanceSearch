"""
Main views blueprint for handling frontend routes.
"""

from flask import Blueprint

views_bp = Blueprint('views', __name__)

from . import routes 