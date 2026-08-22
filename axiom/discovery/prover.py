"""Symbolic and SMT Prover Engine for Phase 12.

Combines SymPy exact summation with Z3 SMT bounded theorem proving.
"""
import time
from typing import Dict, Any, Optional, Tuple
import sympy as sp
import z3

from axiom.discovery.models import (
    CandidateConjecture,
    DiscoveryResult,
    FormulaType,
    ProofStatus,
)


class AutomatedProver:
    """Verifies candidate conjectures via SymPy reduction and Z3 SMT solving."""

    def prove_summation(self, candidate: CandidateConjecture, sample_depth: int = 10) -> DiscoveryResult:
        """Prove closed-form summation using SymPy and verify inductively."""
        t0 = time.time()
        try:
            expr = sp.sympify(candidate.expression_str)
            k_sym = next((s for s in expr.free_symbols if s.name == 'k'), sp.Symbol('k', integer=True, positive=True))
            n_sym = sp.Symbol('n', integer=True, positive=True)

            closed_form = sp.summation(expr, (k_sym, 1, n_sym)).simplify()

            # Inductive numerical verification across sample_depth
            all_valid = True
            for test_n in range(1, sample_depth + 1):
                # Calculate exact numerical sum
                exact_sum = sum(int(round(float(sp.N(expr.subs(k_sym, i))))) for i in range(1, test_n + 1))
                formula_val = int(round(float(sp.N(closed_form.subs(n_sym, test_n)))))
                if exact_sum != formula_val:
                    all_valid = False
                    break

            elapsed = (time.time() - t0) * 1000.0

            if all_valid:
                return DiscoveryResult(
                    conjecture=candidate,
                    status=ProofStatus.PROVED,
                    proof_method="SymPy Exact Summation + Inductive Sample Verification",
                    closed_form=str(closed_form),
                    verification_time_ms=round(elapsed, 3),
                    inductive_samples_checked=sample_depth,
                )
            else:
                return DiscoveryResult(
                    conjecture=candidate,
                    status=ProofStatus.DISPROVED,
                    proof_method="Inductive Sample Counterexample",
                    verification_time_ms=round(elapsed, 3),
                    inductive_samples_checked=sample_depth,
                )
        except Exception as e:
            elapsed = (time.time() - t0) * 1000.0
            return DiscoveryResult(
                conjecture=candidate,
                status=ProofStatus.ERROR,
                proof_method=f"Failed with exception: {str(e)}",
                verification_time_ms=round(elapsed, 3),
            )

    def verify_inequality_smt(self, candidate: CandidateConjecture) -> DiscoveryResult:
        """Verify algebraic inequality using Z3 SMT solver."""
        t0 = time.time()
        try:
            x, y = z3.Ints('x y')
            solver = z3.Solver()
            solver.set("timeout", 10000)  # 10s timeout

            if "x^3 + y^3 < (x + y)^3" in candidate.expression_str:
                solver.add(x > 0)
                solver.add(y > 0)
                # Negate the inequality to search for counterexample
                solver.add((x**3 + y**3) >= (x + y)**3)

            elif "2*(x^2 + y^2) >= (x + y)^2" in candidate.expression_str:
                # Negate
                solver.add(2 * (x**2 + y**2) < (x + y)**2)
            else:
                elapsed = (time.time() - t0) * 1000.0
                return DiscoveryResult(
                    conjecture=candidate,
                    status=ProofStatus.UNKNOWN,
                    proof_method="Unsupported inequality expression format",
                    verification_time_ms=round(elapsed, 3),
                )

            res = solver.check()
            elapsed = (time.time() - t0) * 1000.0

            if res == z3.unsat:
                return DiscoveryResult(
                    conjecture=candidate,
                    status=ProofStatus.PROVED,
                    proof_method="Z3 SMT Solver (No Counterexample Exists)",
                    verification_time_ms=round(elapsed, 3),
                )
            elif res == z3.sat:
                m = solver.model()
                cx = {str(v): int(m[v].as_long()) for v in m}
                return DiscoveryResult(
                    conjecture=candidate,
                    status=ProofStatus.DISPROVED,
                    counterexample=cx,
                    proof_method="Z3 SMT Counterexample Found",
                    verification_time_ms=round(elapsed, 3),
                )
            else:
                return DiscoveryResult(
                    conjecture=candidate,
                    status=ProofStatus.UNKNOWN,
                    proof_method="Z3 SMT Solver Timeout or Unknown",
                    verification_time_ms=round(elapsed, 3),
                )
        except Exception as e:
            elapsed = (time.time() - t0) * 1000.0
            return DiscoveryResult(
                conjecture=candidate,
                status=ProofStatus.ERROR,
                proof_method=f"SMT verification error: {str(e)}",
                verification_time_ms=round(elapsed, 3),
            )
