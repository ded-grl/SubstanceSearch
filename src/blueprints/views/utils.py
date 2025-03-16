from flask import Request
from src.data import AVAILABLE_SOURCES, DEFAULT_SOURCE, DataSource
from flask_caching import Cache

# Initialize cache
cache = Cache()

def _fetch_theme(request: Request) -> str:
    """Fetch the theme preference from the query parameters."""
    theme = request.args.get('theme', '')
    if theme in ['dark', 'light']:
        return theme
    
    # check cookies
    theme = request.cookies.get('theme', '')
    if theme in ['dark', 'light']:
        return theme
    
    return 'light'  # default theme


def _fetch_data_source(request: Request) -> DataSource:
    """Fetch the preferred data source from the query parameters."""
    source = request.args.get('source', '')
    
    # check if source is valid
    if source in AVAILABLE_SOURCES:
        return source
    
    return DEFAULT_SOURCE


def _rank_to_display_string(rank: int) -> str:
    """Convert a numerical rank to a display string with emoji."""
    emoji = ''
    if rank == 1:
        emoji = '🥇 '
    elif rank == 2:
        emoji = '🥈 '
    elif rank == 3:
        emoji = '🥉 '
    return f'{emoji}{rank}' 