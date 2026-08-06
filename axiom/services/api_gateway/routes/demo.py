"""Golden Demo API — public endpoints for the Milestone 006 demonstration."""

from __future__ import annotations

from fastapi import APIRouter

from axiom.demo.data import build_demo_state
from axiom.demo.schema import DemoState, DemoTourStep

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/state", response_model=DemoState)
def get_demo_state() -> DemoState:
    """Return the complete curated Golden Demo dataset."""
    return build_demo_state()


@router.get("/tour")
def get_demo_tour() -> list[DemoTourStep]:
    """Return guided tour steps for the interactive walkthrough."""
    return build_demo_state().tour_steps


@router.get("/health")
def demo_health() -> dict:
    """Demo subsystem health check."""
    return {"status": "ready", "mode": "golden", "version": "0.5-demo"}
