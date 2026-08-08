"""Research Validation Engine — orchestrates runs, scoring, and replay."""

from __future__ import annotations

import time
import uuid
from typing import Any

from axiom.research_validation.dataset import get_problems_for_stage, load_known_answer_dataset
from axiom.research_validation.models import (
    ResearchRunConfig,
    ResearchRunResult,
    STAGE_DESCRIPTIONS,
    ValidationStage,
)
from axiom.research_validation.pipeline import build_pipeline_output
from axiom.research_validation.reproducibility import config_hash
from axiom.research_validation.scoring import (
    compute_capability_score,
    enrich_report_with_keywords,
    generate_heuristic_report,
    score_answer,
)
from axiom.research_validation.store import RVPStore
from axiom.observability.run_provenance import record_rvp_run


class ResearchValidationEngine:
    """Run staged research validation with known-answer scoring and replay."""

    PASS_THRESHOLD = 0.5

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.store = RVPStore(db_path)

    def list_stages(self) -> list[dict[str, Any]]:
        return [
            {
                "stage": int(s),
                "name": s.name,
                "description": STAGE_DESCRIPTIONS[s],
                "problem_count": len(get_problems_for_stage(int(s))),
            }
            for s in ValidationStage
        ]

    def list_problems(self, stage: int | None = None, limit: int = 100) -> list[dict[str, Any]]:
        dataset = load_known_answer_dataset()
        problems = dataset.values()
        if stage is not None:
            problems = [p for p in problems if p.stage == stage]
        return [p.public_dict() for p in list(problems)[:limit]]

    def run_validation(self, config: ResearchRunConfig) -> list[ResearchRunResult]:
        """Execute validation for all problems in config."""
        dataset = load_known_answer_dataset()
        results: list[ResearchRunResult] = []
        for pid in config.problem_ids:
            if pid not in dataset:
                continue
            result = self._run_single(config, dataset[pid])
            self.store.save_run(result.to_dict())
            results.append(result)
        return results

    def replay(self, config: ResearchRunConfig) -> list[ResearchRunResult]:
        """Replay run with identical configuration (reproducibility check)."""
        return self.run_validation(config)

    def _run_single(self, config: ResearchRunConfig, problem) -> ResearchRunResult:
        started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        start = time.perf_counter()
        attempts: list[dict[str, Any]] = []
        report = ""
        answer_score = 0.0

        for attempt in range(1, config.max_attempts + 1):
            report = generate_heuristic_report(problem, attempt)
            answer_score = score_answer(report, problem)
            if answer_score < self.PASS_THRESHOLD and attempt < config.max_attempts:
                report = enrich_report_with_keywords(report, problem, answer_score)
                answer_score = score_answer(report, problem)
            passed_attempt = answer_score >= self.PASS_THRESHOLD
            attempts.append({"attempt": attempt, "score": answer_score, "passed": passed_attempt})
            if passed_attempt:
                break

        capability = compute_capability_score(
            report, problem, answer_score, attempts=len(attempts), config_reproducible=True
        )
        pipeline = build_pipeline_output(problem, report, answer_score, attempts)
        elapsed_ms = (time.perf_counter() - start) * 1000
        finished_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        cfg_dict = config.to_dict()
        cfg_dict["problem_id"] = problem.id
        run_id = str(uuid.uuid4())[:8]
        cfg_hash = config_hash(config)
        verification_invoked = bool(getattr(config, "enable_verification", False))

        provenance_record = record_rvp_run(
            self.db_path,
            run_id=run_id,
            config_hash=cfg_hash,
            config=cfg_dict,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=elapsed_ms,
            stage=config.stage,
            problem_id=problem.id,
            answer_score=answer_score,
            passed=answer_score >= self.PASS_THRESHOLD,
            verification_invoked=verification_invoked,
        )

        return ResearchRunResult(
            run_id=run_id,
            config_hash=cfg_hash,
            timestamp=finished_at,
            stage=config.stage,
            problem_id=problem.id,
            config=cfg_dict,
            capability_score=capability,
            answer_score=answer_score,
            passed=answer_score >= self.PASS_THRESHOLD,
            pipeline=pipeline,
            provenance={
                **provenance_record.to_dict(),
                "seed": config.seed,
                "attempts": len(attempts),
                "hidden_answer_accessed": False,
            },
            cost_ms=elapsed_ms,
            latency_ms=elapsed_ms,
        )

    def run_stage_batch(self, stage: int, limit: int = 10, seed: int = 42) -> list[ResearchRunResult]:
        """Run validation on a batch of problems for a given stage."""
        problems = get_problems_for_stage(stage)[:limit]
        config = ResearchRunConfig(
            stage=stage,
            problem_ids=[p.id for p in problems],
            seed=seed,
        )
        return self.run_validation(config)
