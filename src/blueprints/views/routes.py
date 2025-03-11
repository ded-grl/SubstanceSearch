from flask import (
    Request,
    Response,
    render_template,
    request,
    jsonify,
    make_response,
    current_app
)
import requests
import csv
from src.data import (
    RAW_SUBSTANCE_DATA,
    SUBSTANCE_TRIE,
    CATEGORY_CARD_NAMES,
    SVG_FILES,
    SLUG_TO_SUBSTANCE_NAME,
    get_substance_data_for_source,
    DEFAULT_SOURCE,
    AVAILABLE_SOURCES,
    DataSource
)
from src.utils import validate_slug, slugify
from src.blueprints.views.utils import cache, _fetch_theme, _fetch_data_source, _rank_to_display_string
from src.blueprints.views import views_bp
from urllib.parse import unquote


@views_bp.route('/')
def home() -> Response:
    return make_response(render_template(
        'index.html',
        categories=CATEGORY_CARD_NAMES,
        theme=_fetch_theme(request)
    ))


@views_bp.route('/leaderboard')
@cache.cached()  # one day timeout
def leaderboard() -> Response:
    try:
        # setup request prerequisites
        auth_token = current_app.config['GITHUB_AUTH_TOKEN']
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {auth_token}',
            'X-Github-Api-Version': '2022-11-28'
        }
        current_app.logger.info("Fetching leaderboard data")
        r = requests.get(
            'https://api.github.com/repos/ded-grl/SubstanceSearch/contributors',
            headers=headers
        )
        contributors = r.json()

        # sort by contributions
        contributors.sort(key=lambda x: x['contributions'], reverse=True)
        
        # add rank and label the contributors
        for i, contributor in enumerate(contributors):
            contributor['rank'] = _rank_to_display_string(i + 1)

        return make_response(render_template(
            'leaderboard.html',
            title='Leaderboard',
            contributors=contributors,
            theme=_fetch_theme(request)
        ))
    except Exception as e:
        current_app.logger.error(f"Error fetching leaderboard data: {e}")
        return make_response(render_template(
            'error.html',
            title='Error',
            message='Error fetching leaderboard data.',
            theme=_fetch_theme(request)
        ), 500)


@views_bp.route('/autocomplete')
def autocomplete() -> Response:
    query = request.args.get('query', '').lower()
    if not query or len(query) <= 1:
        return jsonify([])

    # Use search_substring method which is the correct method for the SuffixTrie
    result_substance_names = SUBSTANCE_TRIE.search_substring(query)
    
    # We need to return data in the format expected by the frontend
    results = []
    for substance_name in result_substance_names[:10]:  # Limit to 10 results
        # Get substance data
        substance_data = RAW_SUBSTANCE_DATA.get(substance_name, {})
        if not substance_data:
            continue
            
        # Get the data from TripSit as it's more consistent
        tripsit_data = substance_data.get('tripsit', {})
        if not tripsit_data:
            continue
            
        # Format the data as expected by the frontend
        result = {
            'name': substance_name,
            'pretty_name': tripsit_data.get('pretty_name', substance_name),
            'aliases': tripsit_data.get('aliases', []),
            'slug': slugify(substance_name)
        }
        results.append(result)
    
    return jsonify(results)


@views_bp.route('/substance/<path:slug>')
def substance(slug: str) -> Response:
    # Validate slug
    is_valid_slug, slug_validation_error_message = validate_slug(slug)
    if not is_valid_slug:
        return make_response(render_template(
            'error.html',
            title='Error',
            message=slug_validation_error_message,
            theme=_fetch_theme(request)
        ), 400)

    # Get substance name from slug
    decoded_slug = unquote(slug)
    substance_name = SLUG_TO_SUBSTANCE_NAME.get(decoded_slug.lower(), '')
    
    # Get substance data from the raw data
    substance_data = RAW_SUBSTANCE_DATA.get(substance_name, {})
    if not substance_data:
        return make_response(render_template(
            'error.html',
            title='Not Found',
            message='Substance not found.',
            theme=_fetch_theme(request)
        ), 404)

    # Get current source
    source = _fetch_data_source(request)
    
    # Check if the source has data for this substance, otherwise fallback to an available source
    if source not in substance_data or not substance_data.get(source):
        # Use the first source that has data as fallback
        for available_source in AVAILABLE_SOURCES:
            if available_source in substance_data and substance_data.get(available_source):
                source = available_source
                break
    
    # Get the substance data for the selected source
    substance_info = substance_data.get(source, {})
    substance_info['name'] = substance_name  # Ensure the name is included
    
    # Always use TripSit categories if available
    if 'tripsit' in substance_data and substance_data['tripsit'].get('categories'):
        substance_info['categories'] = substance_data['tripsit']['categories']
    
    # Filter available sources to only those that actually have data for this substance
    substance_available_sources = []
    for src in AVAILABLE_SOURCES:
        if src in substance_data and substance_data.get(src):
            substance_available_sources.append(src)
    
    # SVG_FILES is a set, so check if the SVG exists in the set
    svg_filename = f"{substance_name.lower()}.svg"
    has_svg = svg_filename in SVG_FILES
    
    # Add other necessary data for the template
    all_sources_data = substance_data
    
    return make_response(render_template(
        'substance.html',
        substance=substance_info,  # Use 'substance' as the variable name to match the template
        substance_name=substance_name,
        current_source=source,
        available_sources=substance_available_sources,
        all_sources_data=all_sources_data,
        svg_files=SVG_FILES,
        theme=_fetch_theme(request)
    ))


@views_bp.route('/category/<path:category_slug>')
def category(category_slug: str) -> Response:
    # Add validation before processing
    is_valid_slug, slug_validation_error_message = validate_slug(category_slug)
    if not is_valid_slug:
        return make_response(render_template(
            'error.html',
            title='Error',
            message=slug_validation_error_message,
            theme=_fetch_theme(request)
        ), 400)

    # Find category name from slug
    category_name = None
    for cat in CATEGORY_CARD_NAMES:  # CATEGORY_CARD_NAMES is a list, not a dict
        if slugify(cat).lower() == category_slug.lower():
            category_name = cat
            break

    if not category_name:
        return make_response(render_template(
            'error.html',
            title='Not Found',
            message='Category not found.',
            theme=_fetch_theme(request)
        ), 404)

    # Find substances in this category
    substances = []
    for substance_name, substance_data in RAW_SUBSTANCE_DATA.items():
        # Check if the substance belongs to this category
        if source_data := substance_data.get('tripsit', {}):  # Use tripsit data for categories
            if 'categories' in source_data and category_name.lower() in [c.lower() for c in source_data.get('categories', [])]:
                substance_slug = slugify(substance_name)
                # Check if SVG exists
                has_svg = substance_name.lower() in SVG_FILES
                substances.append({
                    'name': substance_name,
                    'slug': substance_slug,
                    'has_svg': has_svg
                })

    return make_response(render_template(
        'category.html',
        title=f'Category: {category_name}',
        category_name=category_name,
        substances=substances,
        theme=_fetch_theme(request)
    ))


@views_bp.route('/disclaimer')
def disclaimer() -> Response:
    return make_response(render_template(
        'disclaimer.html',
        title='Disclaimer',
        theme=_fetch_theme(request)
    ))

@views_bp.route('/api/docs')
def api_docs() -> Response:
    return make_response(render_template(
        'api_docs.html',
        title='API Documentation',
        theme=_fetch_theme(request)
    )) 