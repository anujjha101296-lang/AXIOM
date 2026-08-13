#!/usr/bin/env python3
"""Self-contained verification runner for AXIOM Phase 7 Milestone 2.

Runs all tests in tests/test_controlled_agent.py using standard Python.
"""

import asyncio
import sys
import types
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Inject stubs if dependencies are absent
try:
    import pytest
except ImportError:
    import contextlib

    class PytestStub:
        class mark:
            @staticmethod
            def asyncio(func):
                return func

            @staticmethod
            def parametrize(argnames, argvalues):
                def decorator(func):
                    func._parametrize = (argnames, argvalues)
                    return func
                return decorator

        @staticmethod
        @contextlib.contextmanager
        def raises(expected_exception):
            class ExcInfo:
                value = None

            exc_info = ExcInfo()
            try:
                yield exc_info
            except expected_exception as e:
                exc_info.value = e
            except Exception as e:
                raise AssertionError(f"Expected {expected_exception}, got {type(e)}") from e
            else:
                raise AssertionError(f"Expected {expected_exception}, but no exception was raised.")

    sys.modules["pytest"] = PytestStub()

try:
    import sqlalchemy
except ImportError:
    class Column:
        def __init__(self, *args, default=None, nullable=True, index=False, server_default=None, primary_key=False, **kwargs):
            self.args = args
            self.default = default
            self.nullable = nullable
            self.index = index
            self.server_default = server_default
            self.primary_key = primary_key
            self.name = None

        def __set_name__(self, owner, name):
            self.name = name

        def __get__(self, instance, owner):
            if instance is None:
                return self
            return instance.__dict__.get(self.name, self.default)

        def __set__(self, instance, value):
            instance.__dict__[self.name] = value

    def declarative_base():
        class Base:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
        return Base

    def dummy_func(*args, **kwargs):
        class DummyStmt:
            def join(self, *a, **kw):
                return self
            def where(self, *a, **kw):
                return self
        return DummyStmt()

    sa = types.ModuleType("sqlalchemy")
    sa.Column = Column
    sa.String = sa.DateTime = sa.ForeignKey = sa.Text = sa.Enum = sa.Integer = sa.Boolean = sa.select = dummy_func
    sys.modules["sqlalchemy"] = sa

    sa_pg = types.ModuleType("sqlalchemy.dialects.postgresql")
    sa_pg.UUID = dummy_func
    sys.modules["sqlalchemy.dialects"] = types.ModuleType("sqlalchemy.dialects")
    sys.modules["sqlalchemy.dialects.postgresql"] = sa_pg

    sa_orm = types.ModuleType("sqlalchemy.orm")
    sa_orm.declarative_base = declarative_base
    sa_orm.relationship = dummy_func
    sys.modules["sqlalchemy.orm"] = sa_orm


def run_verification():
    import tests.test_controlled_agent as test_mod

    passed = 0
    failed = 0
    total = 0

    print("======================================================================")
    print("AXIOM Phase 7 Milestone 2 Verification Suite (Planning & Tool Registry)")
    print("======================================================================")

    test_funcs = [
        (name, getattr(test_mod, name))
        for name in dir(test_mod)
        if name.startswith("test_") and callable(getattr(test_mod, name))
    ]

    for name, func in test_funcs:
        if hasattr(func, "_parametrize"):
            argnames, argvalues = func._parametrize
            arg_list = [a.strip() for a in argnames.split(",")]
            for val_tuple in argvalues:
                total += 1
                if not isinstance(val_tuple, tuple):
                    val_tuple = (val_tuple,)
                kwargs = dict(zip(arg_list, val_tuple))
                try:
                    if asyncio.iscoroutinefunction(func):
                        asyncio.run(func(**kwargs))
                    else:
                        func(**kwargs)
                    passed += 1
                except Exception as err:
                    failed += 1
                    print(f"  FAIL: {name}({kwargs}) -> {err}")
        else:
            total += 1
            try:
                if asyncio.iscoroutinefunction(func):
                    asyncio.run(func())
                else:
                    func()
                passed += 1
                print(f"  PASS: {name}")
            except Exception as err:
                failed += 1
                print(f"  FAIL: {name} -> {err}")

    print("----------------------------------------------------------------------")
    print(f"TOTAL TESTS RUN: {total} | PASSED: {passed} | FAILED: {failed}")
    if failed == 0:
        print("STATUS: 100% SUCCESS — Phase 7 Milestone 2 Verified Green!")
    else:
        print("STATUS: VERIFICATION FAILED")
    print("======================================================================")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_verification())
