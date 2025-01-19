class _SuffixTrieNodeMetadatum:
    """
    Metadata for what data a suffix trie node points to
    and which search suffix it points to
    """

    def __init__(self, data_store_index=-1, suffix_index=-1):
        assert data_store_index >= 0
        assert suffix_index >= 0

        self.data_store_index = data_store_index
        self.suffix_index = suffix_index


class _SuffixTrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.metadata = []


class SuffixTrie:
    def __init__(self):
        self.root = _SuffixTrieNode()
        self.data_store = []

    def insert(self, word, data):
        try:
            # check to see if the data is already in the store
            data_store_index = self.data_store.index(data)
        except ValueError:
            # if data is not in the store, add it
            data_store_index = len(self.data_store)
            self.data_store.append(data)

        # insert for all suffixes (including the empty string)
        for suffix_index in range(len(word) + 1):
            self._insert_suffix(word[suffix_index:],
                                suffix_index, data_store_index)

    def _insert_suffix(self, suffix: str, suffix_index: int, data_store_index: int):
        node = self.root
        for char in suffix.lower():
            if char not in node.children:
                node.children[char] = _SuffixTrieNode()
            node = node.children[char]
        node.is_end = True

        suffix_node_metadatum = _SuffixTrieNodeMetadatum(
            data_store_index, suffix_index)
        node.metadata.append(suffix_node_metadatum)

    def search_substring(self, substring: str):
        node = self.root
        data_store_indices = []

        for char in substring.lower():
            if char not in node.children:
                return []
            node = node.children[char]

        self._collect_words(node, substring, data_store_indices)
        results = [self.data_store[data_store_index]
                   for data_store_index in set(data_store_indices)]

        return results

    def _collect_words(self, node, substring, data_store_indices):
        if node.is_end:
            data_store_indices.extend(
                [metadatum.data_store_index for metadatum in node.metadata])

        for char, child in node.children.items():
            self._collect_words(child, substring + char, data_store_indices)
