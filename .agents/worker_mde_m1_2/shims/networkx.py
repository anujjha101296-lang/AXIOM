"""
Comprehensive networkx shim for testing environment when networkx is not installed.
"""

def simple_cycles(G):
    cycles = []
    visited = set()
    stack = []
    stack_set = set()

    def dfs(node):
        visited.add(node)
        stack.append(node)
        stack_set.add(node)

        for neighbor in G._adj.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in stack_set:
                idx = stack.index(neighbor)
                cycle = stack[idx:]
                cycles.append(cycle)

        stack.pop()
        stack_set.remove(node)

    for n in list(G._nodes):
        if n not in visited:
            dfs(n)

    return cycles

class EdgesView:
    def __init__(self, edges_dict):
        self._edges_dict = edges_dict

    def __getitem__(self, key):
        return self._edges_dict[key]

    def __call__(self, data=False):
        if data:
            return [(u, v, attr) for (u, v), attr in self._edges_dict.items()]
        return list(self._edges_dict.keys())

    def __iter__(self):
        return iter(self._edges_dict.keys())

    def __len__(self):
        return len(self._edges_dict)

class DiGraph:
    def __init__(self, incoming_graph_data=None, **attr):
        self._nodes = {}
        self._edges = {}
        self._adj = {}
        if incoming_graph_data is not None:
            if isinstance(incoming_graph_data, list):
                for edge in incoming_graph_data:
                    u, v = edge[0], edge[1]
                    d = edge[2] if len(edge) > 2 else {}
                    self.add_edge(u, v, **d)

    def add_node(self, node_id, **kwargs):
        self._nodes[node_id] = kwargs
        if node_id not in self._adj:
            self._adj[node_id] = {}

    def add_edge(self, u, v, **kwargs):
        self.add_node(u)
        self.add_node(v)
        self._edges[(u, v)] = kwargs
        self._adj[u][v] = kwargs

    def has_node(self, n):
        return n in self._nodes

    def has_edge(self, u, v):
        return (u, v) in self._edges

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return EdgesView(self._edges)

    def out_degree(self):
        result = []
        for n in self._nodes:
            count = len(self._adj.get(n, {}))
            result.append((n, count))
        return result
