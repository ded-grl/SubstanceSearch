import json
import os
from src.utils.trie import Trie


def _init_substance_data():
    path = os.path.join('data', 'final_updated_drugs.json')
    assert os.path.exists(path), 'Error loading substance data. Unable to find data source file.'

    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _init_svg_file_names():
    svg_directory = os.path.join('src', 'static', 'svg')
    assert os.path.exists(svg_directory), 'Error loading svg files. Unable to find svg directory.'

    return {f for f in os.listdir(svg_directory) if f.endswith('.svg')}


def _init_substance_trie(substance_data):
    substance_trie = Trie()

    for substance_name, details in substance_data.items():
        pretty_name = details.get('pretty_name', 'Unknown')
        aliases = details.get('aliases', [])

        substance_trie.insert(substance_name, substance_name)
        substance_trie.insert(pretty_name, substance_name)
        for alias in aliases:
            substance_trie.insert(alias, substance_name)

    return substance_trie


def _init_category_card_names(substance_data):
    categories = set()
    for substance in substance_data.values():
        for category in substance.get('categories', []):
            if category.lower() not in ['inactive', 'tentative', 'habit-forming', 'common', 'ssri']:
                categories.add(category.capitalize())
    return sorted(categories)


SUBSTANCE_DATA = _init_substance_data()
SVG_FILES = _init_svg_file_names()
SUBSTANCE_TRIE = _init_substance_trie(SUBSTANCE_DATA)
CATEGORY_CARD_NAMES = _init_category_card_names(SUBSTANCE_DATA)
