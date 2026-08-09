"""Research role definitions and assignment (FRCE §6)."""

from __future__ import annotations

from axiom.campaign.models import FrontierCampaign, ResearchRole


ROLE_DESCRIPTIONS: dict[ResearchRole, str] = {
    ResearchRole.PRINCIPAL_INVESTIGATOR: "Owns the research objective and final decisions",
    ResearchRole.LITERATURE_RESEARCHER: "Maps existing work and known results",
    ResearchRole.MATHEMATICIAN: "Develops mathematical approaches and lemmas",
    ResearchRole.COMPUTATIONAL_RESEARCHER: "Runs sandboxed experiments via SEC",
    ResearchRole.FORMALIZATION_SPECIALIST: "Translates mathematics into proof assistants via FMTP",
    ResearchRole.COUNTEREXAMPLE_HUNTER: "Attempts to destroy hypotheses",
    ResearchRole.SKEPTICAL_REVIEWER: "Looks for hidden assumptions and weak evidence",
    ResearchRole.INDEPENDENT_REPLICATOR: "Reproduces results without original reasoning",
    ResearchRole.RESEARCH_STRATEGIST: "Decides which direction deserves resources",
    ResearchRole.RESEARCH_ARCHIVIST: "Maintains provenance and research memory",
}


DEFAULT_ROLE_ASSIGNMENTS: dict[str, list[ResearchRole]] = {
    "literature": [ResearchRole.LITERATURE_RESEARCHER],
    "experiment": [ResearchRole.COMPUTATIONAL_RESEARCHER, ResearchRole.INDEPENDENT_REPLICATOR],
    "formal": [ResearchRole.FORMALIZATION_SPECIALIST, ResearchRole.SKEPTICAL_REVIEWER],
    "counterexample": [ResearchRole.COUNTEREXAMPLE_HUNTER],
    "strategy": [ResearchRole.RESEARCH_STRATEGIST, ResearchRole.PRINCIPAL_INVESTIGATOR],
    "archive": [ResearchRole.RESEARCH_ARCHIVIST],
}


def list_roles() -> list[dict]:
    return [
        {"role": role.value, "description": desc}
        for role, desc in ROLE_DESCRIPTIONS.items()
    ]


def assign_roles_for_cycle(campaign: FrontierCampaign, investigation_type: str) -> list[ResearchRole]:
    """Return roles needed for a given investigation track."""
    base = [ResearchRole.PRINCIPAL_INVESTIGATOR, ResearchRole.RESEARCH_ARCHIVIST]
    track_roles = DEFAULT_ROLE_ASSIGNMENTS.get(investigation_type, [])
    return list(dict.fromkeys(base + track_roles))


def max_parallel_workers(campaign: FrontierCampaign, *, max_workers: int = 5) -> int:
    """Controlled parallelism — never unbounded (FRCE §7)."""
    remaining_compute = campaign.budget.compute_units - campaign.budget.consumed.get("compute_units", 0)
    if remaining_compute <= 0:
        return 0
    active_strategies = [s for s in campaign.strategies if s.status == "active"]
    return min(max_workers, len(active_strategies) or 1, max(1, int(remaining_compute // 10)))
