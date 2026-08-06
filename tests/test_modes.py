"""Tests for AXIOM operation mode contracts."""

from axiom.modes import (
    DEMO_MODE_CONTRACT,
    RESEARCH_LOOP_MODE_CONTRACT,
    RESEARCH_MODE_CONTRACT,
    OperationMode,
)


def test_demo_mode_never_represents_capability():
    assert DEMO_MODE_CONTRACT.mode == OperationMode.DEMO
    assert DEMO_MODE_CONTRACT.represents_scientific_capability is False
    assert DEMO_MODE_CONTRACT.uses_curated_data is True
    assert DEMO_MODE_CONTRACT.evidence_required is False


def test_research_mode_expects_uncertainty():
    assert RESEARCH_MODE_CONTRACT.mode == OperationMode.RESEARCH
    assert RESEARCH_MODE_CONTRACT.represents_scientific_capability is True
    assert RESEARCH_MODE_CONTRACT.uncertainty_expected is True
    assert RESEARCH_MODE_CONTRACT.evidence_required is True


def test_research_loop_mode_is_research():
    assert RESEARCH_LOOP_MODE_CONTRACT.mode == OperationMode.RESEARCH
    assert RESEARCH_LOOP_MODE_CONTRACT.uncertainty_expected is True
