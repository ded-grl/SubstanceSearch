from flask import (
    Request,
    Response,
    render_template,
    request,
    jsonify,
    make_response,
    current_app
)
from flask_caching import Cache, CachedResponse
import os
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
import requests
import csv
from src.utils import validate_slug, slugify
from urllib.parse import unquote
from Levenshtein import distance


def _fetch_theme(request: Request) -> str:
    """
    Fetch theme from request cookies.
    """
    theme = request.cookies.get('Theme', default='light', type=str)

    # Validate theme length to prevent cookie bloat
    if not theme or len(theme) > 10:
        return 'light'

    # Whitelist allowed themes
    ALLOWED_THEMES = {'light', 'dark'}
    if theme not in ALLOWED_THEMES:
        return 'light'

    return theme


def _fetch_data_source(request: Request) -> DataSource:
    """
    Fetch data source from request cookies or query params.
    """
    # First check query params
    source = request.args.get('source', '').lower()
    
    # Then check cookies
    if not source:
        source = request.cookies.get('DataSource', '').lower()
    
    # Validate source
    if source in AVAILABLE_SOURCES:
        return source
    
    return DEFAULT_SOURCE


cache = Cache()


def home() -> Response:
    return make_response(render_template(
        'index.html',
        categories=CATEGORY_CARD_NAMES,
        theme=_fetch_theme(request)
    ))


def _rank_to_display_string(rank: int) -> str:
    emoji = ''
    if rank == 1:
        emoji = '🥇 '
    elif rank == 2:
        emoji = '🥈 '
    elif rank == 3:
        emoji = '🥉 '
    return f'{emoji}{rank}'


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

        if (not r.ok):
            raise RuntimeError(r.content)

        # parse response data
        contribution_data = r.json()
        current_app.logger.info(
            "Retrieved contribution data: %s", str(contribution_data)
        )

        leaderboard_data = [{
            'rank': _rank_to_display_string(index + 1),
            'contributor': contribution['login'],
            'contributions': contribution['contributions']
        } for index, contribution in enumerate(contribution_data)]

        rendered_template = render_template(
            'leaderboard.html',
            leaderboard_data=leaderboard_data,
            theme=_fetch_theme(request)
        )

        return CachedResponse(
            response=make_response(rendered_template),
            timeout=60 * 60 * 24  # one day
        )
    except Exception as e:
        # In case of error, fallback to static cache data in /data/leaderboard.csv
        current_app.logger.error(f'Failed to fetch contribution data. [{e}]')
        current_app.logger.error('Using cached leaderboard data instead.')

        # Read the leaderboard data from the CSV
        leaderboard_data = []
        path = os.path.join('data', 'leaderboard.csv')
        with open(path, 'r') as file:
            reader = csv.DictReader(file)
            for index, row in enumerate(reader):
                rank = index + 1
                leaderboard_data.append({
                    'rank': _rank_to_display_string(rank),
                    'contributor': row['Contributor'],
                    'contributions': row['Contributions']
                })

        rendered_template = render_template(
            'leaderboard.html',
            leaderboard_data=leaderboard_data,
            theme=_fetch_theme(request)
        )

        # Pass the data to the template
        return CachedResponse(
            response=make_response(rendered_template),
            timeout=60  # one minute response to retry in case of 500 level upstream errors
        )


# Route for fetching autocomplete suggestions
def autocomplete() -> Response:
    query = request.args.get('query', '').lower()
    limit = request.args.get('limit', 10)
    source = _fetch_data_source(request)
    
    result_substance_names = set(SUBSTANCE_TRIE.search_substring(query))
    sorted_result_substance_names = sorted(result_substance_names, key=lambda substance_name: distance(substance_name.lower(), query.lower()))
    
    # Get data from user's preferred source
    substance_data = get_substance_data_for_source(source)
    result_substances = []
    
    # Process each substance to include TripSit categories
    for substance_name in sorted_result_substance_names:
        substance = substance_data.get(substance_name)
        if substance:
            # Get TripSit categories if available
            tripsit_data = get_substance_data_for_source('tripsit')
            if substance_name in tripsit_data and tripsit_data[substance_name].get('categories'):
                substance['categories'] = tripsit_data[substance_name]['categories']
            result_substances.append(substance)
    
    results = [{
        'pretty_name': substance.get('pretty_name', 'Unknown'),
        'aliases': substance.get('aliases', []),
        'slug': slugify(substance.get('name', ''))
    } for substance in result_substances][:limit]

    return jsonify(results)


# Route for displaying substance information using slugified names
def substance(slug: str) -> Response:
    is_valid_slug, slug_validation_error_mesage = validate_slug(slug)
    if (not is_valid_slug):
        return make_response(slug_validation_error_mesage, 400)

    decoded_slug = unquote(slug)
    substance_name = SLUG_TO_SUBSTANCE_NAME.get(decoded_slug.lower(), '')
    
    # Get data from both sources
    substance_data = RAW_SUBSTANCE_DATA.get(substance_name, {})
    if not substance_data:
        return make_response("Substance not found", 404)

    # Get current source
    source = _fetch_data_source(request)
    
    # Get the substance data for the selected source
    substance_info = substance_data.get(source, {})
    
    # Always use TripSit categories if available
    if 'tripsit' in substance_data and substance_data['tripsit'].get('categories'):
        substance_info['categories'] = substance_data['tripsit']['categories']
    
    # Create response
    response = make_response(render_template(
        'substance.html',
        substance=substance_info,
        substance_name=substance_name,
        current_source=source,
        available_sources=AVAILABLE_SOURCES,
        all_sources_data=substance_data,
        svg_files=SVG_FILES,
        theme=_fetch_theme(request)
    ))
    
    # Set source cookie
    response.set_cookie('DataSource', source)
    
    return response


# Route for displaying substances in a category
def category(category_slug: str) -> Response:
    # Add validation before processing
    is_valid_slug, slug_validation_error_mesage = validate_slug(category_slug)
    if (not is_valid_slug):
        return make_response(slug_validation_error_mesage, 400)

    decoded_slug = unquote(category_slug).lower()
    user_source = _fetch_data_source(request)
    
    # Always use TripSit data for category listings
    tripsit_data = get_substance_data_for_source('tripsit')

    # Map of slugified category names to their original form
    category_name_mapping = {}
    for substance in tripsit_data.values():
        for category in substance.get('categories', []):
            category_slugified = slugify(category)
            category_name_mapping[category_slugified] = category.capitalize()

    # Get the original category name
    category_name = category_name_mapping.get(decoded_slug)
    if not category_name:
        return make_response("Category not found", 404)

    # Filter substances that belong to the category using TripSit data
    filtered_substances = {}
    for substance_name, details in tripsit_data.items():
        if any(slugify(cat) == decoded_slug for cat in details.get('categories', [])):
            # Get substance data from user's preferred source
            source_data = get_substance_data_for_source(user_source)
            if substance_name in source_data:
                filtered_substances[substance_name] = source_data[substance_name]
            else:
                # Fallback to TripSit data if substance not found in preferred source
                filtered_substances[substance_name] = details

    if not filtered_substances:
        return make_response("Category not found", 404)

    response = make_response(render_template(
        'category.html',
        category_name=category_name,
        substances=filtered_substances,
        current_source=user_source,
        theme=_fetch_theme(request)
    ))
    
    # Set source cookie
    response.set_cookie('DataSource', user_source)
    
    return response


# Route for disclaimer page
def disclaimer() -> Response:
    return make_response(render_template(
        'disclaimer.html',
        theme=_fetch_theme(request)
    ))

