#!/usr/bin/env python3
"""Self-contained, zero-external-dependency verification script for AXIOM M1.

Validates:
1. ResearchAgentState enum and state transition engine (axiom/research/agent/state.py).
2. ResearchSession and ResearchArtifact ORM fields (axiom/core/models.py).
"""

import importlib.util
import json
import sys
import types
from pathlib import Path

# Calculate project root
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def setup_environment_and_imports():
    """Dynamically import required modules without external pip dependencies."""
    # 1. State import
    state_path = PROJECT_ROOT / "axiom" / "research" / "agent" / "state.py"
    if not state_path.exists():
        raise FileNotFoundError(f"state.py not found at {state_path}")

    spec_state = importlib.util.spec_from_file_location("axiom_state", str(state_path))
    state_mod = importlib.util.module_from_spec(spec_state)
    spec_state.loader.exec_module(state_mod)

    # 2. Models import with SQLAlchemy stubs if not installed
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
            return None

        sa = types.ModuleType("sqlalchemy")
        sa.Column = Column
        sa.String = sa.DateTime = sa.ForeignKey = sa.Text = sa.Enum = sa.Integer = sa.Boolean = dummy_func
        sys.modules["sqlalchemy"] = sa

        sa_pg = types.ModuleType("sqlalchemy.dialects.postgresql")
        sa_pg.UUID = dummy_func
        sys.modules["sqlalchemy.dialects"] = types.ModuleType("sqlalchemy.dialects")
        sys.modules["sqlalchemy.dialects.postgresql"] = sa_pg

        sa_orm = types.ModuleType("sqlalchemy.orm")
        sa_orm.declarative_base = declarative_base
        sa_orm.relationship = dummy_func
        sys.modules["sqlalchemy.orm"] = sa_orm

    models_path = PROJECT_ROOT / "axiom" / "core" / "models.py"
    if not models_path.exists():
        raise FileNotFoundError(f"models.py not found at {models_path}")

    spec_models = importlib.util.spec_from_file_location("axiom_models", str(models_path))
    models_mod = importlib.util.module_from_spec(spec_models)
    spec_models.loader.exec_module(models_mod)

    return state_mod, models_mod


def run_verification():
    passed_checks = 0
    total_checks = 0

    state_mod, models_mod = setup_environment_and_imports()

    ResearchAgentState = state_mod.ResearchAgentState
    VALID_TRANSITIONS = state_mod.VALID_TRANSITIONS
    InvalidStateTransitionError = state_mod.InvalidStateTransitionError
    validate_state_transition = state_mod.validate_state_transition
    ResearchSession = models_mod.ResearchSession
    ResearchArtifact = models_mod.ResearchArtifact

    print("======================================================================")
    print("AXIOM Phase 7 Milestone 1 Verification Suite")
    print("======================================================================")

    # 1. State Enum Values Check
    expected_states = {
        "CREATED": "CREATED",
        "PLANNING": "PLANNING",
        "RETRIEVING": "RETRIEVING",
        "ANALYZING": "ANALYZING",
        "VERIFYING": "VERIFYING",
        "COMPLETED": "COMPLETED",
        "FAILED": "FAILED",
        "CANCELLED": "CANCELLED",
    }
    assert len(ResearchAgentState) == len(expected_states), f"Expected {len(expected_states)} states, got {len(ResearchAgentState)}"
    for name, expected_val in expected_states.items():
        total_checks += 1
        assert hasattr(ResearchAgentState, name), f"Missing state {name}"
        enum_member = getattr(ResearchAgentState, name)
        assert enum_member.value == expected_val, f"Value mismatch for {name}: {enum_member.value} != {expected_val}"
        passed_checks += 1
    print(f"1. State Machine Enum Verification: PASS ({len(expected_states)} states verified)")

    # 2. Valid Transitions (25 cases)
    valid_cases = [
        (ResearchAgentState.CREATED, ResearchAgentState.PLANNING, "PLANNING"),
        (ResearchAgentState.CREATED, ResearchAgentState.FAILED, "FAILED"),
        (ResearchAgentState.CREATED, ResearchAgentState.CANCELLED, "CANCELLED"),
        (ResearchAgentState.PLANNING, ResearchAgentState.RETRIEVING, "RETRIEVING"),
        (ResearchAgentState.PLANNING, ResearchAgentState.FAILED, "FAILED"),
        (ResearchAgentState.PLANNING, ResearchAgentState.CANCELLED, "CANCELLED"),
        (ResearchAgentState.RETRIEVING, ResearchAgentState.ANALYZING, "ANALYZING"),
        (ResearchAgentState.RETRIEVING, ResearchAgentState.FAILED, "FAILED"),
        (ResearchAgentState.RETRIEVING, ResearchAgentState.CANCELLED, "CANCELLED"),
        (ResearchAgentState.ANALYZING, ResearchAgentState.VERIFYING, "VERIFYING"),
        (ResearchAgentState.ANALYZING, ResearchAgentState.RETRIEVING, "RETRIEVING"),
        (ResearchAgentState.ANALYZING, ResearchAgentState.FAILED, "FAILED"),
        (ResearchAgentState.ANALYZING, ResearchAgentState.CANCELLED, "CANCELLED"),
        (ResearchAgentState.VERIFYING, ResearchAgentState.COMPLETED, "COMPLETED"),
        (ResearchAgentState.VERIFYING, ResearchAgentState.RETRIEVING, "RETRIEVING"),
        (ResearchAgentState.VERIFYING, ResearchAgentState.FAILED, "FAILED"),
        (ResearchAgentState.VERIFYING, ResearchAgentState.CANCELLED, "CANCELLED"),
        ("CREATED", "PLANNING", "PLANNING"),
        ("PLANNING", "RETRIEVING", "RETRIEVING"),
        ("RETRIEVING", "ANALYZING", "ANALYZING"),
        ("ANALYZING", "VERIFYING", "VERIFYING"),
        ("VERIFYING", "COMPLETED", "COMPLETED"),
        ("VERIFYING", "RETRIEVING", "RETRIEVING"),
        ("CREATED", "FAILED", "FAILED"),
        ("CREATED", "CANCELLED", "CANCELLED"),
    ]
    valid_count = 0
    for curr, nxt, expected in valid_cases:
        total_checks += 1
        res = validate_state_transition(curr, nxt)
        assert res == expected, f"Expected {expected}, got {res} for transition {curr} -> {nxt}"
        passed_checks += 1
        valid_count += 1
    print(f"2. Valid Transitions Matrix:        PASS ({valid_count}/{len(valid_cases)} valid transitions verified)")

    # 3. Invalid Transitions (18 cases)
    invalid_cases = [
        (ResearchAgentState.CREATED, ResearchAgentState.COMPLETED),
        (ResearchAgentState.CREATED, ResearchAgentState.ANALYZING),
        (ResearchAgentState.CREATED, ResearchAgentState.VERIFYING),
        (ResearchAgentState.PLANNING, ResearchAgentState.COMPLETED),
        (ResearchAgentState.PLANNING, ResearchAgentState.VERIFYING),
        (ResearchAgentState.RETRIEVING, ResearchAgentState.COMPLETED),
        (ResearchAgentState.RETRIEVING, ResearchAgentState.VERIFYING),
        (ResearchAgentState.ANALYZING, ResearchAgentState.COMPLETED),
        (ResearchAgentState.ANALYZING, ResearchAgentState.PLANNING),
        (ResearchAgentState.COMPLETED, ResearchAgentState.PLANNING),
        (ResearchAgentState.FAILED, ResearchAgentState.CREATED),
        (ResearchAgentState.CANCELLED, ResearchAgentState.RETRIEVING),
        (ResearchAgentState.COMPLETED, ResearchAgentState.FAILED),
        (ResearchAgentState.FAILED, ResearchAgentState.CANCELLED),
        (ResearchAgentState.CANCELLED, ResearchAgentState.FAILED),
        (ResearchAgentState.CREATED, ResearchAgentState.CREATED),
        (ResearchAgentState.PLANNING, ResearchAgentState.PLANNING),
        (ResearchAgentState.COMPLETED, ResearchAgentState.COMPLETED),
    ]
    invalid_count = 0
    for curr, nxt in invalid_cases:
        total_checks += 1
        try:
            validate_state_transition(curr, nxt)
            assert False, f"Expected InvalidStateTransitionError for {curr} -> {nxt}"
        except InvalidStateTransitionError as exc:
            assert "Invalid state transition" in str(exc)
            passed_checks += 1
            invalid_count += 1
    print(f"3. Invalid Transitions Matrix:      PASS ({invalid_count}/{len(invalid_cases)} invalid transitions rejected)")

    # 4. Invalid State String Names
    invalid_strings = [
        ("NON_EXISTENT_STATE", "PLANNING", "Invalid current state"),
        ("CREATED", "NON_EXISTENT_STATE", "Invalid target state"),
        ("FOO", "BAR", "Invalid current state"),
    ]
    invalid_str_count = 0
    for curr, nxt, expected_err in invalid_strings:
        total_checks += 1
        try:
            validate_state_transition(curr, nxt)
            assert False, f"Expected InvalidStateTransitionError for '{curr}' -> '{nxt}'"
        except InvalidStateTransitionError as exc:
            assert expected_err in str(exc), f"Expected '{expected_err}' in '{exc}'"
            passed_checks += 1
            invalid_str_count += 1
    print(f"4. Invalid State Strings Handling:  PASS ({invalid_str_count}/{len(invalid_strings)} invalid string inputs rejected)")

    # 5. Terminal State Outgoing Transitions & Graph Structure
    total_checks += 1
    assert set(VALID_TRANSITIONS.keys()) == set(ResearchAgentState), "VALID_TRANSITIONS keys mismatch with enum"
    passed_checks += 1

    terminal_states = [
        ResearchAgentState.COMPLETED,
        ResearchAgentState.FAILED,
        ResearchAgentState.CANCELLED,
    ]
    for term in terminal_states:
        total_checks += 1
        assert len(VALID_TRANSITIONS[term]) == 0, f"Terminal state {term} has outgoing transitions"
        passed_checks += 1
    print(f"5. Terminal States Zero Outgoing:   PASS ({len(terminal_states)} terminal states verified)")

    # 6. ResearchSession ORM Inspection
    session = ResearchSession(project_id="proj-123", goal="Investigate AI safety")
    session_fields = [
        ("status", "CREATED"),
        ("goal", "Investigate AI safety"),
        ("max_steps", 10),
        ("max_tool_calls", 15),
        ("max_runtime_seconds", 120),
        ("step_count", 0),
        ("tool_call_count", 0),
        ("cancellation_requested", False),
        ("error_message", None),
        ("completed_at", None),
    ]
    session_field_count = 0
    for attr, expected_val in session_fields:
        total_checks += 1
        actual_val = getattr(session, attr)
        assert actual_val == expected_val, f"ResearchSession.{attr}: expected {expected_val!r}, got {actual_val!r}"
        passed_checks += 1
        session_field_count += 1
    print(f"6. ResearchSession ORM Inspection:   PASS ({session_field_count} fields inspected and verified)")

    # 7. ResearchArtifact ORM & Property
    dict_artifact = ResearchArtifact(
        session_id="sess-123",
        type="plan",
        content='{"goal": "Understand quantum mechanics", "subtasks": []}',
    )
    total_checks += 1
    assert dict_artifact.type == "plan"
    parsed = dict_artifact.json_content
    assert parsed == {"goal": "Understand quantum mechanics", "subtasks": []}
    passed_checks += 1

    list_artifact = ResearchArtifact(
        session_id="sess-123",
        type="data",
        content='[1, 2, 3]',
    )
    total_checks += 1
    assert list_artifact.json_content == {"data": [1, 2, 3]}
    passed_checks += 1

    raw_artifact = ResearchArtifact(
        session_id="sess-123",
        type="log",
        content="non-json raw text log",
    )
    total_checks += 1
    assert raw_artifact.json_content == {"raw": "non-json raw text log"}
    passed_checks += 1

    print("7. ResearchArtifact ORM & Property: PASS (3 json_content variations verified)")

    print("----------------------------------------------------------------------")
    print(f"TOTAL CHECKS: {passed_checks} Passed, 0 Failed, 0 Skipped")
    print("STATUS: 100% SUCCESS")
    print("======================================================================")


if __name__ == "__main__":
    run_verification()
