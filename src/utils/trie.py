from typing import Dict, Generic, List, TypeVar

_DataType = TypeVar("_DataType")


class _SuffixTrieNodeMetadatum:
    """
    Metadata for what data a suffix trie node points to
    and which search suffix it points to
    """

    def __init__(self, data_store_index: int = -1, suffix_index: int = -1) -> None:
        if data_store_index < 0:
            raise AssertionError("data_store_index must be non-negative")
        if suffix_index < 0:
            raise AssertionError("suffix_index must be non-negative")

        self.data_store_index: int = data_store_index
        self.suffix_index: int = suffix_index


class _SuffixTrieNode:
    def __init__(self) -> None:
        self.children: Dict[str, _SuffixTrieNode] = {}
        self.is_end: bool = False
        self.metadata: List[_SuffixTrieNodeMetadatum] = []


class SuffixTrie(Generic[_DataType]):
    def __init__(self) -> None:
        self.root: _SuffixTrieNode = _SuffixTrieNode()
        self.data_store: List[_DataType] = []

    def insert(self, word: str, data: _DataType) -> None:
        try:
            # check to see if the data is already in the store
            data_store_index: int = self.data_store.index(data)
        except ValueError:
            # if data is not in the store, add it
            data_store_index: int = len(self.data_store)
            self.data_store.append(data)

        # insert for all suffixes (including the empty string)
        for suffix_index in range(len(word) + 1):
            self._insert_suffix(word[suffix_index:], suffix_index, data_store_index)

    def _insert_suffix(
        self, suffix: str, suffix_index: int, data_store_index: int
    ) -> None:
        node: _SuffixTrieNode = self.root
        for char in suffix.lower():
            if char not in node.children:
                node.children[char] = _SuffixTrieNode()
            node = node.children[char]
        node.is_end = True

        suffix_node_metadatum = _SuffixTrieNodeMetadatum(data_store_index, suffix_index)
        node.metadata.append(suffix_node_metadatum)

    def search_substring(self, substring: str) -> List[_DataType]:
        node: _SuffixTrieNode = self.root
        data_store_indices: List[int] = []

        for char in substring.lower():
            if char not in node.children:
                return []
            node = node.children[char]

        self._collect_words(node, substring, data_store_indices)
        results = [
            self.data_store[data_store_index]
            for data_store_index in set(data_store_indices)
        ]

        return results

    def _collect_words(
        self, node: _SuffixTrieNode, substring: str, data_store_indices: List[int]
    ) -> None:
        if node.is_end:
            data_store_indices.extend(
                [metadatum.data_store_index for metadatum in node.metadata]
            )

        for char, child in node.children.items():
            self._collect_words(child, substring + char, data_store_indices)
