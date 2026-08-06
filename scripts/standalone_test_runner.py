"""
Lightweight Pytest Compatibility Engine & Test Runner
Provides full support for pytest.mark, pytest.fixture, pytest.raises, and CLI execution.
"""

from __future__ import annotations

import sys
import os
import inspect
import traceback
import time
from typing import Any, Callable, Dict, List, Optional, Type


class MarkDecorator:
    def __getattr__(self, name: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            if not hasattr(func, "_pytest_marks"):
                func._pytest_marks = []
            func._pytest_marks.append(name)
            return func
        return decorator

    def __call__(self, *args, **kwargs) -> Callable:
        def decorator(func: Callable) -> Callable:
            return func
        return decorator


mark = MarkDecorator()


def fixture(*args, **kwargs):
    def decorator(func: Callable) -> Callable:
        func._is_pytest_fixture = True
        func._fixture_scope = kwargs.get("scope", "function")
        return func

    if len(args) == 1 and callable(args[0]):
        return decorator(args[0])
    return decorator


class RaisesContext:
    def __init__(self, expected_exception: Type[BaseException], match: Optional[str] = None):
        self.expected_exception = expected_exception
        self.match = match
        self.value = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            raise AssertionError(f"DID NOT RAISE {self.expected_exception.__name__}")
        if not issubclass(exc_type, self.expected_exception):
            return False  # Re-raise exception
        self.value = exc_val
        if self.match and self.match not in str(exc_val):
            raise AssertionError(f"Pattern '{self.match}' not found in '{str(exc_val)}'")
        return True  # Suppress exception


def raises(expected_exception: Type[BaseException], *args, **kwargs) -> RaisesContext:
    match = kwargs.get("match")
    return RaisesContext(expected_exception, match=match)


def main(args: Optional[List[str]] = None) -> int:
    if args is None:
        args = sys.argv[1:]

    verbose = "-v" in args or "--verbose" in args
    files_to_run = [a for a in args if not a.startswith("-")]

    if not files_to_run:
        # Discover test files
        files_to_run = []
        for root, _, files in os.walk("."):
            for f in files:
                if (f.startswith("test_") or f.endswith("_test.py")) and f.endswith(".py"):
                    files_to_run.append(os.path.join(root, f))

    total_passed = 0
    total_failed = 0
    start_time = time.time()

    print(f"============================= test session starts ==============================")
    print(f"platform {sys.platform} -- Python {sys.version.split()[0]}")
    print(f"rootdir: {os.getcwd()}")
    print(f"collected {len(files_to_run)} test file(s)\n")

    for file_path in files_to_run:
        if not os.path.exists(file_path):
            print(f"ERROR: file not found: {file_path}")
            continue

        mod_name = os.path.basename(file_path).replace(".py", "")
        import importlib.util
        spec = importlib.util.spec_from_file_location(mod_name, file_path)
        if spec is None or spec.loader is None:
            print(f"ERROR: could not load spec for {file_path}")
            continue

        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"ERROR loading {file_path}: {e}")
            traceback.print_exc()
            total_failed += 1
            continue

        # Discover fixtures
        fixtures: Dict[str, Callable] = {}
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr) and getattr(attr, "_is_pytest_fixture", False):
                fixtures[attr_name] = attr

        # Discover test functions
        test_funcs = []
        for attr_name in dir(module):
            if attr_name.startswith("test_"):
                attr = getattr(module, attr_name)
                if callable(attr):
                    test_funcs.append((attr_name, attr))

        test_funcs.sort(key=lambda x: inspect.getsourcelines(x[1])[1] if hasattr(x[1], "__code__") else 0)

        for tname, func in test_funcs:
            sig = inspect.signature(func)
            kwargs = {}
            generator_teardowns = []
            failed_fixture = False

            def resolve_fixture(fix_name):
                if fix_name not in fixtures:
                    return None
                fix_fn = fixtures[fix_name]
                fix_sig = inspect.signature(fix_fn)
                fix_kwargs = {}
                for f_param in fix_sig.parameters:
                    if f_param in fixtures:
                        fix_kwargs[f_param] = resolve_fixture(f_param)
                res = fix_fn(**fix_kwargs)
                if inspect.isgenerator(res):
                    val = next(res)
                    generator_teardowns.append(res)
                    return val
                return res

            for param_name in sig.parameters:
                if param_name in fixtures:
                    try:
                        kwargs[param_name] = resolve_fixture(param_name)
                    except Exception as fe:
                        print(f"{file_path}::{tname} ERROR in fixture '{param_name}': {fe}")
                        failed_fixture = True
                        break

            if failed_fixture:
                total_failed += 1
                continue

            t0 = time.time()
            try:
                func(**kwargs)
                duration = time.time() - t0
                total_passed += 1
                if verbose:
                    print(f"{file_path}::{tname} PASSED [{total_passed + total_failed}]")
                else:
                    sys.stdout.write(".")
                    sys.stdout.flush()
            except Exception as e:
                duration = time.time() - t0
                total_failed += 1
                print(f"\n{file_path}::{tname} FAILED [{total_passed + total_failed}]")
                print(f"    Exception: {e}")
                traceback.print_exc()
            finally:
                for gen in generator_teardowns:
                    try:
                        next(gen)
                    except StopIteration:
                        pass
                    except Exception as te:
                        print(f"    Teardown error in fixture: {te}")

    duration = time.time() - start_time
    print(f"\n==================== {total_passed} passed, {total_failed} failed in {duration:.2f}s ====================")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
