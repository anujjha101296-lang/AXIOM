"""Frontier Research Campaign Engine (FRCE) — connects all AXIOM research loops."""

from axiom.campaign.allocator import allocate_resources, consume_budget, where_next_compute
from axiom.campaign.gates import pending_gates, resolve_gate, should_trigger_gate
from axiom.campaign.graph import (
    decompose_problem,
    find_bottleneck,
    graph_summary,
    update_node_from_evidence,
)
from axiom.campaign.ladder import can_advance_ladder, ladder_manifest
from axiom.campaign.memory import compound_to_global_memory, record_cycle_memory
from axiom.campaign.models import (
    CampaignPhase,
    ContributionLevel,
    FrontierCampaign,
    LadderLevel,
    PivotDecision,
    ResearchRole,
    ResourceBudget,
    can_transition,
)
from axiom.campaign.orchestrator import FrontierCampaignEngine
from axiom.campaign.planner import generate_strategies, plan_hypotheses, scope_campaign
from axiom.campaign.pivot import apply_pivot, evaluate_cycle
from axiom.campaign.roles import list_roles, max_parallel_workers
from axiom.campaign.store import CampaignEngineStore, get_campaign_store

__all__ = [
    "CampaignEngineStore",
    "CampaignPhase",
    "ContributionLevel",
    "FrontierCampaign",
    "FrontierCampaignEngine",
    "LadderLevel",
    "PivotDecision",
    "ResearchRole",
    "ResourceBudget",
    "allocate_resources",
    "apply_pivot",
    "can_advance_ladder",
    "can_transition",
    "compound_to_global_memory",
    "decompose_problem",
    "evaluate_cycle",
    "find_bottleneck",
    "generate_strategies",
    "get_campaign_store",
    "graph_summary",
    "ladder_manifest",
    "list_roles",
    "max_parallel_workers",
    "pending_gates",
    "record_cycle_memory",
    "resolve_gate",
    "scope_campaign",
    "should_trigger_gate",
    "where_next_compute",
]
