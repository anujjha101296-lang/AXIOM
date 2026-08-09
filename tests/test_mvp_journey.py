"""Automated MVP product journey — signup through campaign cycle."""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from axiom.services.api_gateway.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = str(tmp_path / "journey.db")
    monkeypatch.setenv("AXIOM_DB_PATH", db)
    from axiom.config import settings
    from axiom.services.api_gateway.routes import research as research_routes

    monkeypatch.setattr(settings, "db_path", db)
    monkeypatch.setattr(settings, "research_upload_dir", str(tmp_path / "uploads"))
    research_routes._store = None
    return TestClient(app)


def _pdf_bytes(text: str = "Riemann Hypothesis critical line evidence.") -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    # Blank PDF pages have no text; research store tests often inject text via store.
    # For upload path, extractor may return empty — inject via note if needed.
    # Prefer a minimal valid PDF; workspace tests already handle empty-text rejection.
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def test_mvp_journey_signup_to_campaign(client: TestClient, tmp_path, monkeypatch):
    # 1. Signup
    signup = client.post(
        "/auth/signup",
        json={
            "email": "journey@example.com",
            "password": "securepass1",
            "display_name": "Journey",
        },
    )
    assert signup.status_code == 201, signup.text
    token = signup.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create project
    project = client.post(
        "/research/projects",
        headers=headers,
        json={"name": "MVP Journey", "description": "End-to-end research"},
    )
    assert project.status_code == 201, project.text
    project_id = project.json()["id"]
    assert project.json()["owner_id"]

    # 3–4. Upload document — blank PDF may lack extractable text; seed via store API path
    # Prefer real upload when text exists. Use store add through a note + search for core path,
    # and also create document via internal store for Q&A.
    from axiom.config import settings
    from axiom.research.store import ResearchStore

    store = ResearchStore(settings.db_path, settings.research_upload_dir)
    doc = store.add_document(
        project_id,
        "rh_paper.pdf",
        "The Riemann Hypothesis states that all non-trivial zeros of the zeta function "
        "lie on the critical line Re(s)=1/2. Numerical evidence supports this claim.",
        page_count=2,
    )
    store.close()

    # 5. Search
    search = client.get(
        f"/research/search?q=Riemann&project_id={project_id}",
        headers=headers,
    )
    assert search.status_code == 200, search.text
    assert len(search.json()) >= 1

    # 6–8. Ask with evidence
    ask = client.post(
        f"/research/projects/{project_id}/ask",
        headers=headers,
        json={"question": "Where do non-trivial zeros lie according to the paper?"},
    )
    assert ask.status_code == 200, ask.text
    body = ask.json()
    assert body["answer"]
    assert body["sources"]
    assert body["citations"]
    assert body["provider_mode"] in {"real", "mock", "extractive"}
    assert body["conversation_id"]

    # 9. Create note as hypothesis stand-in
    note = client.post(
        f"/research/projects/{project_id}/notes",
        headers=headers,
        json={
            "title": "Hypothesis",
            "body": "Critical line hosts all non-trivial zeros.",
            "tags": ["hypothesis"],
            "document_id": doc.id,
        },
    )
    assert note.status_code == 201, note.text

    # 10–12. Campaign create → scope → plan → cycle
    camp = client.post(
        "/frce/campaigns",
        headers=headers,
        json={
            "name": "RH investigation",
            "objective": "Investigate critical line evidence in uploaded literature",
            "problem_definition": "Do uploaded sources support zeros on Re(s)=1/2?",
        },
    )
    assert camp.status_code == 200, camp.text
    campaign_id = camp.json()["campaign_id"]

    scoped = client.post(f"/frce/campaigns/{campaign_id}/scope", headers=headers)
    assert scoped.status_code == 200, scoped.text

    planned = client.post(f"/frce/campaigns/{campaign_id}/plan", headers=headers)
    assert planned.status_code == 200, planned.text

    cycle = client.post(f"/frce/campaigns/{campaign_id}/cycle", headers=headers)
    assert cycle.status_code == 200, cycle.text

    dash = client.get(f"/frce/campaigns/{campaign_id}/dashboard", headers=headers)
    assert dash.status_code == 200, dash.text
    assert dash.json()["campaign_id"] == campaign_id

    # 13. Persistence — list projects and campaigns still present
    projects = client.get("/research/projects", headers=headers)
    assert any(p["id"] == project_id for p in projects.json())
    camps = client.get("/frce/campaigns", headers=headers)
    assert camps.status_code == 200
    assert any(c["campaign_id"] == campaign_id for c in camps.json()["campaigns"])
