"""Grand Challenge Program — campaign management engine."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from axiom.evaluation.benchmarks.suite import (
    MATH_REASONING_CASES,
    run_math_reasoning_benchmarks,
    run_proof_verification_benchmarks,
)
from axiom.evaluation.frameworks.capability import CapabilitySnapshot, make_dimension_score, CapabilityDimension
from axiom.grand_challenge.gates import evaluate_gate
from axiom.grand_challenge.journal import generate_campaign_journal
from axiom.grand_challenge.models import (
    Campaign,
    CampaignCheckpoint,
    CampaignStatus,
    ChallengeTier,
    EvidenceRecord,
    EvidenceTier,
    ExperimentRecord,
    ExperimentStatus,
    HypothesisRecord,
    JournalEntry,
)
from axiom.grand_challenge.registry import get_challenge, list_challenges
from axiom.grand_challenge.store import CampaignStore
from axiom.workflow.checkpoints import get_checkpoint_store


# Map benchmark refs to SCEP runners
_BENCHMARK_RUNNERS: dict[str, Any] = {
    "mathematical_reasoning": run_math_reasoning_benchmarks,
    "proof_verification": run_proof_verification_benchmarks,
}

# Map challenge benchmark refs to SCEP case IDs
_CASE_INDEX: dict[str, dict] = {
    case["id"]: case for case in MATH_REASONING_CASES
}


class GrandChallengeEngine:
    """
    Manages long-term scientific campaigns across challenge tiers.
    Does not solve prize problems — manages campaigns, evidence, and gates.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.store = CampaignStore(db_path)
        self._checkpoint_store = get_checkpoint_store(db_path)

    def create_campaign(
        self,
        name: str,
        description: str = "",
        tier: ChallengeTier = ChallengeTier.TIER_0_TOY,
        challenge_ids: list[str] | None = None,
    ) -> Campaign:
        if challenge_ids is None:
            challenge_ids = [c.challenge_id for c in list_challenges(tier)]
        campaign = Campaign(
            name=name,
            description=description,
            current_tier=tier,
            target_tier=ChallengeTier(min(int(tier) + 1, 5)),
            challenge_ids=challenge_ids,
            status=CampaignStatus.DRAFT,
        )
        self.store.save(campaign)
        return campaign

    def get_campaign(self, campaign_id: str) -> Campaign | None:
        return self.store.get(campaign_id)

    def activate_campaign(self, campaign_id: str) -> Campaign:
        campaign = self._load(campaign_id)
        campaign.status = CampaignStatus.ACTIVE
        campaign.updated_at = datetime.now(timezone.utc)
        self.store.save(campaign)
        return campaign

    def add_hypothesis(self, campaign_id: str, statement: str, confidence: float = 0.5) -> Campaign:
        campaign = self._load(campaign_id)
        campaign.hypotheses.append(HypothesisRecord(statement=statement, confidence=confidence))
        campaign.updated_at = datetime.now(timezone.utc)
        self.store.save(campaign)
        return campaign

    def add_journal_entry(
        self,
        campaign_id: str,
        title: str,
        content: str,
        phase: str = "observation",
        experiment_id: str | None = None,
    ) -> Campaign:
        campaign = self._load(campaign_id)
        campaign.journal.append(JournalEntry(
            title=title, content=content, phase=phase, experiment_id=experiment_id,
        ))
        campaign.updated_at = datetime.now(timezone.utc)
        self.store.save(campaign)
        return campaign

    def run_experiment(self, campaign_id: str, challenge_id: str) -> Campaign:
        """Execute a challenge experiment using available SCEP benchmarks."""
        campaign = self._load(campaign_id)
        challenge = get_challenge(challenge_id)

        experiment = ExperimentRecord(
            challenge_id=challenge_id,
            title=challenge.title,
            status=ExperimentStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )
        campaign.experiments.append(experiment)

        results = self._execute_challenge(challenge)
        experiment.outputs = results
        experiment.score = results.get("score", 0.0)
        experiment.passed = results.get("passed", False)
        experiment.evidence_tier = EvidenceTier(results.get("evidence_tier", "unavailable"))
        experiment.status = ExperimentStatus.COMPLETED if experiment.passed else ExperimentStatus.FAILED
        experiment.completed_at = datetime.now(timezone.utc)
        experiment.notes = results.get("notes", "")

        # Collect evidence
        campaign.evidence.append(EvidenceRecord(
            source=f"experiment:{experiment.experiment_id}",
            evidence_type="benchmark_result",
            content=f"{challenge.title}: score={experiment.score}, passed={experiment.passed}",
            evidence_tier=experiment.evidence_tier,
            experiment_id=experiment.experiment_id,
            metadata=results,
        ))

        if experiment.passed and challenge_id not in campaign.challenges_completed:
            campaign.challenges_completed.append(challenge_id)

        campaign.updated_at = datetime.now(timezone.utc)
        self.store.save(campaign)
        return campaign

    def checkpoint(self, campaign_id: str) -> Campaign:
        """Save campaign checkpoint for long-running execution recovery."""
        campaign = self._load(campaign_id)
        cp = CampaignCheckpoint(
            tier=campaign.current_tier,
            challenges_completed=list(campaign.challenges_completed),
            experiments_completed=len([e for e in campaign.experiments if e.status == ExperimentStatus.COMPLETED]),
            evidence_count=len(campaign.evidence),
            context_snapshot={
                "status": campaign.status.value,
                "hypothesis_count": len(campaign.hypotheses),
                "journal_count": len(campaign.journal),
            },
        )
        campaign.checkpoints.append(cp)
        campaign.status = CampaignStatus.CHECKPOINTED
        campaign.updated_at = datetime.now(timezone.utc)
        self.store.save(campaign)
        return campaign

    def evaluate_readiness(
        self,
        campaign_id: str,
        capability_snapshot: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        campaign = self._load(campaign_id)
        if capability_snapshot is None:
            capability_snapshot = self._build_capability_snapshot()
        evaluation = evaluate_gate(campaign, capability_snapshot)
        return {
            "campaign_id": campaign_id,
            "current_tier": int(campaign.current_tier),
            "target_tier": int(campaign.target_tier),
            "passed": evaluation.passed,
            "checks": evaluation.checks,
            "blockers": evaluation.blockers,
            "warnings": evaluation.warnings,
        }

    def advance_tier(
        self,
        campaign_id: str,
        capability_snapshot: dict[str, Any] | None = None,
        human_approved: bool = False,
    ) -> Campaign:
        campaign = self._load(campaign_id)
        if human_approved:
            campaign.context.setdefault("human_approval", {})[
                str(int(campaign.target_tier))
            ] = True

        readiness = self.evaluate_readiness(campaign_id, capability_snapshot)
        if not readiness["passed"]:
            blockers = "; ".join(readiness["blockers"])
            raise ValueError(f"Readiness gate not passed: {blockers}")

        next_tier = ChallengeTier(min(int(campaign.current_tier) + 1, 5))
        campaign.current_tier = next_tier
        campaign.target_tier = ChallengeTier(min(int(next_tier) + 1, 5))
        campaign.status = CampaignStatus.ACTIVE

        # Add default challenges for new tier if not already present
        new_challenges = [c.challenge_id for c in list_challenges(next_tier)]
        for cid in new_challenges:
            if cid not in campaign.challenge_ids:
                campaign.challenge_ids.append(cid)

        campaign.updated_at = datetime.now(timezone.utc)
        self.store.save(campaign)
        return campaign

    def get_journal(self, campaign_id: str) -> str:
        campaign = self._load(campaign_id)
        return generate_campaign_journal(campaign)

    def run_tier_batch(self, campaign_id: str, tier: ChallengeTier | None = None) -> Campaign:
        """Run all challenges in a tier sequentially."""
        campaign = self._load(campaign_id)
        target = tier or campaign.current_tier
        tier_challenges = [c for c in campaign.challenge_ids if c.startswith(f"t{int(target)}_")]

        for challenge_id in tier_challenges:
            if challenge_id not in campaign.challenges_completed:
                campaign = self.run_experiment(campaign_id, challenge_id)

        campaign.status = CampaignStatus.ACTIVE
        campaign.updated_at = datetime.now(timezone.utc)
        self.store.save(campaign)
        return campaign

    def _execute_challenge(self, challenge) -> dict[str, Any]:
        """Run SCEP benchmarks referenced by a challenge."""
        refs = challenge.benchmark_refs
        if not refs:
            return {
                "score": 0.0,
                "passed": False,
                "evidence_tier": challenge.evidence_tier.value,
                "notes": "No benchmark refs; manual review required",
            }

        # Run math reasoning benchmarks for mr_* refs
        mr_refs = [r for r in refs if r.startswith("mr_")]
        if mr_refs:
            all_results, overall_score = run_math_reasoning_benchmarks()
            case_results = {r.case_id: r for r in all_results}
            scores = []
            for ref in mr_refs:
                if ref in case_results:
                    scores.append(case_results[ref].score)
            avg = sum(scores) / len(scores) if scores else 0.0
            return {
                "score": round(avg, 4),
                "passed": avg >= 1.0,
                "evidence_tier": "measured",
                "notes": f"Math reasoning: {len(scores)}/{len(mr_refs)} cases scored",
                "case_scores": {ref: case_results[ref].score for ref in mr_refs if ref in case_results},
            }

        # Run proof verification for pv_* refs
        pv_refs = [r for r in refs if r.startswith("pv_")]
        if pv_refs:
            all_results, overall_score = run_proof_verification_benchmarks()
            case_results = {r.case_id: r for r in all_results}
            scores = [case_results[r].score for r in pv_refs if r in case_results]
            avg = sum(scores) / len(scores) if scores else 0.0
            threshold = 2 / 3  # per challenge success criteria
            return {
                "score": round(avg, 4),
                "passed": avg >= threshold,
                "evidence_tier": "simulated",
                "notes": f"Proof verification: {sum(1 for s in scores if s >= 1.0)}/{len(pv_refs)} passed (simulated if compilers absent)",
                "case_scores": {ref: case_results[ref].score for ref in pv_refs if ref in case_results},
            }

        return {
            "score": 0.0,
            "passed": False,
            "evidence_tier": challenge.evidence_tier.value,
            "notes": f"Benchmark refs {refs} require manual or workflow execution",
        }

    def _build_capability_snapshot(self) -> dict[str, Any]:
        """Build a lightweight capability snapshot from SCEP benchmarks."""
        mr_results, mr_score = run_math_reasoning_benchmarks()
        pv_results, pv_score = run_proof_verification_benchmarks()

        snapshot = CapabilitySnapshot(
            run_id="gcp_snapshot",
            timestamp=datetime.now(timezone.utc).isoformat(),
            dimension_scores=[
                make_dimension_score(CapabilityDimension.MATHEMATICAL_REASONING, mr_score, len(mr_results)),
                make_dimension_score(CapabilityDimension.PROOF_VERIFICATION, pv_score, len(pv_results), estimated=pv_score < 0.5),
            ],
        )
        snapshot.compute_composite()
        return snapshot.to_dict()

    def _load(self, campaign_id: str) -> Campaign:
        campaign = self.store.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign not found: {campaign_id}")
        return campaign
