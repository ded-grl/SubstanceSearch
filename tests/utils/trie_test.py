import pytest
from src.utils.trie import SuffixTrie


class TestTrieClass:
    @pytest.fixture()
    def trie(self) -> SuffixTrie:
        test_trie = SuffixTrie()
        test_trie.insert('key1', 'value1')
        test_trie.insert('key12', 'value12')
        test_trie.insert('key1-dupe', 'value1')
        test_trie.insert('key2', 'value2')

        yield test_trie

    def test_trie_substring_search(self, trie):
        results = trie.search_substring('key1')

        assert len(results) == 2
        assert set(['value1', 'value12']) == set(results)
