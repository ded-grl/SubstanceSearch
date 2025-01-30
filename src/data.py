import json
import os
from src.utils.trie import SuffixTrie
from src.utils import slugify
from typing import Set, List, Dict


def _validate_substance_data(substance_data: Dict) -> None:
    """
    Validate that no null (ie None) values are present in the substance data.
    """
    assert substance_data is not None

    if isinstance(substance_data, dict):
        [_validate_substance_data(v) for v in substance_data.values()]
    elif isinstance(substance_data, list):
        [_validate_substance_data(ele) for ele in substance_data]


def _init_substance_data() -> Dict:
    path = os.path.join('data', 'tripsit.json')
    assert os.path.exists(
        path), 'Error loading substance data. Unable to find data source file.'

    with open(path, encoding='utf-8') as f:
        data = json.load(f)
        _validate_substance_data(data)
        return data


def _init_svg_file_names() -> Set[str]:
    svg_directory = os.path.join('src', 'static', 'svg')
    assert os.path.exists(
        svg_directory), 'Error loading svg files. Unable to find svg directory.'

    return {f for f in os.listdir(svg_directory) if f.endswith('.svg')}


def _init_substance_trie(substance_data: Dict) -> SuffixTrie[str]:
    substance_trie: SuffixTrie[str] = SuffixTrie()

    for substance_name, details in substance_data.items():
        pretty_name = details.get('pretty_name', 'Unknown')
        aliases = details.get('aliases', [])

        substance_trie.insert(substance_name, substance_name)
        substance_trie.insert(pretty_name, substance_name)
        for alias in aliases:
            substance_trie.insert(alias, substance_name)

    return substance_trie


def _init_category_card_names(substance_data: Dict) -> List[str]:
    categories: Set[str] = set()
    for substance in substance_data.values():
        for category in substance.get('categories', []):
            if category.lower() not in ['inactive', 'tentative', 'habit-forming', 'common', 'ssri']:
                categories.add(category.capitalize())
    return sorted(categories)


def _init_slug_to_substance_name_map(substance_data: Dict) -> Dict[str, str]:
    map: Dict[str, str] = {}
    for substance_name in substance_data.keys():
        slug = slugify(substance_name)
        assert slug not in map, f'Two substance names map to the same slug[\"{slug}\"]: {substance_name} and {map.get(slug)}'

        map[slug] = substance_name

    return map


SUBSTANCE_DATA = _init_substance_data()
SVG_FILES = _init_svg_file_names()
SUBSTANCE_TRIE = _init_substance_trie(SUBSTANCE_DATA)
CATEGORY_CARD_NAMES = _init_category_card_names(SUBSTANCE_DATA)
SLUG_TO_SUBSTANCE_NAME = _init_slug_to_substance_name_map(SUBSTANCE_DATA)
