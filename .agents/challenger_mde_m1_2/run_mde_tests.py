import sys
import os

# Add shims and project root to sys.path
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
SHIMS_DIR = os.path.join(AGENT_DIR, "shims")
PROJECT_ROOT = os.path.abspath(os.path.join(AGENT_DIR, "../.."))

sys.path.insert(0, SHIMS_DIR)
sys.path.insert(0, PROJECT_ROOT)

import inspect
import tests.test_mde_ontology as test_module

def run_all_tests():
    print(f"=== Running test_mde_ontology suite using python at {sys.executable} ===")
    test_funcs = [
        (name, func) for name, func in inspect.getmembers(test_module, inspect.isfunction)
        if name.startswith("test_")
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    for name, func in test_funcs:
        sig = inspect.signature(func)
        try:
            if "temp_db" in sig.parameters:
                # Invoke generator fixture temp_db
                gen = test_module.temp_db()
                store = next(gen)
                try:
                    func(store)
                finally:
                    try:
                        next(gen)
                    except StopIteration:
                        pass
            else:
                func()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
            errors.append((name, e))

    print(f"\nTest Summary: {passed} passed, {failed} failed out of {len(test_funcs)} total.")
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
