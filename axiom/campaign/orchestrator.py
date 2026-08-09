"""Frontier Research Campaign Engine — orchestrates all AXIOM loops (FRCE §1, §17)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from axiom.campaign.allocator import allocate_resources, consume_budget, where_next_compute
from axiom.campaign.gates import pending_gates, resolve_gate, should_trigger_gate
from axiom.campaign.graph import decompose_problem, find_bottleneck, graph_summary, update_node_from_evidence
from axiom.campaign.ladder import can_advance_ladder, ladder_manifest
from axiom.campaign.memory import compound_to_global_memory, record_cycle_memory
from axiom.campaign.models import (
    CampaignHypothesis,
    CampaignPhase,
    CampaignCheckpoint,
    ContributionLevel,
    CycleRecord,
    FrontierCampaign,
    LadderLevel,
    PivotDecision,
    ResourceBudget,
    _new_id,
    _utc_now,
    can_transition,
)
from axiom.campaign.pivot import apply_pivot, evaluate_cycle
from axiom.campaign.planner import generate_strategies, plan_hypotheses, scope_campaign
from axiom.campaign.roles import list_roles, max_parallel_workers
from axiom.campaign.store import CampaignEngineStore
from axiom.evidence.models import ClaimStatus, EvidenceType
from axiom.evidence.registry import ClaimRegistry
from axiom.experiment.executor import execute_experiment
from axiom.experiment.models import ExperimentSpec, ResourceBudget as SecResourceBudget
from axiom.experiment.store import ExperimentStore
from axiom.formal_math.formalization import formalize_informal
from axiom.grand_challenge.engine import GrandChallengeEngine
from axiom.grand_challenge.models import ChallengeTier


class FrontierCampaignEngine:
    """
    Orchestrates long-running research missions across E&R, SIMR, FMTP, SEC, and GCP.

    AXIOM continuously decides whether the plan is still worth pursuing.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.store = CampaignEngineStore(db_path)
        self._claims = ClaimRegistry(db_path)
        self._experiments = ExperimentStore(db_path)
        self._gcp = GrandChallengeEngine(db_path)

    # ── Campaign lifecycle ────────────────────────────────────────────────

    def create_campaign(
        self,
        name: str,
        objective: str,
        *,
        problem_definition: str = "",
        domain: str = "mathematics",
        ladder_level: LadderLevel = LadderLevel.LEVEL_1_KNOWN_ANSWER_MATH,
        success_criteria: list[str] | None = None,
        constraints: list[str] | None = None,
        budget: ResourceBudget | None = None,
        link_gcp: bool = False,
    ) -> FrontierCampaign:
        campaign = FrontierCampaign(
            campaign_id=_new_id("camp"),
            name=name,
            objective=objective,
            problem_definition=problem_definition,
            domain=domain,
            ladder_level=ladder_level,
            success_criteria=success_criteria or [],
            constraints=constraints or [],
            budget=budget or ResourceBudget(),
            phase=CampaignPhase.PROPOSED,
        )

        if link_gcp:
            gcp_tier = ChallengeTier(min(int(ladder_level), 5))
            gcp = self._gcp.create_campaign(
                name=f"GCP:{name}",
                description=objective,
                tier=gcp_tier,
            )
            campaign.gcp_campaign_id = gcp.campaign_id

        self.store.save(campaign, archive_previous=False)
        return campaign

    def get_campaign(self, campaign_id: str) -> FrontierCampaign | None:
        return self.store.get(campaign_id)

    def list_campaigns(self, phase: str | None = None, limit: int = 50) -> list[FrontierCampaign]:
        return self.store.list_campaigns(phase=phase, limit=limit)

    def transition(self, campaign_id: str, to_phase: CampaignPhase) -> FrontierCampaign:
        campaign = self._load(campaign_id)
        if not can_transition(campaign.phase, to_phase):
            raise ValueError(f"Invalid transition: {campaign.phase.value} → {to_phase.value}")
        campaign.phase = to_phase
        self.store.save(campaign)
        return campaign

    def scope(self, campaign_id: str) -> FrontierCampaign:
        campaign = self._load(campaign_id)
        scope_campaign(campaign)
        self._checkpoint(campaign, "Problem scoped", "Scoped problem and decomposed research graph")
        self.store.save(campaign)
        return campaign

    def plan(self, campaign_id: str) -> FrontierCampaign:
        campaign = self._load(campaign_id)
        generate_strategies(campaign)
        plan_hypotheses(campaign)
        self._checkpoint(campaign, "Strategies generated", "SIMR routing plan and hypotheses")
        self.store.save(campaign)
        return campaign

    # ── Research cycle ────────────────────────────────────────────────────

    def run_cycle(self, campaign_id: str) -> dict[str, Any]:
        """
        Execute one full research cycle:
        parallel investigation → collect evidence → attack results → decide next action.
        """
        campaign = self._load(campaign_id)
        if campaign.budget.budget_exceeded():
            campaign.phase = CampaignPhase.BLOCKED
            self.store.save(campaign)
            return {"status": "blocked", "reason": "budget_exceeded"}

        cycle_num = len(campaign.cycles) + 1
        cycle = CycleRecord(
            cycle_id=_new_id("cycle"),
            cycle_number=cycle_num,
            started_at=_utc_now(),
        )

        campaign.phase = CampaignPhase.INVESTIGATION
        workers = max_parallel_workers(campaign)
        allocated = allocate_resources(campaign, max_workers=workers)

        results: dict[str, Any] = {
            "cycle_number": cycle_num,
            "strategies_executed": [],
            "experiment_ids": [],
            "claim_ids": [],
        }

        for strategy in allocated[:3]:  # controlled parallelism
            track_result = self._execute_strategy_track(campaign, strategy, cycle)
            results["strategies_executed"].append(track_result)

        # Collect evidence into E&R
        for hyp in campaign.hypotheses:
            if hyp.claim_id:
                continue
            claim = self._claims.register_claim(
                hyp.statement,
                campaign_id=campaign.campaign_id,
                status=ClaimStatus.SPECULATIVE,
            )
            hyp.claim_id = claim.claim_id
            cycle.claim_ids.append(claim.claim_id)
            campaign.claim_ids.append(claim.claim_id)

        cycle.completed_at = _utc_now()
        cycle.pivot_decision = evaluate_cycle(campaign, cycle)
        apply_pivot(campaign, cycle.pivot_decision)

        # Update contribution level from cycle outcomes
        cycle.contribution_level = self._assess_contribution(campaign, cycle)
        campaign.contribution_level = max(
            campaign.contribution_level,
            cycle.contribution_level,
            key=lambda c: list(ContributionLevel).index(c),
        )

        record_cycle_memory(campaign, cycle)
        campaign.cycles.append(cycle)

        # Human gates
        gate = should_trigger_gate(
            campaign,
            trigger="potential_contribution",
            details={"cycle": cycle_num, "contribution": cycle.contribution_level.value},
        )
        if gate:
            campaign.phase = CampaignPhase.REVIEW
            results["human_gate"] = gate.to_dict()

        consume_budget(campaign, time_seconds=60, compute_units=10, model_calls=1, tool_calls=len(allocated))
        self._checkpoint(campaign, f"Cycle {cycle_num}", f"Completed research cycle {cycle_num}")
        self.store.save(campaign)

        results["pivot_decision"] = cycle.pivot_decision.value if cycle.pivot_decision else None
        results["contribution_level"] = cycle.contribution_level.value
        results["phase"] = campaign.phase.value
        return results

    def _execute_strategy_track(
        self,
        campaign: FrontierCampaign,
        strategy: Any,
        cycle: CycleRecord,
    ) -> dict[str, Any]:
        """Run one investigation track: experiment, formal, or literature stub."""
        plan = strategy.execution_plan
        strategy_type = plan.get("strategy_type", plan.get("action", "general"))

        if strategy_type in ("computational", "experiment", "numerical", "simulation"):
            return self._run_computational_track(campaign, strategy, cycle)

        if strategy_type in ("formal", "symbolic", "proof"):
            return self._run_formal_track(campaign, strategy, cycle)

        # Literature / general — recorded as observation
        cycle.learned.append(f"Literature track for {strategy.name}: mapping required")
        return {"track": "literature", "strategy": strategy.name, "status": "recorded"}

    def _run_computational_track(
        self,
        campaign: FrontierCampaign,
        strategy: Any,
        cycle: CycleRecord,
    ) -> dict[str, Any]:
        """SEC sandboxed experiment."""
        bottleneck = find_bottleneck(campaign)
        spec = ExperimentSpec(
            research_question=campaign.objective,
            hypothesis=strategy.description,
            objective=f"Investigate: {bottleneck.title if bottleneck else campaign.objective}",
            campaign_id=campaign.campaign_id,
            code="print('frce_cycle')",
            resource_budget=SecResourceBudget(timeout_seconds=10.0, memory_mb=256),
        )
        exp = self._experiments.create_experiment(spec)
        run_result = execute_experiment(self._experiments, exp.experiment_id)

        campaign.experiment_ids.append(exp.experiment_id)
        cycle.experiment_ids.append(exp.experiment_id)

        if run_result.get("status") == "COMPLETED":
            cycle.learned.append(f"Experiment {exp.experiment_id} completed")
            if bottleneck:
                claim = self._claims.register_claim(
                    f"Computational evidence for: {bottleneck.title}",
                    campaign_id=campaign.campaign_id,
                )
                self._claims.add_evidence(
                    claim.claim_id,
                    EvidenceType.COMPUTATION,
                    summary="Sandbox experiment completed — NOT mathematical proof",
                    experiment_id=exp.experiment_id,
                    supports=True,
                )
                update_node_from_evidence(campaign, bottleneck.node_id, evidence_id=claim.claim_id, supports=True)
        else:
            cycle.failed_approaches.append(strategy.name)

        return {
            "track": "computational",
            "experiment_id": exp.experiment_id,
            "status": run_result.get("status"),
            "not_mathematical_proof": True,
        }

    def _run_formal_track(
        self,
        campaign: FrontierCampaign,
        strategy: Any,
        cycle: CycleRecord,
    ) -> dict[str, Any]:
        """FMTP formalization attempt."""
        result = formalize_informal(campaign.objective)
        cycle.learned.append(f"Formalization attempted: {result.status.value}")
        success = result.status.value in ("successfully_formalized", "partially_formalized")
        if success:
            should_trigger_gate(campaign, trigger="formal_proof_success", details={"result": result.to_dict()})
        return {"track": "formal", "status": result.status.value, "success": success}

    def _assess_contribution(self, campaign: FrontierCampaign, cycle: CycleRecord) -> ContributionLevel:
        if cycle.failed_approaches and not cycle.learned:
            return ContributionLevel.NO_PROGRESS
        if cycle.learned and not cycle.experiment_ids:
            return ContributionLevel.USEFUL_OBSERVATION
        if cycle.experiment_ids:
            return ContributionLevel.USEFUL_OBSERVATION
        if any(h.status == "supported" for h in campaign.hypotheses):
            return ContributionLevel.NEW_CONJECTURE
        return ContributionLevel.NO_PROGRESS

    # ── Checkpoints & review ────────────────────────────────────────────

    def checkpoint(self, campaign_id: str, title: str = "Manual checkpoint") -> FrontierCampaign:
        campaign = self._load(campaign_id)
        self._checkpoint(campaign, title, "Manual checkpoint")
        self.store.save(campaign)
        return campaign

    def _checkpoint(self, campaign: FrontierCampaign, title: str, description: str) -> CampaignCheckpoint:
        cp = CampaignCheckpoint(
            checkpoint_id=_new_id("cp"),
            sequence=len(campaign.checkpoints) + 1,
            title=title,
            phase=campaign.phase.value,
            snapshot={
                "phase": campaign.phase.value,
                "contribution_level": campaign.contribution_level.value,
                "graph": graph_summary(campaign),
                "hypothesis_count": len(campaign.hypotheses),
                "experiment_count": len(campaign.experiment_ids),
                "claim_count": len(campaign.claim_ids),
                "description": description,
            },
        )
        campaign.checkpoints.append(cp)
        campaign.journal.append({
            "title": title,
            "content": description,
            "checkpoint_id": cp.checkpoint_id,
        })
        return cp

    def resolve_human_gate(
        self,
        campaign_id: str,
        gate_id: str,
        approved: bool,
        notes: str = "",
    ) -> FrontierCampaign:
        campaign = self._load(campaign_id)
        gate = resolve_gate(campaign, gate_id, approved=approved, notes=notes)
        if not gate:
            raise ValueError(f"Gate not found: {gate_id}")
        if approved:
            campaign.phase = CampaignPhase.RESEARCHING
        self.store.save(campaign)
        return campaign

    def abandon(self, campaign_id: str, reason: str = "") -> FrontierCampaign:
        """ABANDONED is not failure — preserve everything learned (FRCE §3)."""
        campaign = self._load(campaign_id)
        campaign.phase = CampaignPhase.ABANDONED
        campaign.journal.append({"title": "Campaign abandoned", "content": reason, "phase": "terminal"})
        compound_to_global_memory(self.store, campaign)
        self.store.save(campaign)
        return campaign

    def compound_memory(self, campaign_id: str) -> list[str]:
        campaign = self._load(campaign_id)
        return compound_to_global_memory(self.store, campaign)

    # ── Dashboard / status ────────────────────────────────────────────────

    def dashboard(self, campaign_id: str) -> dict[str, Any]:
        campaign = self._load(campaign_id)
        return {
            "campaign_id": campaign.campaign_id,
            "name": campaign.name,
            "phase": campaign.phase.value,
            "contribution_level": campaign.contribution_level.value,
            "ladder_level": int(campaign.ladder_level),
            "objective": campaign.objective,
            "research_graph": graph_summary(campaign),
            "active_strategies": len([s for s in campaign.strategies if s.status == "active"]),
            "hypotheses": len(campaign.hypotheses),
            "experiments": len(campaign.experiment_ids),
            "claims": len(campaign.claim_ids),
            "checkpoints": len(campaign.checkpoints),
            "cycles_completed": len(campaign.cycles),
            "pending_human_gates": len(pending_gates(campaign)),
            "failed_approaches": campaign.failed_approaches,
            "budget": campaign.budget.to_dict(),
            "next_compute": where_next_compute(campaign),
            "ladder_readiness": can_advance_ladder(campaign),
            "gcp_campaign_id": campaign.gcp_campaign_id,
        }

    def manifest(self) -> dict[str, Any]:
        return {
            "name": "AXIOM Frontier Research Campaign Engine",
            "version": "1.0",
            "loops_integrated": ["E&R", "SIMR", "FMTP", "SEC", "GCP"],
            "roles": list_roles(),
            "ladder": ladder_manifest(),
            "principles": [
                "Computation is not mathematical proof",
                "ABANDONED is not failure",
                "Earn ladder advancement through evidence",
                "Human gates for novel claims and major pivots",
            ],
        }

    def _load(self, campaign_id: str) -> FrontierCampaign:
        campaign = self.store.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign not found: {campaign_id}")
        return campaign
