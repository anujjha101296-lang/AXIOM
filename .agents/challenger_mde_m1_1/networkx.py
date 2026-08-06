"""
Lightweight NetworkX implementation for AXIOM graph data structures.
"""

class DiGraphNodeView(dict):
    def __call__(self, data=False):
        if not data:
            return list(self.keys())
        return list(self.items())

class DiGraphEdgeView(dict):
    def __call__(self, data=False):
        if not data:
            return list(self.keys())
        return [(u, v, d) for (u, v), d in self.items()]

    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            return super().__getitem__(key)
        raise KeyError(key)

class DiGraph:
    def __init__(self):
        self._node = {}
        self._adj = {}
        self._pred = {}

    @property
    def nodes(self):
        return DiGraphNodeView(self._node)

    @property
    def edges(self):
        return DiGraphEdgeView({
            (u, v): self._adj[u][v]
            for u in self._adj
            for v in self._adj[u]
        })

    def add_node(self, node_for_adding, **attr):
        if node_for_adding not in self._node:
            self._node[node_for_adding] = {}
            self._adj[node_for_adding] = {}
            self._pred[node_for_adding] = {}
        self._node[node_for_adding].update(attr)

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        u, v = u_of_edge, v_of_edge
        if u not in self._node:
            self.add_node(u)
        if v not in self._node:
            self.add_node(v)
        if v not in self._adj[u]:
            self._adj[u][v] = {}
        self._adj[u][v].update(attr)
        if u not in self._pred[v]:
            self._pred[v][u] = self._adj[u][v]

    def has_node(self, n):
        return n in self._node

    def has_edge(self, u, v):
        return u in self._adj and v in self._adj[u]

    def number_of_nodes(self):
        return len(self._node)

    def number_of_edges(self):
        return sum(len(neighbors) for neighbors in self._adj.values())

    def degree(self):
        return {n: len(self._adj[n]) + len(self._pred[n]) for n in self._node}

    def in_degree(self):
        return {n: len(self._pred[n]) for n in self._node}

    def out_degree(self):
        return {n: len(self._adj[n]) for n in self._node}

__all__ = ["DiGraph"]
