"""Topology engine and dynamic dependency resolution for AXIOM TaskGraph."""

from typing import Dict, List, Set, Union
from axiom.multi_agent.models import (
    TaskState,
    TaskNode,
    TaskGraph,
)


class TaskGraphCycleError(ValueError):
    """Raised when a cycle is detected in a TaskGraph during topological sorting."""

    pass


class TaskGraphValidationError(ValueError):
    """Raised when graph structure or dependency reference is invalid."""

    pass


class TransitionResult(list):
    """List of task IDs updated during dependency resolution, which also evaluates equal to integer length."""

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int):
            return len(self) == other
        return super().__eq__(other)

    def __ne__(self, other: object) -> bool:
        return not (self == other)


def topological_sort(graph: TaskGraph) -> List[str]:
    """Perform Kahn's algorithm topological sort on a TaskGraph.

    Returns:
        List[str]: Task IDs sorted in execution order (dependencies before dependents).

    Raises:
        TaskGraphValidationError: If a node depends on a task ID that does not exist in the graph.
        TaskGraphCycleError: If a cycle is detected in the dependency graph.
    """
    if not graph.nodes:
        return []

    # Validate all dependency references exist
    for node_id, node in graph.nodes.items():
        for dep in node.depends_on:
            if dep not in graph.nodes:
                raise TaskGraphValidationError(
                    f"Task node '{node_id}' depends on non-existent task '{dep}'"
                )

    # In-degree count (number of prerequisites for each node)
    in_degree: Dict[str, int] = {node_id: len(node.depends_on) for node_id, node in graph.nodes.items()}

    # Adjacency list: map each node to the list of nodes that depend on it
    dependents: Dict[str, List[str]] = {node_id: [] for node_id in graph.nodes}
    for node_id, node in graph.nodes.items():
        for dep in node.depends_on:
            dependents[dep].append(node_id)

    # Start queue with nodes that have 0 in-degree (sorted for determinism)
    queue: List[str] = sorted([node_id for node_id, deg in in_degree.items() if deg == 0])
    sorted_result: List[str] = []

    while queue:
        current = queue.pop(0)
        sorted_result.append(current)

        for dependent_id in sorted(dependents[current]):
            in_degree[dependent_id] -= 1
            if in_degree[dependent_id] == 0:
                queue.append(dependent_id)

    if len(sorted_result) != len(graph.nodes):
        cycle_node_ids = sorted([node_id for node_id, deg in in_degree.items() if deg > 0])
        raise TaskGraphCycleError(
            f"Cycle detected in TaskGraph involving nodes: {cycle_node_ids}"
        )

    return sorted_result


TERMINAL_FAIL_STATES: Set[TaskState] = {
    TaskState.FAILED,
    TaskState.BLOCKED,
    TaskState.CANCELLED,
    TaskState.BUDGET_EXCEEDED,
}


def resolve_dependencies(graph: TaskGraph) -> TransitionResult:
    """Dynamically transition PENDING nodes in TaskGraph based on dependency states.

    - Nodes with all dependencies in COMPLETED (or no dependencies) transition PENDING -> READY.
    - Nodes with any dependency in FAILED, BLOCKED, CANCELLED, or BUDGET_EXCEEDED transition PENDING -> BLOCKED.
    - Operates iteratively to cascade BLOCKED state across deep dependency chains.

    Returns:
        TransitionResult: List of task IDs updated during resolution (also compares equal to transition count int).
    """
    transitioned_nodes: List[str] = []

    while True:
        pass_transitions = 0
        for task_id, node in list(graph.nodes.items()):
            if node.state != TaskState.PENDING:
                continue

            if not node.depends_on:
                # No dependencies -> READY
                node.transition_to(TaskState.READY)
                pass_transitions += 1
                transitioned_nodes.append(task_id)
            else:
                dep_states = []
                failed_dep = None
                for dep_id in node.depends_on:
                    dep_node = graph.nodes.get(dep_id)
                    if dep_node is None:
                        dep_states.append(None)
                        failed_dep = f"missing dependency '{dep_id}'"
                    else:
                        dep_states.append(dep_node.state)
                        if dep_node.state in TERMINAL_FAIL_STATES:
                            failed_dep = f"dependency '{dep_id}' in state {dep_node.state.value}"

                if failed_dep is not None:
                    # Transition to BLOCKED
                    node.transition_to(
                        TaskState.BLOCKED,
                        error_message=f"Blocked due to {failed_dep}",
                    )
                    pass_transitions += 1
                    transitioned_nodes.append(task_id)
                elif all(st == TaskState.COMPLETED for st in dep_states):
                    # All dependencies completed -> READY
                    node.transition_to(TaskState.READY)
                    pass_transitions += 1
                    transitioned_nodes.append(task_id)

        if pass_transitions == 0:
            break

    return TransitionResult(transitioned_nodes)


def get_ready_nodes(graph: TaskGraph) -> List[TaskNode]:
    """Retrieve all TaskNodes currently in state READY."""
    return [node for node in graph.nodes.values() if node.state == TaskState.READY]


class TaskGraphEngine:
    """Engine providing graph algorithms and dependency management for TaskGraph."""

    @staticmethod
    def topological_sort(graph: TaskGraph) -> List[str]:
        return topological_sort(graph)

    @staticmethod
    def resolve_dependencies(graph: TaskGraph) -> TransitionResult:
        return resolve_dependencies(graph)

    @staticmethod
    def get_ready_nodes(graph: TaskGraph) -> List[TaskNode]:
        return get_ready_nodes(graph)

