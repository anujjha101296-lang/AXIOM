"""
Lightweight pytest module & runner for AXIOM offline test environment.
"""

import sys
import inspect
import traceback
import importlib.util
from typing import Type

class RaisesContext:
    def __init__(self, expected_exception: Type[BaseException]):
        self.expected_exception = expected_exception
        self.exc_value = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            raise AssertionError(f"DID NOT RAISE {self.expected_exception}")
        if not issubclass(exc_type, self.expected_exception):
            return False
        self.exc_value = exc_val
        return True

def raises(expected_exception: Type[BaseException]):
    return RaisesContext(expected_exception)

def fixture(func):
    func._is_fixture = True
    return func

def main():
    args = sys.argv[1:]
    verbose = "-v" in args
    test_files = [a for a in args if not a.startswith("-")]
    if not test_files:
        test_files = ["tests/test_mde_ontology.py"]

    total_passed = 0
    total_failed = 0

    for test_file in test_files:
        print(f"============================= test session starts =============================")
        print(f"rootdir: /Users/itachiuchiha/.gemini/antigravity/scratch/axiom")
        print(f"collected test items from {test_file}\n")
        
        spec = importlib.util.spec_from_file_location("test_module", test_file)
        if spec is None or spec.loader is None:
            print(f"ERROR: Could not load test file {test_file}")
            sys.exit(1)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Collect fixtures
        fixtures = {}
        for name, item in inspect.getmembers(mod):
            if callable(item) and getattr(item, "_is_fixture", False):
                fixtures[name] = item

        # Collect test functions
        test_funcs = [
            (name, item) for name, item in inspect.getmembers(mod)
            if inspect.isfunction(item) and name.startswith("test_")
        ]

        for name, func in test_funcs:
            # Prepare arguments from fixtures
            sig = inspect.signature(func)
            kwargs = {}
            fixture_cleanups = []
            
            try:
                for param in sig.parameters:
                    if param in fixtures:
                        fix_res = fixtures[param]()
                        if inspect.isgenerator(fix_res):
                            val = next(fix_res)
                            kwargs[param] = val
                            fixture_cleanups.append(fix_res)
                        else:
                            kwargs[param] = fix_res
                    else:
                        raise RuntimeError(f"Fixture '{param}' not found for test {name}")
                
                # Execute test function
                func(**kwargs)
                total_passed += 1
                if verbose:
                    print(f"{test_file}::{name} PASSED")
                else:
                    sys.stdout.write(".")
                    sys.stdout.flush()
            except Exception as e:
                total_failed += 1
                if verbose:
                    print(f"{test_file}::{name} FAILED")
                    traceback.print_exc()
                else:
                    sys.stdout.write("F")
                    sys.stdout.flush()
            finally:
                for gen in fixture_cleanups:
                    try:
                        next(gen)
                    except StopIteration:
                        pass
        print()

    print(f"\n====================== {total_passed} passed, {total_failed} failed ======================")
    if total_failed > 0:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
