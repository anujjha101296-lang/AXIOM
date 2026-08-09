"""Workflow API mount verification."""

from __future__ import annotations

from axiom.workflow import get_engine


class TestWorkflowMount:
    def test_workflow_engine_available(self):
        engine = get_engine()
        assert engine is not None

    def test_workflow_router_importable(self):
        from axiom.services.api_gateway.routes.workflow_router import workflow_router
        assert workflow_router.prefix == "/workflows"

    def test_workflow_mounted_in_app(self):
        from axiom.services.api_gateway.main import app
        paths = [getattr(r, "path", "") for r in app.routes]
        assert any(p.startswith("/workflows") for p in paths)
