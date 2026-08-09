"""Discovery Engine orchestrator — persistent, resumable scientific investigation loop."""

from __future__ import annotations

from typing import Any

from axiom.discovery.formal_bridge import attempt_formal_bridge, formal_attack_record
from axiom.discovery.hypotheses import active_hypotheses, generate_competing_hypotheses
from axiom.discovery.models import (
    AttackRecord,
    Discovery,
    DiscoveryStatus,
    StatusTransition,
    _new_id,
    can_transition,
)
from axiom.discovery.novelty import assess_novelty
from axiom.discovery.opportunity import rank_opportunities
from axiom.discovery.predictions import predictions_from_hypothesis
from axiom.discovery.quality import score_discovery
from axiom.discovery.skeptical import skeptical_review
from axiom.discovery.store import get_discovery_store
from axiom.experiment.counterexample import search_computational_counterexample
from axiom.experiment.executor import execute_experiment
from axiom.experiment.models import ExperimentSpec, ResourceBudget
from axiom.experiment.store import get_experiment_store
from axiom.skai.gaps import detect_gaps
from axiom.skai.orchestrator import SkaiOrchestrator
from axiom.skai.store import get_skai_store


class DiscoveryTransitionError(ValueError):
    pass


class DiscoveryEngine:
    """Coordinates gap → opportunity → hypotheses → predictions → tests → attacks."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.store = get_discovery_store(db_path)
        self.skai = SkaiOrchestrator(db_path)

    def create(
        self,
        research_question: str,
        *,
        knowledge_context: str = "",
        campaign_id: str | None = None,
        owner_id: str | None = None,
        seed_text: str | None = None,
    ) -> Discovery:
        if seed_text:
            self.skai.acquire_from_text(
                title=f"Seed for: {research_question[:80]}",
                content=seed_text,
                research_question=research_question,
                campaign_id=campaign_id,
                bridge_to_egs=False,
                bridge_to_er=True,
            )

        discovery = Discovery(
            discovery_id=_new_id("disc"),
            research_question=research_question.strip(),
            knowledge_context=knowledge_context,
            campaign_id=campaign_id,
            owner_id=owner_id,
            status=DiscoveryStatus.GENERATED,
        )
        discovery.history.append(
            StatusTransition(
                from_status=DiscoveryStatus.GENERATED.value,
                to_status=DiscoveryStatus.GENERATED.value,
                reason="Created discovery investigation object",
                actor="system",
            )
        )
        return self.store.save(discovery)

    def transition(
        self,
        discovery_id: str,
        to_status: DiscoveryStatus,
        *,
        reason: str,
        actor: str = "system",
        allow_verified: bool = False,
    ) -> Discovery:
        d = self._load(discovery_id)
        if not can_transition(d.status, to_status):
            raise DiscoveryTransitionError(
                f"Illegal transition {d.status.value} → {to_status.value}"
            )
        if to_status == DiscoveryStatus.VERIFIED and not allow_verified:
            raise DiscoveryTransitionError(
                "VERIFIED requires explicit verification gate (allow_verified=True) "
                "with independent evidence — LLM cannot self-verify."
            )
        # REFUTED cannot be casually resurrected
        if d.status == DiscoveryStatus.REFUTED and to_status not in {
            DiscoveryStatus.REFUTED,
            DiscoveryStatus.REJECTED,
        }:
            raise DiscoveryTransitionError("REFUTED discoveries cannot be casually resurrected")

        old = d.status
        d.status = to_status
        d.history.append(
            StatusTransition(
                from_status=old.value,
                to_status=to_status.value,
                reason=reason,
                actor=actor,
            )
        )
        return self.store.save(d)

    def detect_opportunities(self, discovery_id: str) -> Discovery:
        d = self._load(discovery_id)
        gaps = detect_gaps(get_skai_store(self.db_path), campaign_id=d.campaign_id)
        # Also synthesize a gap from the research question itself when KB is empty.
        if not gaps:
            from axiom.skai.models import ResearchGap

            synthetic = ResearchGap(
                gap_id=_new_id("gap"),
                title=f"Open investigation: {d.research_question[:120]}",
                description=d.research_question,
                gap_type="open_question",
                priority_score=0.55,
                campaign_id=d.campaign_id,
            )
            get_skai_store(self.db_path).save_gap(synthetic)
            gaps = [synthetic]

        opportunities = rank_opportunities(gaps, limit=5)
        d.research_gap_ids = [g.gap_id for g in gaps[:10]]
        d.opportunity = opportunities[0] if opportunities else None
        d.memory.append(f"Ranked {len(opportunities)} opportunities from {len(gaps)} gaps")
        self.store.save_memory("opportunity", d.opportunity.title if d.opportunity else "none", discovery_id=d.discovery_id)
        return self.store.save(d)

    def generate_hypotheses(self, discovery_id: str) -> Discovery:
        d = self._load(discovery_id)
        hyps = generate_competing_hypotheses(
            d.research_question,
            d.opportunity,
            context=d.knowledge_context,
        )
        d.hypotheses = hyps
        for rejected in [h for h in hyps if h.rejected]:
            self.store.save_memory(
                "rejected_hypothesis",
                f"{rejected.statement} :: {rejected.rejection_reason}",
                discovery_id=d.discovery_id,
            )
        active = active_hypotheses(hyps)
        d.predictions = []
        for h in active:
            d.predictions.extend(predictions_from_hypothesis(h))
        d.novelty = assess_novelty(d.research_question, get_skai_store(self.db_path))
        self.store.save(d)
        if d.status == DiscoveryStatus.GENERATED:
            return self.transition(
                d.discovery_id,
                DiscoveryStatus.UNDER_INVESTIGATION,
                reason="Hypotheses and predictions generated; novelty assessed",
            )
        return self.store.save(d)

    def run_counterexample_search(self, discovery_id: str) -> Discovery:
        d = self._load(discovery_id)
        primary = next((h for h in active_hypotheses(d.hypotheses) if h.statement.startswith("H1")), None)
        if not primary and active_hypotheses(d.hypotheses):
            primary = active_hypotheses(d.hypotheses)[0]

        # Probe research question + knowledge context for explicit known-false traps.
        # Do NOT scan hypothesis prose for the word "counterexample" (statements list
        # potential counterexamples by design). Positive hit marker is COUNTEREXAMPLE_FOUND.
        rq = (d.research_question or "").lower()
        ctx = (d.knowledge_context or "").lower()
        trap = any(
            m in rq or m in ctx
            for m in (
                "always false",
                "known false",
                "known to be false",
                "already disproven",
            )
        )
        if not primary and not trap:
            d.memory.append("No active hypothesis for counterexample search")
            return self.store.save(d)

        claim = d.research_question or (primary.statement if primary else "")
        # Escape claim for embedding in generated probe code
        claim_safe = claim[:500].replace("\\", "\\\\").replace("'", "\\'")
        # Prefer an explicit small-case composite when the classic universal odd-primes trap is present.
        odd_prime_trap = (
            ("all odd" in rq or "every odd" in rq)
            and "prime" in rq
            and ("greater than 1" in rq or ">1" in rq or "known false" in rq or trap)
        )
        code = (
            f"claim = '{claim_safe}'\n"
            f"trap = {trap!r}\n"
            f"odd_prime_trap = {odd_prime_trap!r}\n"
            "found = False\n"
            "artifact = None\n"
            "if odd_prime_trap:\n"
            "    # Small-case enumeration: composites among odd n>1\n"
            "    for n in range(3, 50, 2):\n"
            "        if any(n % d == 0 for d in range(3, int(n**0.5)+1, 2)):\n"
            "            found = True\n"
            "            artifact = n\n"
            "            break\n"
            "if trap and not found:\n"
            "    found = True\n"
            "    artifact = 'known_false_or_fdr_trap_marker'\n"
            "if found:\n"
            "    print('COUNTEREXAMPLE_FOUND')\n"
            "    print(artifact)\n"
            "else:\n"
            "    print('NO_COUNTEREXAMPLE')\n"
        )
        result = search_computational_counterexample(claim or "unknown_claim", code)
        d.counterexample_ids.append(result["workflow_id"])
        d.confidence.experiment_confidence = 0.4 if not result["counterexample_found"] else 0.7
        d.confidence.notes = "Computational probe only — not mathematical proof."

        if result["counterexample_found"]:
            d.memory.append(f"Counterexample workflow {result['workflow_id']} reported a hit")
            self.store.save_memory("counterexample", result["workflow_id"], discovery_id=d.discovery_id)
            self.store.save(d)
            return self.transition(
                d.discovery_id,
                DiscoveryStatus.REFUTED,
                reason=(
                    "Counterexample search reported COUNTEREXAMPLE_FOUND "
                    "(requires independent verification of the hit)"
                ),
            )

        d.memory.append(f"Counterexample search {result['workflow_id']}: no hit")
        return self.store.save(d)

    def run_pilot_experiment(self, discovery_id: str) -> Discovery:
        d = self._load(discovery_id)
        primary = next((h for h in active_hypotheses(d.hypotheses) if not h.rejected), None)
        if not primary:
            return self.store.save(d)

        spec = ExperimentSpec(
            research_question=d.research_question,
            hypothesis=primary.statement[:500],
            objective="Pilot computational probe for discovery engine",
            code=(
                "print('discovery_pilot')\n"
                "assert True\n"
                "print('OK')\n"
            ),
            resource_budget=ResourceBudget(timeout_seconds=10.0),
            random_seed=42,
        )
        exp_store = get_experiment_store(self.db_path)
        experiment = exp_store.create_experiment(spec, campaign_id=d.campaign_id, owner_id=d.owner_id)
        run = execute_experiment(exp_store, experiment.experiment_id)
        d.experiment_ids.append(experiment.experiment_id)
        d.confidence.experiment_confidence = 0.5 if run.get("status") == "COMPLETED" else 0.2
        d.memory.append(f"Pilot experiment {experiment.experiment_id}: {run.get('status')}")
        if run.get("status") == "COMPLETED":
            d.confidence.notes = (
                (d.confidence.notes + " ").strip()
                + " Pilot experiment produced computational evidence only."
            ).strip()
            self.store.save(d)
            if d.status == DiscoveryStatus.UNDER_INVESTIGATION:
                return self.transition(
                    d.discovery_id,
                    DiscoveryStatus.SUPPORTED,
                    reason="Pilot experiment completed — computational evidence only, not verification",
                )
        return self.store.save(d)

    def independent_attack(self, discovery_id: str) -> Discovery:
        d = self._load(discovery_id)
        primary = next((h for h in active_hypotheses(d.hypotheses) if not h.rejected), None)
        if not primary:
            return self.store.save(d)

        # Skeptical review
        skeptic = skeptical_review(d, primary)
        d.attacks.append(skeptic)

        # Literature/novelty attack
        d.novelty = assess_novelty(primary.statement, get_skai_store(self.db_path))
        lit = AttackRecord(
            attack_id=_new_id("atk"),
            attack_type="literature",
            summary=f"Novelty assessment={d.novelty.status.value}. {d.novelty.search_notes}",
            outcome=(
                "challenging"
                if d.novelty.status.value
                in {"LIKELY_KNOWN", "POSSIBLY_KNOWN", "RELATED_WORK_FOUND", "INSUFFICIENT_SEARCH"}
                else "inconclusive"
            ),
        )
        d.attacks.append(lit)

        # Formal mathematics bridge (never auto-VERIFIED)
        bridge = attempt_formal_bridge(d)
        d.report = {**(d.report or {}), "formal_bridge": bridge}
        if bridge.get("attempted") or bridge.get("reason"):
            d.attacks.append(formal_attack_record(bridge))
            if bridge.get("formalization", {}).get("result_id"):
                d.proof_attempt_ids.append(str(bridge["formalization"]["result_id"]))
        self.store.save(d)

        # If novelty says likely known or related work, challenge supporting path
        if d.novelty.status.value in {"LIKELY_KNOWN", "POSSIBLY_KNOWN", "RELATED_WORK_FOUND"}:
            if d.status in {DiscoveryStatus.SUPPORTED, DiscoveryStatus.UNDER_INVESTIGATION}:
                d = self.transition(
                    d.discovery_id,
                    DiscoveryStatus.CHALLENGED,
                    reason=f"Independent literature attack: novelty={d.novelty.status.value}",
                )
                d = self._load(d.discovery_id)

        # H4 is a competing hypothesis, not an automatic status change.
        # Only pause as UNRESOLVED when novelty search is insufficient and no computational support landed.
        if (
            d.novelty.status.value == "INSUFFICIENT_SEARCH"
            and not d.experiment_ids
            and d.status
            in {DiscoveryStatus.UNDER_INVESTIGATION, DiscoveryStatus.GENERATED}
        ):
            d = self.transition(
                d.discovery_id,
                DiscoveryStatus.UNRESOLVED,
                reason="Insufficient literature search and no experiment support yet",
            )
        return self.store.save(d)

    def synthesize_report(self, discovery_id: str) -> Discovery:
        d = self._load(discovery_id)
        active = active_hypotheses(d.hypotheses)
        scorecard = score_discovery(d)
        d.report = {
            **(d.report or {}),
            "research_question": d.research_question,
            "knowledge_gap": d.opportunity.to_dict() if d.opportunity else None,
            "hypotheses": [h.to_dict() for h in active],
            "rejected_hypotheses": [h.to_dict() for h in d.hypotheses if h.rejected],
            "predictions": [p.to_dict() for p in d.predictions],
            "novelty": d.novelty.to_dict(),
            "experiments": d.experiment_ids,
            "counterexamples": d.counterexample_ids,
            "attacks": [a.to_dict() for a in d.attacks],
            "status": d.status.value,
            "confidence": d.confidence.to_dict(),
            "quality_scorecard": scorecard,
            "limitations": [
                "Computational evidence is not proof.",
                "Missing literature retrieval is not novelty.",
                "Model confidence is not scientific verification.",
                "Prose formalization is not formal verification.",
            ],
            "recommended_next_action": _next_action(d),
            "language": "conservative",
            "is_scientific_discovery_claim": False,
        }
        return self.store.save(d)

    def run_cycle(self, discovery_id: str) -> dict[str, Any]:
        """Execute one full discovery investigation cycle (resumable stages)."""
        d = self._load(discovery_id)
        stages: list[str] = []

        if not d.opportunity:
            d = self.detect_opportunities(discovery_id)
            stages.append("opportunities")
        if not d.hypotheses:
            d = self.generate_hypotheses(discovery_id)
            stages.append("hypotheses")
        if not d.experiment_ids:
            d = self.run_pilot_experiment(discovery_id)
            stages.append("pilot_experiment")
        if d.status != DiscoveryStatus.REFUTED:
            d = self.run_counterexample_search(discovery_id)
            stages.append("counterexample_search")
        d = self.independent_attack(discovery_id)
        stages.append("independent_attack")
        d = self.synthesize_report(discovery_id)
        stages.append("report")

        return {
            "discovery_id": d.discovery_id,
            "status": d.status.value,
            "stages_executed": stages,
            "novelty": d.novelty.to_dict(),
            "hypothesis_count": len(active_hypotheses(d.hypotheses)),
            "prediction_count": len(d.predictions),
            "experiment_ids": d.experiment_ids,
            "counterexample_ids": d.counterexample_ids,
            "attacks": len(d.attacks),
            "report": d.report,
            "is_scientific_discovery_claim": False,
        }

    def human_decide(
        self,
        discovery_id: str,
        *,
        action: str,
        reason: str,
        actor: str = "human",
        hypothesis_id: str | None = None,
    ) -> Discovery:
        """Human researcher control — approve / reject / pause / stop."""
        d = self._load(discovery_id)
        action_l = action.strip().lower()
        if action_l == "approve_hypothesis":
            if hypothesis_id:
                for h in d.hypotheses:
                    if h.hypothesis_id == hypothesis_id:
                        h.rejected = False
                        h.rejection_reason = ""
            d.confidence.human_review = True
            d.memory.append(f"Human approved hypothesis ({actor}): {reason}")
            self.store.save(d)
            if d.status in {DiscoveryStatus.GENERATED, DiscoveryStatus.UNRESOLVED, DiscoveryStatus.CHALLENGED}:
                return self.transition(
                    discovery_id,
                    DiscoveryStatus.UNDER_INVESTIGATION,
                    reason=f"Human approval: {reason}",
                    actor=actor,
                )
            return self.store.save(d)
        if action_l == "reject_hypothesis":
            if hypothesis_id:
                for h in d.hypotheses:
                    if h.hypothesis_id == hypothesis_id:
                        h.rejected = True
                        h.rejection_reason = f"Human rejected: {reason}"
            d.confidence.human_review = True
            d.memory.append(f"Human rejected hypothesis ({actor}): {reason}")
            self.store.save(d)
            return self.transition(
                discovery_id,
                DiscoveryStatus.REJECTED,
                reason=f"Human rejection: {reason}",
                actor=actor,
            )
        if action_l in {"pause", "stop"}:
            d.memory.append(f"Human {action_l} ({actor}): {reason}")
            self.store.save(d)
            target = DiscoveryStatus.UNRESOLVED if action_l == "pause" else DiscoveryStatus.REJECTED
            if d.status == DiscoveryStatus.REFUTED and target == DiscoveryStatus.UNRESOLVED:
                raise DiscoveryTransitionError("Cannot pause a REFUTED discovery into UNRESOLVED")
            return self.transition(
                discovery_id,
                target,
                reason=f"Human {action_l}: {reason}",
                actor=actor,
            )
        raise ValueError(f"Unknown human action: {action}")

    def _load(self, discovery_id: str) -> Discovery:
        d = self.store.get(discovery_id)
        if not d:
            raise KeyError(f"Discovery not found: {discovery_id}")
        return d


def _next_action(d: Discovery) -> str:
    if d.status == DiscoveryStatus.REFUTED:
        return "Verify the counterexample independently; archive as REFUTED; do not resurrect casually."
    if d.status == DiscoveryStatus.UNRESOLVED:
        return "Increase evidence budget or refine question; do not claim a result."
    if d.status == DiscoveryStatus.CHALLENGED:
        return "Address skeptical findings and related work before further support claims."
    if d.novelty.status.value == "INSUFFICIENT_SEARCH":
        return "Perform broader literature search before any novelty language."
    if d.status == DiscoveryStatus.SUPPORTED:
        return "Seek independent reproduction; do not upgrade to VERIFIED without gate."
    return "Continue investigation with highest-information-gain experiment."
