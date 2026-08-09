"""Proof compilation — actual prover check (FMTP §15)."""

from __future__ import annotations

from axiom.core.verification.truthfulness import (
    evidence_mode_from_compile_result,
    is_simulated_compiler_output,
)
from axiom.formal_math.models import ProofArtifact, ProofCompilationStatus, TrustLayer
from axiom.mip.formal.lean4 import check_lean4_available, compile_lean4


def compile_proof(
    artifact: ProofArtifact,
) -> tuple[ProofCompilationStatus, str, list[str]]:
    """Compile/check proof with actual theorem prover. Never claim verified from LLM alone."""
    trust_layers = [TrustLayer.GENERATED_CODE.value]

    if artifact.prover == "lean4":
        success, output = compile_lean4(artifact.source_code)
        trust_layers.append(TrustLayer.TACTIC.value)

        if is_simulated_compiler_output(output):
            trust_layers.append(TrustLayer.LLM_OUTPUT.value)
            return ProofCompilationStatus.PARTIALLY_FORMALIZED, output, trust_layers

        if "TIMEOUT" in output:
            return ProofCompilationStatus.TIMEOUT, output, trust_layers

        if success:
            if "sorry" in artifact.source_code:
                return ProofCompilationStatus.PARTIALLY_FORMALIZED, output, trust_layers
            if check_lean4_available():
                trust_layers.insert(0, TrustLayer.TRUSTED_KERNEL.value)
                return ProofCompilationStatus.FORMALLY_VERIFIED, output, trust_layers
            return ProofCompilationStatus.COMPILES, output, trust_layers

        return ProofCompilationStatus.DOES_NOT_COMPILE, output, trust_layers

    if artifact.prover == "smt":
        trust_layers.append(TrustLayer.AUTOMATION.value)
        return ProofCompilationStatus.PARTIALLY_FORMALIZED, "SMT checks are finite-domain only", trust_layers

    return ProofCompilationStatus.UNKNOWN, f"Unknown prover: {artifact.prover}", trust_layers


def classify_compilation(success: bool, output: str) -> ProofCompilationStatus:
    """Map compile result to status using truthfulness guards."""
    mode = evidence_mode_from_compile_result(success, output)
    if mode.value == "formal_compiler" and success:
        return ProofCompilationStatus.FORMALLY_VERIFIED
    if is_simulated_compiler_output(output):
        return ProofCompilationStatus.PARTIALLY_FORMALIZED
    if success:
        return ProofCompilationStatus.COMPILES
    if "TIMEOUT" in output:
        return ProofCompilationStatus.TIMEOUT
    return ProofCompilationStatus.DOES_NOT_COMPILE
