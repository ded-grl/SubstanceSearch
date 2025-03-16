from flask import jsonify, make_response, Response
from src.data import (
    RAW_SUBSTANCE_DATA,
    SLUG_TO_SUBSTANCE_NAME,
    get_substance_data_for_source,
    DataSource,
    AVAILABLE_SOURCES
)
from src.utils import validate_slug
from urllib.parse import unquote

def api_substance(slug: str) -> Response:
    """API endpoint to get substance data for all sources or a specific source."""
    # Validate slug
    is_valid_slug, slug_validation_error_message = validate_slug(slug)
    if not is_valid_slug:
        return make_response({"error": slug_validation_error_message}, 400)

    # Get substance name from slug
    decoded_slug = unquote(slug)
    substance_name = SLUG_TO_SUBSTANCE_NAME.get(decoded_slug.lower(), '')
    
    # Get substance data
    substance_data = RAW_SUBSTANCE_DATA.get(substance_name, {})
    if not substance_data:
        return make_response({"error": "Substance not found"}, 404)

    return jsonify(substance_data)

def api_substance_source(slug: str, source: str) -> Response:
    """API endpoint to get substance data for a specific source."""
    # Validate source
    if source not in AVAILABLE_SOURCES:
        return make_response({"error": f"Invalid source. Available sources: {', '.join(AVAILABLE_SOURCES)}"}, 400)

    # Validate slug
    is_valid_slug, slug_validation_error_message = validate_slug(slug)
    if not is_valid_slug:
        return make_response({"error": slug_validation_error_message}, 400)

    # Get substance name from slug
    decoded_slug = unquote(slug)
    substance_name = SLUG_TO_SUBSTANCE_NAME.get(decoded_slug.lower(), '')
    
    # Get substance data
    substance_data = RAW_SUBSTANCE_DATA.get(substance_name, {})
    if not substance_data:
        return make_response({"error": "Substance not found"}, 404)

    # Get data for specific source
    source_data = substance_data.get(source)
    if not source_data:
        return make_response({"error": f"No data available for source: {source}"}, 404)

    return jsonify(source_data) 