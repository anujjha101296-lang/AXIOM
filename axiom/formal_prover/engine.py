"""Unified Formal Verification Engine for Phase 14."""
import json, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from axiom.formal_prover.models import (
    FormalTheorem,
    FormalVerificationResult,
    ProverType,
    FormalStatus,
)
from axiom.formal_prover.lean4_bridge import Lean4Bridge
from axiom.formal_prover.coq_bridge import CoqBridge
from axiom.formal_prover.isabelle_bridge import IsabelleBridge


class FormalVerificationEngine:
    """Coordinates multi-prover formal verification across Lean 4, Coq, and Isabelle."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.lean4 = Lean4Bridge()
        self.coq = CoqBridge()
        self.isabelle = IsabelleBridge()
        self.output_dir = output_dir or (Path(__file__).parent.parent.parent / "evaluation_results" / "phase14")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def verify_theorem(
        self,
        theorem: FormalTheorem,
        tactic_script: str,
    ) -> FormalVerificationResult:
        """Route verification request to the target theorem prover bridge."""
        if theorem.prover == ProverType.LEAN4:
            res = self.lean4.verify_lean4_script(theorem, tactic_script)
        elif theorem.prover == ProverType.COQ:
            res = self.coq.verify_coq_script(theorem, tactic_script)
        elif theorem.prover == ProverType.ISABELLE:
            res = self.isabelle.verify_isabelle_script(theorem, tactic_script)
        else:
            t0 = time.time()
            res = FormalVerificationResult(
                theorem_name=theorem.name,
                prover=theorem.prover,
                status=FormalStatus.SYNTAX_ERROR,
                proof_code=tactic_script,
                error_message=f"Unsupported prover type: {theorem.prover}",
                verification_time_ms=round((time.time() - t0) * 1000.0, 3),
            )

        # Persist verification result
        out_file = self.output_dir / f"formal_verify_{int(time.time())}_{theorem.name}.json"
        out_file.write_text(json.dumps(res.model_dump(), indent=2))

        return res
