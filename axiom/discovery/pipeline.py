"""Discovery Pipeline for Phase 12.

Coordinates candidate generation, symbolic & SMT verification, and delta logging.
"""
import json, time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from axiom.discovery.generator import ConjectureGenerator
from axiom.discovery.prover import AutomatedProver
from axiom.discovery.models import DiscoveryResult, FormulaType


class DiscoveryPipeline:
    """End-to-end pipeline for mathematical discovery and verification."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.generator = ConjectureGenerator()
        self.prover = AutomatedProver()
        self.output_dir = output_dir or (Path(__file__).parent.parent.parent / "evaluation_results" / "phase12")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_discovery_cycle(self) -> Dict[str, Any]:
        """Execute a full autonomous discovery cycle."""
        results: List[DiscoveryResult] = []

        # 1. Summation Series Candidates
        sum_candidates = self.generator.generate_summation_candidates()
        for cand in sum_candidates:
            res = self.prover.prove_summation(cand)
            results.append(res)

        # 2. Inequality Candidates
        ineq_candidates = self.generator.generate_inequality_candidates()
        for cand in ineq_candidates:
            res = self.prover.verify_inequality_smt(cand)
            results.append(res)

        # Summary statistics
        proved_count = sum(1 for r in results if r.status == "PROVED")
        disproved_count = sum(1 for r in results if r.status == "DISPROVED")
        total_count = len(results)

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_candidates": total_count,
            "proved": proved_count,
            "disproved": disproved_count,
            "results": [r.model_dump() for r in results],
        }

        # Persist report
        out_file = self.output_dir / f"discovery_run_{int(time.time())}.json"
        out_file.write_text(json.dumps(report, indent=2))

        return report
