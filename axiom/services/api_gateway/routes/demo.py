"""Golden Demo API — public endpoints for the Milestone 006 demonstration."""

from __future__ import annotations

from fastapi import APIRouter

from axiom.demo.data import build_demo_state
from axiom.demo.schema import DemoState, DemoTourStep
from axiom.modes import DEMO_MODE_CONTRACT, OperationModeContract

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/mode", response_model=OperationModeContract)
def get_demo_mode() -> OperationModeContract:
    """Return the Demo Mode honesty contract. Always represents_scientific_capability=False."""
    return DEMO_MODE_CONTRACT


@router.get("/state", response_model=DemoState)
def get_demo_state() -> DemoState:
    """Return the complete curated Golden Demo dataset (Demo Mode only)."""
    return build_demo_state()


@router.get("/tour")
def get_demo_tour() -> list[DemoTourStep]:
    """Return guided tour steps for the interactive walkthrough."""
    return build_demo_state().tour_steps


@router.get("/health")
def demo_health() -> dict:
    """Demo subsystem health check."""
    return {
        "status": "ready",
        "operation_mode": "demo",
        "represents_scientific_capability": False,
        "version": "0.5-demo",
    }
