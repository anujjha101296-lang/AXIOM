"""Research graph operations (FRCE §5)."""

from __future__ import annotations

from axiom.campaign.models import (
    FrontierCampaign,
    GraphNodeStatus,
    GraphNodeType,
    ResearchGraphNode,
    ResearchRole,
    _new_id,
)


def add_graph_node(
    campaign: FrontierCampaign,
    *,
    node_type: GraphNodeType,
    title: str,
    dependencies: list[str] | None = None,
    owner_role: ResearchRole | None = None,
    next_action: str = "",
    metadata: dict | None = None,
) -> ResearchGraphNode:
    node = ResearchGraphNode(
        node_id=_new_id("node"),
        node_type=node_type,
        title=title,
        status=GraphNodeStatus.OPEN,
        dependencies=dependencies or [],
        owner_role=owner_role,
        next_action=next_action,
        metadata=metadata or {},
    )
    campaign.research_graph.append(node)
    return node


def decompose_problem(campaign: FrontierCampaign) -> list[ResearchGraphNode]:
    """Decompose grand problem into subproblems and candidate lemmas (FRCE §4)."""
    if campaign.research_graph:
        return campaign.research_graph

    main = add_graph_node(
        campaign,
        node_type=GraphNodeType.MAIN_PROBLEM,
        title=campaign.objective,
        owner_role=ResearchRole.PRINCIPAL_INVESTIGATOR,
        next_action="map known results and identify open space",
    )

    # Heuristic decomposition from problem definition
    parts = [
        p.strip()
        for p in campaign.problem_definition.replace(";", ".").split(".")
        if p.strip()
    ]
    if not parts:
        parts = ["Identify known results", "Identify open subproblems", "Formulate candidate lemmas"]

    sub_nodes: list[ResearchGraphNode] = []
    for i, part in enumerate(parts[:5]):
        role = ResearchRole.MATHEMATICIAN if i % 2 == 0 else ResearchRole.COMPUTATIONAL_RESEARCHER
        sub = add_graph_node(
            campaign,
            node_type=GraphNodeType.SUBPROBLEM if i < len(parts) - 1 else GraphNodeType.OPEN_QUESTION,
            title=part[:200],
            dependencies=[main.node_id],
            owner_role=role,
            next_action="investigate",
        )
        sub_nodes.append(sub)

    return [main, *sub_nodes]


def find_bottleneck(campaign: FrontierCampaign) -> ResearchGraphNode | None:
    """Identify the most constrained open node (lowest confidence, most dependents)."""
    open_nodes = [
        n for n in campaign.research_graph
        if n.status in (GraphNodeStatus.OPEN, GraphNodeStatus.IN_PROGRESS, GraphNodeStatus.UNKNOWN)
    ]
    if not open_nodes:
        return None

    dependent_counts: dict[str, int] = {n.node_id: 0 for n in campaign.research_graph}
    for node in campaign.research_graph:
        for dep in node.dependencies:
            if dep in dependent_counts:
                dependent_counts[dep] += 1

    return min(open_nodes, key=lambda n: (n.confidence, -dependent_counts.get(n.node_id, 0)))


def update_node_from_evidence(
    campaign: FrontierCampaign,
    node_id: str,
    *,
    evidence_id: str,
    supports: bool,
    confidence_delta: float = 0.1,
) -> ResearchGraphNode | None:
    for node in campaign.research_graph:
        if node.node_id != node_id:
            continue
        node.evidence_ids.append(evidence_id)
        if supports:
            node.confidence = min(1.0, node.confidence + confidence_delta)
            if node.confidence >= 0.8:
                node.status = GraphNodeStatus.SUPPORTED
        else:
            node.confidence = max(0.0, node.confidence - confidence_delta)
            if node.confidence <= 0.2:
                node.status = GraphNodeStatus.REFUTED
        return node
    return None


def graph_summary(campaign: FrontierCampaign) -> dict:
    by_status: dict[str, int] = {}
    by_type: dict[str, int] = {}
    for node in campaign.research_graph:
        by_status[node.status.value] = by_status.get(node.status.value, 0) + 1
        by_type[node.node_type.value] = by_type.get(node.node_type.value, 0) + 1
    bottleneck = find_bottleneck(campaign)
    return {
        "node_count": len(campaign.research_graph),
        "by_status": by_status,
        "by_type": by_type,
        "bottleneck_node_id": bottleneck.node_id if bottleneck else None,
        "bottleneck_title": bottleneck.title if bottleneck else None,
    }
