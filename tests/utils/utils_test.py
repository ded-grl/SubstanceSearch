from src.utils import validate_slug, slugify


class TestUtilsClass:
    def test_validate_slug_success(self):
        slug = "VALID-SLUG"
        is_slug_valid, _ = validate_slug(slug)
        assert is_slug_valid

    def test_validate_slug_length(self):
        slug = 'INVALID-SLUG-LENGTH' * 100
        is_slug_valid, error_message = validate_slug(slug)
        assert not is_slug_valid
        assert error_message == "Invalid slug length"

    def test_validate_slug_format(self):
        slug = 'INVALID%SLUG%FORMAT'
        is_slug_valid, error_message = validate_slug(slug)
        assert not is_slug_valid
        assert error_message == "Invalid slug format"

    def test_slugify_success(self):
        unormalized_str = '  SLUG! SLUG! SLUG!  '
        expected_slug = 'slug-slug-slug'

        assert expected_slug == slugify(unormalized_str)

    def test_slugify_failed_validation(self):
        unormalized_str = '-slug-'
        expected_slug = ''

        assert expected_slug == slugify(unormalized_str)

    def test_slugify_encoding(self):
        unormalized_str = 'α-pbp'
        expected_slug = 'a-pbp'

        assert expected_slug == slugify(unormalized_str)
