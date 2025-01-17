from flask import (
    Request,
    render_template,
    request,
    jsonify,
    make_response,
    current_app
)
from flask_caching import Cache, CachedResponse
import os
from src.data import (
    SUBSTANCE_DATA,
    SUBSTANCE_TRIE,
    CATEGORY_CARD_NAMES,
    SVG_FILES
)
import requests
import csv
from src.utils import validate_slug, clean_data, slugify
from urllib.parse import unquote


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


cache = Cache()


def home():
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
def leaderboard():
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
def autocomplete():
    query = request.args.get('query', '').lower()
    results = SUBSTANCE_TRIE.search_prefix(query)
    return jsonify(results)


# Route for displaying substance information using slugified names
def substance(slug):
    is_valid_slug, slug_validation_error_mesage = validate_slug(slug)
    if (not is_valid_slug):
        return slug_validation_error_mesage, 400

    decoded_slug = unquote(slug)
    substance_name = SUBSTANCE_TRIE.get(decoded_slug.lower()).get('name', None)
    substance_data = SUBSTANCE_DATA.get(substance_name, None)

    if substance_data is None:
        return "Substance not found", 404

    # Clean the substance data to remove None values
    cleaned_substance_data = clean_data(substance_data)
    return render_template(
        'substance.html',
        substance=cleaned_substance_data,
        svg_files=SVG_FILES,
        theme=_fetch_theme(request)
    )


# Route for displaying substances in a category
def category(category_slug):
    # Add validation before processing
    is_valid_slug, slug_validation_error_mesage = validate_slug(category_slug)
    if (not is_valid_slug):
        return slug_validation_error_mesage, 400

    decoded_slug = unquote(category_slug).lower()

    # Map of slugified category names to their original form
    category_name_mapping = {}
    for substance in SUBSTANCE_DATA.values():
        for category in substance.get('categories', []):
            category_slugified = slugify(category)
            category_name_mapping[category_slugified] = category.capitalize()

    # Get the original category name
    category_name = category_name_mapping.get(decoded_slug)
    if not category_name:
        return "Category not found", 404

    # Filter substances that belong to the category
    filtered_substances = {}
    for substance_name, details in SUBSTANCE_DATA.items():
        if any(slugify(cat) == decoded_slug for cat in details.get('categories', [])):
            filtered_substances[substance_name] = details

    if not filtered_substances:
        return "Category not found", 404

    return render_template(
        'category.html',
        category_name=category_name,
        substances=filtered_substances,
        theme=_fetch_theme(request)
    )
