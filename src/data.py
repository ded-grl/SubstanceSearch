import json
import os
from src.utils.trie import SuffixTrie
from src.utils import slugify
from typing import Set, List, Dict, Optional, Literal

DataSource = Literal['tripsit', 'psychonautwiki']

AVAILABLE_SOURCES: List[DataSource] = ['tripsit', 'psychonautwiki']
DEFAULT_SOURCE: DataSource = 'tripsit'

def _validate_substance_data(substance_data: Dict) -> None:
    """
    Basic validation of substance data structure.
    Skips validation of any None values.
    """
    assert substance_data is not None
    
    if isinstance(substance_data, dict):
        for key, value in substance_data.items():
            if isinstance(value, (dict, list)) and value is not None:
                _validate_substance_data(value)
    elif isinstance(substance_data, list):
        for value in substance_data:
            if isinstance(value, (dict, list)) and value is not None:
                _validate_substance_data(value)

def _get_substance_data_for_source(raw_data: Dict, source: DataSource) -> Dict:
    """
    Extract substance data for a specific source from the raw data.
    """
    processed_data = {}
    for substance_name, substance_data in raw_data.items():
        if source in substance_data:
            processed_data[substance_name] = substance_data[source]
    return processed_data

def _init_substance_data() -> Dict[str, Dict]:
    """
    Load and validate substance data from the JSON file.
    Returns a dictionary mapping substance names to their data.
    Raises FileNotFoundError if data file is missing.
    Raises JSONDecodeError if data file is invalid JSON.
    Raises AssertionError if data validation fails.
    """
    path = os.path.join('data', 'datamed', 'data.json')
    
    # Load from data.json
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
            
        # Validate data structure
        if not isinstance(data, dict):
            raise AssertionError(f'Expected dictionary data, got {type(data)}')
            
        # Validate each substance has required source data
        for substance_name, substance_data in data.items():
            if not isinstance(substance_data, dict):
                raise AssertionError(f'Invalid data format for substance {substance_name}')
            if not any(source in substance_data for source in AVAILABLE_SOURCES):
                raise AssertionError(f'Substance {substance_name} missing required source data')
        
        _validate_substance_data(data)
        return data
        
    except FileNotFoundError:
        raise FileNotFoundError('Data file (data.json) not found. This file should exist in the repository. Please clone the repository again or fetch the data files.')
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f'Invalid JSON in data file: {str(e)}', e.doc, e.pos)

def _init_svg_file_names() -> Set[str]:
    svg_directory = os.path.join('src', 'static', 'svg')
    assert os.path.exists(
        svg_directory), 'Error loading svg files. Unable to find svg directory.'

    return {f for f in os.listdir(svg_directory) if f.endswith('.svg')}

def _init_substance_trie(substance_data: Dict, source: DataSource = 'tripsit') -> SuffixTrie[str]:
    substance_trie: SuffixTrie[str] = SuffixTrie()
    source_data = _get_substance_data_for_source(substance_data, source)

    for substance_name, details in source_data.items():
        pretty_name = details.get('pretty_name', 'Unknown')
        aliases = details.get('aliases', [])

        substance_trie.insert(substance_name, substance_name)
        substance_trie.insert(pretty_name, substance_name)
        for alias in aliases:
            substance_trie.insert(alias, substance_name)

    return substance_trie

def _init_category_card_names(substance_data: Dict, source: DataSource = 'tripsit') -> List[str]:
    """
    Initialize category card names using TripSit data only.
    """
    categories: Set[str] = set()
    # Always use TripSit data for categories
    source_data = _get_substance_data_for_source(substance_data, 'tripsit')
    
    for substance in source_data.values():
        for category in substance.get('categories', []):
            if category.lower() not in ['inactive', 'tentative', 'habit-forming', 'common', 'ssri']:
                categories.add(category.capitalize())
    return sorted(categories)

def _init_slug_to_substance_name_map(substance_data: Dict, source: DataSource = 'tripsit') -> Dict[str, str]:
    map: Dict[str, str] = {}
    source_data = _get_substance_data_for_source(substance_data, source)
    
    for substance_name in source_data.keys():
        slug = slugify(substance_name)
        assert slug not in map, f'Two substance names map to the same slug[\"{slug}\"]: {substance_name} and {map.get(slug)}'
        map[slug] = substance_name

    return map

# Initialize raw data that contains all sources
RAW_SUBSTANCE_DATA = _init_substance_data()

# Pre-process and cache substance data for each available source
CACHED_SUBSTANCE_DATA = {
    source: _get_substance_data_for_source(RAW_SUBSTANCE_DATA, source) 
    for source in AVAILABLE_SOURCES
}

# Initialize data structures with TripSit as default
SVG_FILES = _init_svg_file_names()
SUBSTANCE_TRIE = _init_substance_trie(RAW_SUBSTANCE_DATA)
# Always use TripSit data for categories
CATEGORY_CARD_NAMES = _init_category_card_names(RAW_SUBSTANCE_DATA, 'tripsit')
SLUG_TO_SUBSTANCE_NAME = _init_slug_to_substance_name_map(RAW_SUBSTANCE_DATA)

def get_substance_data_for_source(source: DataSource = 'tripsit') -> Dict:
    """
    Get substance data for a specific source.
    Returns cached data to avoid reprocessing on every call.
    """
    return CACHED_SUBSTANCE_DATA[source]
