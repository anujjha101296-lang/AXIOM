"""
Minimal networkx shim for testing when networkx is not installed in environment.
"""

class DiGraph:
    def __init__(self):
        self._nodes = {}
        self._edges = {}

    def add_node(self, node_id, **kwargs):
        self._nodes[node_id] = kwargs

    def add_edge(self, u, v, **kwargs):
        self._edges[(u, v)] = kwargs

    def has_node(self, n):
        return n in self._nodes

    def has_edge(self, u, v):
        return (u, v) in self._edges

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges
