class _TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.data = None


class Trie:
    def __init__(self):
        self.root = _TrieNode()

    def insert(self, word, data):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = _TrieNode()
            node = node.children[char]
        node.is_end = True
        node.data = data

    def search_prefix(self, prefix, limit=10):
        node = self.root
        results = []

        for char in prefix.lower():
            if char not in node.children:
                return results
            node = node.children[char]

        self._collect_words(node, prefix, results)
        return results[:limit]

    def get(self, word):
        result = self.search_prefix(word, limit=1)

        if (len(result) == 0):
            return None

        return result[0]

    def _collect_words(self, node, prefix, results):
        if node.is_end:
            results.append(node.data)

        for char, child in node.children.items():
            self._collect_words(child, prefix + char, results)
