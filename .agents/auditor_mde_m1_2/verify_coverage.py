import sys
import os
import trace
import unittest

PROJECT_ROOT = "/Users/itachiuchiha/.gemini/antigravity/scratch/axiom"
SHIMS_DIR = os.path.join(PROJECT_ROOT, ".agents/worker_mde_m1_2/shims")

sys.path.insert(0, SHIMS_DIR)
sys.path.insert(0, PROJECT_ROOT)

def main():
    tracer = trace.Trace(
        count=1,
        trace=0,
        ignoredirs=[sys.prefix, sys.exec_prefix]
    )

    import importlib.util
    spec = importlib.util.spec_from_file_location("custom_pytest", os.path.join(PROJECT_ROOT, "pytest.py"))
    custom_pytest = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(custom_pytest)

    print("=== Tracing execution of unit tests ===")
    tracer.runfunc(custom_pytest.main, ["tests/test_mde_ontology.py", "tests/test_epistemic_layer.py", "-v"])

    results = tracer.results()
    executed_files = results.counts

    target_files = [
        "axiom/core/knowledge_graph/schema.py",
        "axiom/core/knowledge_graph/migrations.py",
        "axiom/core/knowledge_graph/db.py",
    ]

    print("\n=== Line Coverage Summary for Target Source Files ===")
    for rel_path in target_files:
        full_path = os.path.join(PROJECT_ROOT, rel_path)
        executed_lines = [line for (filename, line) in executed_files.keys() if filename == full_path]
        print(f"File: {rel_path} -> Executed lines count: {len(executed_lines)}")
        assert len(executed_lines) > 0, f"File {rel_path} was NOT executed during test run!"

    print("\nPASS: All target source files executed real code paths during unit test execution.\n")

if __name__ == "__main__":
    main()
