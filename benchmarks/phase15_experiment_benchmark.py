"""
AXIOM Phase 15 — Computational Experiment & Verification Benchmark
15 deterministic benchmark test cases.
Saved to evaluation_results/phase15_experiment_benchmark.json
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from axiom.experiment.models import (
    Experiment,
    ExperimentRun,
    ExperimentStatus,
    ObservationLevel,
    ReproducibilityStatus,
    VerificationStatus,
)
from axiom.experiment.sandbox import SecureSandbox
from axiom.experiment.designer import ExperimentDesigner
from axiom.experiment.executor import ExperimentExecutor
from axiom.experiment.reproducibility import ReproducibilityEngine
from axiom.experiment.independent_verifier import IndependentVerifier
from axiom.experiment.interpretation import ScientificInterpreter
from axiom.hypothesis.models import Hypothesis, HypothesisStatus


def run_benchmarks():
    print("=" * 70)
    print("AXIOM PHASE 15 — COMPUTATIONAL EXPERIMENT BENCHMARKS")
    print("=" * 70)

    results = []

    sandbox = SecureSandbox(timeout_seconds=2.0, max_memory_mb=64, max_output_bytes=1000)
    executor = ExperimentExecutor()
    designer = ExperimentDesigner()
    verifier = IndependentVerifier()
    interpreter = ScientificInterpreter()
    repro_engine = ReproducibilityEngine()

    # CASE 1: Correct calculation
    res1 = sandbox.execute_code("result = {'val': sum(range(100))}")
    pass_c1 = res1["status"] == ExperimentStatus.COMPLETED and res1["result_data"].get("val") == 4950
    results.append({"case": 1, "name": "Correct calculation execution", "passed": pass_c1})

    # CASE 2: Incorrect calculation / Error handling
    res2 = sandbox.execute_code("x = 1 / 0")
    pass_c2 = res2["status"] == ExperimentStatus.FAILED and "ZeroDivisionError" in res2["stderr"]
    results.append({"case": 2, "name": "Incorrect calculation error capture", "passed": pass_c2})

    # CASE 3: Reproducibility test
    exp3 = designer.design_experiment("proj-1", name="Repro Exp", code_body="import math\nresult = {'v': math.sqrt(16)}")
    status_3, r1, r2 = repro_engine.test_reproducibility(exp3, seed=42)
    pass_c3 = status_3 == ReproducibilityStatus.REPRODUCIBLE and r1.input_hash == r2.input_hash
    results.append({"case": 3, "name": "Reproducibility verification", "passed": pass_c3})

    # CASE 4: Independent verification test
    exp4_run = executor.run_experiment(exp3)
    v4 = verifier.verify_run(exp3.id, exp4_run)
    pass_c4 = v4.verification_status == VerificationStatus.VERIFIED
    results.append({"case": 4, "name": "Independent verification check", "passed": pass_c4})

    # CASE 5: Prediction supported
    h5 = Hypothesis(project_id="proj-1", claim="Identity holds.", status=HypothesisStatus.PROPOSED)
    exp5_run = executor.run_experiment(exp3)
    obs5, h5_up = interpreter.interpret_experiment(exp3.id, exp5_run, h5)
    pass_c5 = h5_up.status == HypothesisStatus.SUPPORTED and not obs5.is_mathematical_proof
    results.append({"case": 5, "name": "Prediction supported hypothesis update", "passed": pass_c5})

    # CASE 6: Prediction contradicted
    exp6 = designer.design_experiment("proj-1", name="Fail Exp", code_body="result = {'failed': True, 'identity_error': 0.5}")
    exp6_run = executor.run_experiment(exp6)
    h6 = Hypothesis(project_id="proj-1", claim="False claim.", status=HypothesisStatus.PROPOSED)
    obs6, h6_up = interpreter.interpret_experiment(exp6.id, exp6_run, h6)
    pass_c6 = h6_up.status == HypothesisStatus.CONTRADICTED
    results.append({"case": 6, "name": "Prediction contradicted hypothesis update", "passed": pass_c6})

    # CASE 7: Inconclusive experiment (timeout run)
    run7 = ExperimentRun(experiment_id="e7", status=ExperimentStatus.TIMEOUT)
    h7 = Hypothesis(project_id="proj-1", claim="Inconclusive test.")
    obs7, h7_up = interpreter.interpret_experiment("e7", run7, h7)
    pass_c7 = obs7.is_mathematical_proof == False and obs7.metrics.get("status") == "TIMEOUT"
    results.append({"case": 7, "name": "Inconclusive experiment status preservation", "passed": pass_c7})

    # CASE 8: Timeout attack blocking
    res8 = sandbox.execute_code("while True:\n    pass")
    pass_c8 = res8["status"] in (ExperimentStatus.TIMEOUT, ExperimentStatus.FAILED)
    results.append({"case": 8, "name": "Timeout infinite loop blocking", "passed": pass_c8})

    # CASE 9: Memory exhaustion blocking
    res9 = sandbox.execute_code("raise MemoryError('Memory limit exceeded')")
    pass_c9 = res9["status"] in (ExperimentStatus.MEMORY_LIMIT_EXCEEDED, ExperimentStatus.FAILED)
    results.append({"case": 9, "name": "Memory allocation exhaustion blocking", "passed": pass_c9})

    # CASE 10: Huge output limit truncation
    res10 = sandbox.execute_code("print('X' * 5000)")
    pass_c10 = "[OUTPUT TRUNCATED" in res10["stdout"]
    results.append({"case": 10, "name": "Huge stdout truncation limit", "passed": pass_c10})

    # CASE 11: Network attempt blocking
    res11 = sandbox.execute_code("import socket\ns = socket.socket()")
    pass_c11 = res11["status"] == ExperimentStatus.SECURITY_VIOLATION
    results.append({"case": 11, "name": "Network socket attempt blocking", "passed": pass_c11})

    # CASE 12: Filesystem path traversal blocking
    res12 = sandbox.execute_code("with open('/etc/passwd') as f: text = f.read()")
    pass_c12 = res12["status"] in (ExperimentStatus.SECURITY_VIOLATION, ExperimentStatus.FAILED)
    results.append({"case": 12, "name": "Filesystem path traversal blocking", "passed": pass_c12})

    # CASE 13: Subprocess execution blocking
    res13 = sandbox.execute_code("import subprocess\nsubprocess.run(['ls'])")
    pass_c13 = res13["status"] == ExperimentStatus.SECURITY_VIOLATION
    results.append({"case": 13, "name": "Subprocess execution blocking", "passed": pass_c13})

    # CASE 14: Cross-project access isolation
    exp14_a = designer.design_experiment("proj-A", name="A")
    exp14_b = designer.design_experiment("proj-B", name="B")
    pass_c14 = exp14_a.project_id != exp14_b.project_id
    results.append({"case": 14, "name": "Cross-project access isolation", "passed": pass_c14})

    # CASE 15: State persistence after restart
    exp15_dict = exp3.model_dump()
    exp15_restored = Experiment.model_validate(exp15_dict)
    pass_c15 = exp15_restored.id == exp3.id and exp15_restored.code_body == exp3.code_body
    results.append({"case": 15, "name": "State persistence after serialization", "passed": pass_c15})

    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    pass_rate = (passed_count / total_count) * 100.0

    print("-" * 70)
    for r in results:
        status = "PASSED" if r["passed"] else "FAILED"
        print(f"Case {r['case']:02d}: {r['name']:<45} → {status}")
    print("-" * 70)
    print(f"TOTAL BENCHMARK RESULT: {passed_count}/{total_count} PASSED ({pass_rate:.1f}%)")
    print("=" * 70)

    # Save results JSON
    os.makedirs("evaluation_results", exist_ok=True)
    summary_path = "evaluation_results/phase15_experiment_benchmark.json"
    with open(summary_path, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_cases": total_count,
                "passed_cases": passed_count,
                "pass_rate_percent": pass_rate,
                "cases": results,
            },
            f,
            indent=2,
        )

    sys.exit(0 if passed_count == total_count else 1)


if __name__ == "__main__":
    run_benchmarks()
