import unicodedata
import re


def validate_slug(slug: str) -> (bool, str):
    """
    Validates a slug against length and format.
    If invalid, returns False and an error message.
    Otherwise, returns True.
    """

    # Validate slug length
    if not slug or len(slug) > 100:
        return False, "Invalid slug length"

    # Validate slug format
    if not re.match(r'^[a-zA-Z0-9-]+$', slug):
        return False, "Invalid slug format"

    return True, ""


def slugify(value: object) -> str:
    """
    Converts an object to a URL-friendly slug.
    Only allows alphanumeric characters and single hyphens.
    """
    value = str(value)
    value = unicodedata.normalize('NFKD', value)
    value = value.encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)

    # Additional validation to prevent empty or malicious slugs
    if not value or value.startswith('-') or value.endswith('-'):
        return ''

    return value


def clean_data(data):
    """
    Recursively clean the data to remove None or undefined values.
    """
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [clean_data(v) for v in data if v is not None]
    return data
