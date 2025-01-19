from flask import Flask, Request, Response, render_template, request, jsonify, make_response
from flask_minify import Minify
from flask_caching import Cache, CachedResponse
from flask_cors import CORS
from urllib.parse import unquote
import json
import unicodedata
import re
import csv
import os
import requests
from Levenshtein import distance
from functools import wraps

app = Flask(__name__)
CORS(app, resources={
    r"/autocomplete": {
        "origins": [
            "http://localhost:5000",  # Development
            "http://1.stg.substancesearch.com" # Staging
            "https://substancesearch.org",  # Production
            "https://search.dedgrl.com"  # Production
        ],
        "methods": ["GET"],
        "allow_headers": ["Content-Type"]
    }
})
Minify(app=app, html=True, js=True, cssless=True)

cache = Cache()
cache.init_app(app, config={ "CACHE_TYPE": "SimpleCache" })

# Load the substances from JSON with UTF-8 encoding
with open('data/final_updated_drugs.json', encoding='utf-8') as f:
    substances = json.load(f)

# Get list of SVG files
svg_files = set()
svg_directory = os.path.join('static', 'svg')
if os.path.exists(svg_directory):
    svg_files = {f for f in os.listdir(svg_directory) if f.endswith('.svg')}

# Function to slugify strings for URL-friendly names
def slugify(value):
    """
    Converts a string to a URL-friendly slug.
    Only allows alphanumeric characters and single hyphens.
    """
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    # Additional validation to prevent empty or malicious slugs
    if not value or value.startswith('-') or value.endswith('-'):
        return ''
    return value

# Make slugify available in templates
app.jinja_env.globals.update(slugify=slugify)

# Add regex_match func to Jinja
def regex_match(value, pattern="", flags=0):
  return re.match(pattern, value, flags)

app.jinja_env.filters["regex_match"] = regex_match

# Create a mapping from slugs to substance names
slug_to_substance_name = {}
for substance_name, details in substances.items():
    slug = slugify(substance_name)
    slug_to_substance_name[slug] = substance_name
    # Include aliases in the slug mapping
    for alias in details.get('aliases', []):
        alias_slug = slugify(alias)
        slug_to_substance_name[alias_slug] = substance_name

# Helper function to get all unique categories and apply the necessary transformations
def get_all_categories(substances):
    categories = set()
    for substance in substances.values():
        for category in substance.get('categories', []):
            if category.lower() not in ['inactive', 'tentative', 'habit-forming', 'common', 'ssri']:
                categories.add(category.capitalize())
    return sorted(categories)

# Substance Colors
category_colors = {
    'psychedelic': '#FFB6C1',
    'dissociative': '#87CEFA',
    'stimulant': '#FFD700',
    'research-chemical': '#98FB98',
    'empathogen': '#FF69B4',
    'habit-forming': '#FFA07A',
    'opioid': '#BA55D3',
    'depressant': '#ADD8E6',
    'hallucinogen': '#FF6347',
    'entactogen': '#20B2AA',
    'deliant': '#FFFFE0',
    'antidepressant': '#FF4500',
    'sedative': '#9370DB',
    'nootropic': '#AFEEEE',
    'disassociative': '#FF7F50',
    'barbiturate': '#F08080',
    'benzodiazepine': '#FFDEAD',
    'deliriant': '#FFE4E1',
    'supplement': '#98FB98',
}

# Clean data by removing or replacing None values
def clean_data(data):
    """
    Recursively clean the data to remove None or undefined values.
    """
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [clean_data(v) for v in data if v is not None]
    return data

# Fetch theme from request cookies
def fetch_theme(request: Request) -> str:
    # Get theme
    theme = request.cookies.get('Theme', default='light', type=str)
    
    # Validate theme length to prevent cookie bloat
    if not theme or len(theme) > 10:
        return 'light'
    
    # Whitelist allowed themes
    ALLOWED_THEMES = {'light', 'dark'}
    if theme not in ALLOWED_THEMES:
        return 'light'
    
    return theme

def with_theme_cookie(view_function):
    @wraps(view_function)
    def view_function_with_theme_cookie(*args, **kwargs):
        response = view_function(*args, **kwargs)

        # if function does not return a response, do not add a cookie to it
        if (not issubclass(response.__class__, Response)):
            return response

        # if no cookie is given in the request, do not send a theme cookie back
        if (request.cookies.get('Theme', default=None) is None):
            return response

        response.set_cookie(
            'Theme',
            value=fetch_theme(request),
            max_age=31536000,  # one year
            # TODO: change this to be environment config based
            secure=request.url.startswith('https') or request.host.startswith('localhost:'),
            httponly=False,
            samesite='Lax'
        )
        return response

    return view_function_with_theme_cookie


# Route for the home page
@app.route('/')
@with_theme_cookie
def home():
    categories = get_all_categories(substances)
    return make_response(render_template('index.html', 
                                         categories=categories, 
                                         category_colors=category_colors, 
                                         theme=fetch_theme(request)))

def rank_to_display_string(rank: int) -> str:
    emoji = ''
    if rank == 1:
        emoji = '🥇 '
    elif rank == 2:
        emoji = '🥈 '
    elif rank == 3:
        emoji = '🥉 '
    return f'{emoji}{rank}'

# Route for the leaderboard
@app.route('/leaderboard')
@with_theme_cookie
@cache.cached() # one day timeout
def leaderboard():
    try:
        # setup request prerequisites
        auth_token= os.environ['GITHUB_AUTH_TOKEN'] # get auth token from environment
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {auth_token}',
            'X-Github-Api-Version': '2022-11-28'
        }
        app.logger.info("Fetching leaderboard data")
        r = requests.get(
            'https://api.github.com/repos/ded-grl/SubstanceSearch/contributors',
            headers=headers
        )

        if (not r.ok):
            raise RuntimeError(r.content)

        #parse response data
        contribution_data= r.json()
        app.logger.info("Retrieved contribution data: %s", str(contribution_data))

        leaderboard_data = [{
            'rank': rank_to_display_string(index + 1),
            'contributor': contribution['login'],
            'contributions': contribution['contributions']
        } for index, contribution in enumerate(contribution_data)]

        return CachedResponse(
            response=make_response(render_template('leaderboard.html', leaderboard_data=leaderboard_data, theme=fetch_theme(request))),
            timeout = 60 * 60 * 24 # one day
        )
    except Exception as e:
        # In case of error, fallback to static cache data in /data/leaderboard.csv
        app.logger.error(f'Failed to fetch contribution data. [{e}]')
        app.logger.error('Using cached leaderboard data instead.')

        # Read the leaderboard data from the CSV
        leaderboard_data = []
        with open('data/leaderboard.csv', 'r') as file:
            reader = csv.DictReader(file)
            for index, row in enumerate(reader):
                rank = index + 1
                leaderboard_data.append({
                    'rank': rank_to_display_string(rank),
                    'contributor': row['Contributor'],
                    'contributions': row['Contributions']
                })

        # Pass the data to the template
        return CachedResponse(
            response=make_response(render_template('leaderboard.html', leaderboard_data=leaderboard_data, theme=fetch_theme(request))),
            timeout = 60 # one minute response to retry in case of 500 level upstream errors
        )

# Route for fetching autocomplete suggestions
@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '').lower()
    limit = request.args.get('limit', 10)
    result_substance_names = set(substance_trie.search_substring(query))
    sorted_result_substance_names = sorted(result_substance_names, key=lambda substance_name: distance(substance_name.lower(), query.lower()))
    result_substances = [substances.get(substance_name) for substance_name in sorted_result_substance_names]
    results = [{
        'pretty_name': substance.get('pretty_name', 'Unknown'),
        'aliases': substance.get('aliases', []),
        'slug': slugify(substance.get('name', ''))
    } for substance in result_substances][:limit]

    return jsonify(results)

# Route for displaying substance information using slugified names
@app.route('/substance/<path:slug>')
@with_theme_cookie
def substance(slug):
    # Add validation before processing
    if not slug or len(slug) > 100:  # Reasonable maximum length
        return "Invalid slug", 400
    
    # Validate slug format
    if not re.match(r'^[a-z0-9-]+$', slug):
        return "Invalid slug format", 400
        
    decoded_slug = unquote(slug)
    substance_name = slug_to_substance_name.get(decoded_slug.lower())
    if not substance_name:
        return "Substance not found", 404
    substance_data = substances.get(substance_name)
    if not substance_data:
        return "Substance not found", 404

    # Clean the substance data to remove None values
    cleaned_substance_data = clean_data(substance_data)
    return make_response(render_template('substance.html', substance=cleaned_substance_data, category_colors=category_colors, svg_files=svg_files, theme=fetch_theme(request)))

# Route for displaying substances in a category
@app.route('/category/<path:category_slug>')
@with_theme_cookie
def category(category_slug):
    # Add validation before processing
    if not category_slug or len(category_slug) > 100:
        return "Invalid category", 400
    
    # Validate category slug format
    if not re.match(r'^[a-z0-9-]+$', category_slug):
        return "Invalid category format", 400
        
    decoded_slug = unquote(category_slug).lower()
    # Map of slugified category names to their original form
    category_name_mapping = {}
    for substance in substances.values():
        for category in substance.get('categories', []):
            category_slugified = slugify(category)
            category_name_mapping[category_slugified] = category.capitalize()
    # Get the original category name
    category_name = category_name_mapping.get(decoded_slug)
    if not category_name:
        return "Category not found", 404

    # Filter substances that belong to the category
    filtered_substances = {}
    for substance_name, details in substances.items():
        if any(slugify(cat) == decoded_slug for cat in details.get('categories', [])):
            filtered_substances[substance_name] = details

    if not filtered_substances:
        return "Category not found", 404

    return make_response(render_template('category.html', category_name=category_name, substances=filtered_substances, category_colors=category_colors, theme=fetch_theme(request)))


class SuffixTrieNodeMetadatum:
    """
    Metadata for what data a suffix trie node points to
    and which search suffix it points to
    """

    def __init__(self, data_store_index=-1, suffix_index=-1):
        assert data_store_index >= 0
        assert suffix_index >= 0

        self.data_store_index = data_store_index
        self.suffix_index = suffix_index


class SuffixTrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.metadata = []


class SuffixTrie:
    def __init__(self):
        self.root = SuffixTrieNode()
        self.data_store = []

    def insert(self, word, data):
        data_store_index = len(self.data_store)
        self.data_store.append(data)

        for suffix_index in range(len(word) + 1):  # all suffixes including the empty string
            self._insert_suffix(word[suffix_index:], suffix_index, data_store_index)

    def _insert_suffix(self, suffix: str, suffix_index: int, data_store_index: int):
        node = self.root
        for char in suffix.lower():
            if char not in node.children:
                node.children[char] = SuffixTrieNode()
            node = node.children[char]
        node.is_end = True

        suffix_node_metadatum = SuffixTrieNodeMetadatum(data_store_index, suffix_index)
        node.metadata.append(suffix_node_metadatum)

    def search_substring(self, substring):
        node = self.root
        data_store_indices = []

        for char in substring.lower():
            if char not in node.children:
                return []
            node = node.children[char]

        self._collect_words(node, substring, data_store_indices)
        results = [self.data_store[data_store_index] for data_store_index in set(data_store_indices)]

        return results

    def _collect_words(self, node, substring, data_store_indices):
        if node.is_end:
            data_store_indices.extend([metadatum.data_store_index for metadatum in node.metadata])

        for char, child in node.children.items():
            self._collect_words(child, substring + char, data_store_indices)


substance_trie = SuffixTrie()
for substance_name, details in substances.items():
    pretty_name = details.get('pretty_name', 'Unknown')
    aliases = details.get('aliases', [])

    substance_trie.insert(substance_name, substance_name)
    substance_trie.insert(pretty_name, substance_name)

    for alias in aliases:
        substance_trie.insert(alias, substance_name)

if __name__ == '__main__':
    app.run(debug=True)
