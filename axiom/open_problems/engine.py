"""Open Problem Lab engine — orchestrates intake → map → decompose → strategies → tracks."""

from __future__ import annotations

from typing import Any

from axiom.campaign.models import LadderLevel
from axiom.campaign.orchestrator import FrontierCampaignEngine
from axiom.discovery.engine import DiscoveryEngine
from axiom.discovery.models import DiscoveryStatus
from axiom.open_problems.decompose import decompose_open_problem
from axiom.open_problems.intake import understand_problem
from axiom.open_problems.maps import (
    build_known_result_map,
    build_literature_map,
    known_results_by_bucket,
)
from axiom.open_problems.models import (
    OpenProblem,
    ResearchStatus,
    ResearchTrack,
    StageLevel,
    TimelineEvent,
    TrackKind,
    _new_id,
    _utc_now,
    can_transition,
)
from axiom.open_problems.strategies import generate_strategies, select_top_strategies
from axiom.open_problems.store import get_open_problem_store


class OpenProblemError(ValueError):
    pass


# Stage advancement requires evidence — Level 9 never auto.
_STAGE_REQUIREMENTS: dict[int, str] = {
    1: "Known-outcome conjecture handled with counterexample-first honesty",
    2: "Nontrivial known theorem formalization attempted",
    3: "Historical conjecture with known resolution reproduced",
    4: "Published result reproduction status recorded",
    5: "Small open problem campaign with persistent state",
    6: "Open subproblem of a major problem investigated",
    7: "Frontier problem — expert review required",
    8: "Major open problem — extraordinary evidence",
    9: "Millennium-level — blocked without Layer-1 human approval",
}


class OpenProblemLab:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.store = get_open_problem_store(db_path)
        self.frce = FrontierCampaignEngine(db_path)
        self.discovery = DiscoveryEngine(db_path)

    def create(
        self,
        title: str,
        informal_statement: str,
        *,
        domain: str = "mathematics",
        known_info: str = "",
        sources: list[str] | None = None,
        research_objective: str = "",
        constraints: list[str] | None = None,
        stage_level: int = 1,
        owner_id: str | None = None,
        formal_statement: str = "",
    ) -> OpenProblem:
        if stage_level >= StageLevel.L9_MILLENNIUM.value:
            raise OpenProblemError(
                "Level 9 Millennium campaigns require explicit human Layer-1 approval "
                "and are not auto-started by the Open Problem Lab."
            )
        problem = OpenProblem(
            problem_id=_new_id("op"),
            title=title.strip() or informal_statement[:80],
            domain=domain,
            informal_statement=informal_statement.strip(),
            formal_statement=formal_statement,
            research_objective=research_objective or informal_statement.strip()[:200],
            constraints=constraints or [],
            stage_level=max(1, min(8, stage_level)),
            owner_id=owner_id,
            origin="researcher",
        )
        problem.understanding = understand_problem(
            informal_statement, known_info=known_info
        )
        seed = "\n".join([known_info, *(sources or [])])
        problem.known_results = build_known_result_map(problem, seed)
        problem.literature = build_literature_map(problem, seed)
        problem.research_gaps = [
            "External literature coverage incomplete",
            "Formal library search incomplete",
        ]
        self._event(problem, "SOURCE_FOUND", "Intake seed / known_info recorded")
        self._event(problem, "KNOWLEDGE_EXTRACTED", "Problem understanding parsed")
        return self.store.save(problem)

    def transition(
        self,
        problem_id: str,
        to_status: ResearchStatus,
        *,
        reason: str,
        allow_resolved: bool = False,
    ) -> OpenProblem:
        p = self._load(problem_id)
        if to_status == ResearchStatus.RESOLVED and not allow_resolved:
            raise OpenProblemError(
                "RESOLVED requires allow_resolved=True with independent verification evidence"
            )
        if not can_transition(p.research_status, to_status):
            raise OpenProblemError(
                f"Illegal status transition {p.research_status.value} → {to_status.value}"
            )
        if p.research_status == ResearchStatus.REFUTED and to_status != ResearchStatus.REFUTED:
            raise OpenProblemError("REFUTED problems cannot be casually resurrected")
        p.research_status = to_status
        self._event(p, "RESEARCH_DIRECTION_CHANGED", reason)
        return self.store.save(p)

    def map_knowledge(self, problem_id: str) -> OpenProblem:
        p = self._load(problem_id)
        # Refresh maps from existing understanding (idempotent enrichment)
        if not p.known_results:
            p.known_results = build_known_result_map(p)
        if not p.literature:
            p.literature = build_literature_map(p)
        buckets = known_results_by_bucket(p.known_results)
        self._event(
            p,
            "GAP_IDENTIFIED",
            f"Known-result buckets populated; unknown={len(buckets.get('WHAT_IS_UNKNOWN', []))}",
        )
        if p.research_status == ResearchStatus.UNKNOWN:
            p.research_status = ResearchStatus.MAPPED
        return self.store.save(p)

    def decompose(self, problem_id: str) -> OpenProblem:
        p = self._load(problem_id)
        p.subproblems = decompose_open_problem(p)
        self._event(p, "GAP_IDENTIFIED", f"Decomposed into {len(p.subproblems)} subproblems")
        return self.store.save(p)

    def generate_strategies(self, problem_id: str) -> OpenProblem:
        p = self._load(problem_id)
        p.strategies = generate_strategies(p)
        # Independent tracks — one per top strategy kind
        p.tracks = []
        for s in select_top_strategies(p.strategies, k=5):
            p.tracks.append(
                ResearchTrack(
                    track_id=_new_id("trk"),
                    kind=s.kind,
                    strategy_id=s.strategy_id,
                    independent_state={"strategy_name": s.name, "rank": s.rank_score},
                )
            )
        self._event(p, "STRATEGY_STARTED", f"Generated {len(p.strategies)} strategies / {len(p.tracks)} tracks")
        if p.research_status in {ResearchStatus.UNKNOWN, ResearchStatus.MAPPED}:
            p.research_status = ResearchStatus.UNDER_INVESTIGATION
        return self.store.save(p)

    def start_campaign(self, problem_id: str) -> OpenProblem:
        p = self._load(problem_id)
        if not p.strategies:
            p = self.generate_strategies(problem_id)
            p = self._load(problem_id)

        ladder = {
            1: LadderLevel.LEVEL_1_KNOWN_ANSWER_MATH,
            2: LadderLevel.LEVEL_2_FORMAL_REPRODUCTION,
            3: LadderLevel.LEVEL_3_PUBLISHED_REPRODUCTION,
            4: LadderLevel.LEVEL_4_RESEARCH_BENCHMARK,
            5: LadderLevel.LEVEL_5_SMALL_OPEN,
            6: LadderLevel.LEVEL_6_OPEN_SUBPROBLEM,
            7: LadderLevel.LEVEL_7_MAJOR_OPEN,
            8: LadderLevel.LEVEL_8_FRONTIER,
        }.get(p.stage_level, LadderLevel.LEVEL_1_KNOWN_ANSWER_MATH)

        campaign = self.frce.create_campaign(
            name=f"OPL: {p.title[:60]}",
            objective=p.research_objective or p.informal_statement[:200],
            problem_definition=p.informal_statement,
            domain=p.domain,
            ladder_level=ladder,
            success_criteria=[
                "Produce evidence-backed research report",
                "Attempt counterexample-first where conjectural",
                "Never claim RESOLVED without verification gate",
            ],
            constraints=p.constraints
            + ["No Millennium attempt", "Computational evidence is not proof"],
            owner_id=p.owner_id,
            link_gcp=False,
        )
        loaded = self.frce.get_campaign(campaign.campaign_id)
        if loaded is not None and isinstance(getattr(loaded, "context", None), dict):
            loaded.context["open_problem_id"] = p.problem_id
            self.frce.store.save(loaded, archive_previous=False)

        p.campaign_ids.append(campaign.campaign_id)
        self._event(p, "STRATEGY_STARTED", f"FRCE campaign {campaign.campaign_id} created")
        return self.store.save(p)

    def start_discovery(self, problem_id: str, *, seed_text: str = "") -> OpenProblem:
        p = self._load(problem_id)
        seed = seed_text or "\n".join(e.title + ": " + " ".join(e.claims) for e in p.literature[:2])
        d = self.discovery.create(
            p.informal_statement,
            knowledge_context=seed,
            seed_text=seed,
            campaign_id=p.campaign_ids[0] if p.campaign_ids else None,
            owner_id=p.owner_id,
        )
        p.discovery_ids.append(d.discovery_id)
        self._event(p, "HYPOTHESIS_CREATED", f"Discovery investigation {d.discovery_id}")
        return self.store.save(p)

    def run_investigation_cycle(self, problem_id: str) -> dict[str, Any]:
        """Run one OPL cycle: ensure maps/strategies, FRCE scope/plan/cycle, discovery cycle, synthesize."""
        p = self._load(problem_id)
        stages: list[str] = []

        if p.research_status == ResearchStatus.UNKNOWN:
            p = self.map_knowledge(problem_id)
            stages.append("map_knowledge")
        if not p.subproblems:
            p = self.decompose(problem_id)
            stages.append("decompose")
        if not p.strategies:
            p = self.generate_strategies(problem_id)
            stages.append("strategies")
        if not p.campaign_ids:
            p = self.start_campaign(problem_id)
            stages.append("start_campaign")
        if not p.discovery_ids:
            p = self.start_discovery(problem_id)
            stages.append("start_discovery")

        p = self._load(problem_id)

        # FRCE: scope → plan → cycle (best-effort)
        frce_out: dict[str, Any] = {}
        camp_id = p.campaign_ids[-1]
        try:
            camp = self.frce.get_campaign(camp_id)
            if camp and camp.phase.value == "PROPOSED":
                self.frce.scope(camp_id)
                stages.append("frce_scope")
            camp = self.frce.get_campaign(camp_id)
            if camp and not getattr(camp, "strategies", None):
                self.frce.plan(camp_id)
                stages.append("frce_plan")
            frce_out = self.frce.run_cycle(camp_id)
            stages.append("frce_cycle")
            self._event(p, "EXPERIMENT_COMPLETED", f"FRCE cycle on {camp_id}")
        except Exception as exc:  # noqa: BLE001
            frce_out = {"error": str(exc)[:300]}
            self._event(p, "STRATEGY_ABANDONED", f"FRCE cycle error: {exc}"[:200])

        # Discovery cycle (counterexample-first integrated)
        disc_out: dict[str, Any] = {}
        disc_id = p.discovery_ids[-1]
        try:
            disc_out = self.discovery.run_cycle(disc_id)
            stages.append("discovery_cycle")
            final = self.discovery.store.get(disc_id)
            if final:
                p.experiment_ids.extend(final.experiment_ids)
                p.counterexample_ids.extend(final.counterexample_ids)
                p.proof_attempt_ids.extend(final.proof_attempt_ids)
                if final.status == DiscoveryStatus.REFUTED:
                    self._event(p, "COUNTEREXAMPLE_FOUND", "Discovery marked REFUTED")
                    if p.research_status not in {ResearchStatus.REFUTED, ResearchStatus.RESOLVED}:
                        p.research_status = ResearchStatus.REFUTED
                        p.verification_state = "REFUTED_BY_COUNTEREXAMPLE"
                        p.stopping_reasons.append("Counterexample track succeeded")
                elif final.status == DiscoveryStatus.SUPPORTED:
                    self._event(p, "EXPERIMENT_COMPLETED", "Discovery pilot supported (computational only)")
                    if p.research_status == ResearchStatus.UNDER_INVESTIGATION:
                        p.research_status = ResearchStatus.PARTIALLY_PROGRESSING
        except Exception as exc:  # noqa: BLE001
            disc_out = {"error": str(exc)[:300]}

        # Per-track independent notes (no cross-contamination of conclusions)
        for tr in p.tracks:
            if not tr.active:
                continue
            if tr.kind == TrackKind.COUNTEREXAMPLE and p.counterexample_ids:
                tr.findings.append(f"Counterexample artifacts: {p.counterexample_ids[-1:]}")
            elif tr.kind == TrackKind.COMPUTATIONAL and p.experiment_ids:
                tr.findings.append(f"Experiments: {p.experiment_ids[-1:]}")
            elif tr.kind == TrackKind.FORMAL and p.proof_attempt_ids:
                tr.findings.append(f"Formal attempts: {p.proof_attempt_ids[-1:]}")
            elif tr.kind == TrackKind.LITERATURE:
                tr.findings.append(f"Literature entries: {len(p.literature)}")
            else:
                tr.findings.append("Analytical track awaiting deeper lemma work")

        p.report = self._synthesize_report(p, frce_out, disc_out)
        self.store.save(p)
        return {
            "problem_id": p.problem_id,
            "research_status": p.research_status.value,
            "stage_level": p.stage_level,
            "stages_executed": stages,
            "campaign_ids": p.campaign_ids,
            "discovery_ids": p.discovery_ids,
            "report": p.report,
            "is_millennium_attempt": False,
            "is_scientific_discovery_claim": False,
        }

    def abandon_strategy(self, problem_id: str, strategy_id: str, reason: str) -> OpenProblem:
        p = self._load(problem_id)
        for s in p.strategies:
            if s.strategy_id == strategy_id:
                s.abandoned = True
                s.abandon_reason = reason
        for t in p.tracks:
            if t.strategy_id == strategy_id:
                t.active = False
                t.failures.append(reason)
        self._event(p, "STRATEGY_ABANDONED", reason)
        p.stopping_reasons.append(reason)
        return self.store.save(p)

    def compare_tracks(self, problem_id: str) -> dict[str, Any]:
        p = self._load(problem_id)
        return {
            "problem_id": p.problem_id,
            "tracks": [t.to_dict() for t in p.tracks],
            "agreement": "Tracks remain independent; compare findings without merging conclusions",
            "disagreement": [
                t.kind.value for t in p.tracks if t.failures and t.findings
            ],
        }

    def stage_manifest(self) -> dict[str, Any]:
        return {
            "levels": {k: v for k, v in _STAGE_REQUIREMENTS.items()},
            "millennium_auto_start": False,
            "note": "Advance only with measured evidence — not model confidence",
        }

    def _synthesize_report(
        self, p: OpenProblem, frce_out: dict[str, Any], disc_out: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "title": p.title,
            "informal_statement": p.informal_statement,
            "research_status": p.research_status.value,
            "stage_level": p.stage_level,
            "understanding": p.understanding.to_dict(),
            "known_results_by_bucket": known_results_by_bucket(p.known_results),
            "literature_count": len(p.literature),
            "subproblems": [s.to_dict() for s in p.subproblems[:8]],
            "strategies": [s.to_dict() for s in p.strategies],
            "tracks": [t.to_dict() for t in p.tracks],
            "campaign_ids": p.campaign_ids,
            "discovery_ids": p.discovery_ids,
            "frce": frce_out if not frce_out.get("error") else {"error": frce_out["error"]},
            "discovery": {
                "status": disc_out.get("status"),
                "stages": disc_out.get("stages_executed"),
                "is_scientific_discovery_claim": False,
            },
            "timeline_tail": [e.to_dict() for e in p.timeline[-12:]],
            "stopping_reasons": p.stopping_reasons,
            "limitations": [
                "Computational evidence is not proof.",
                "Missing literature retrieval is not novelty.",
                "RESOLVED requires explicit verification gate.",
                "Millennium campaigns are not auto-started.",
            ],
            "language": "conservative",
            "is_millennium_attempt": False,
            "is_scientific_discovery_claim": False,
            "recommended_next_action": _next_action(p),
        }

    def _event(self, p: OpenProblem, event_type: str, detail: str) -> None:
        p.timeline.append(
            TimelineEvent(event_id=_new_id("ev"), event_type=event_type, detail=detail)
        )

    def _load(self, problem_id: str) -> OpenProblem:
        p = self.store.get(problem_id)
        if not p:
            raise OpenProblemError(f"Open problem not found: {problem_id}")
        return p


def _next_action(p: OpenProblem) -> str:
    if p.research_status == ResearchStatus.REFUTED:
        return "Verify counterexample independently; archive REFUTED; do not resurrect."
    if p.research_status == ResearchStatus.BLOCKED:
        return "Record blocker; consider alternate strategy or human expertise."
    if not p.subproblems:
        return "Decompose into subproblems."
    if not p.campaign_ids:
        return "Start FRCE campaign."
    return "Continue highest-ranked active track; prefer counterexample-first for conjectures."
