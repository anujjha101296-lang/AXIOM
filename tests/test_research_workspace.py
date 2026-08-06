"""Tests for the research workspace vertical slice."""

from __future__ import annotations

import io
import os

import pytest
from fastapi.testclient import TestClient

from axiom.research.pdf_extractor import PdfExtractor
from axiom.research.store import ResearchStore
from axiom.research.summarizer import DocumentSummarizer
from axiom.services.api_gateway.main import app


@pytest.fixture
def client():
  token = os.environ.get("AXIOM_API_TOKEN", "test_token")
  return TestClient(app, headers={"Authorization": f"Bearer {token}"})


@pytest.fixture
def research_store(tmp_path):
  store = ResearchStore(str(tmp_path / "research.db"), str(tmp_path / "uploads"))
  yield store
  store.close()


def _make_pdf_bytes(text: str = "Riemann zeta function research paper content.") -> bytes:
  from pypdf import PdfWriter

  writer = PdfWriter()
  writer.add_blank_page(width=612, height=792)
  buffer = io.BytesIO()
  writer.write(buffer)
  return buffer.getvalue()


class TestPdfExtractor:
  def test_extract_raises_on_invalid_pdf(self):
    extractor = PdfExtractor()
    with pytest.raises(ValueError, match="Failed to extract"):
      extractor.extract_bytes(b"not a pdf")


class TestResearchStore:
  def test_create_project_and_session(self, research_store):
    project = research_store.create_project("RH Study", "Zeros on critical line")
    assert project.name == "RH Study"
    assert project.id

    session = research_store.get_session(project.id)
    assert session is not None
    assert session.project_id == project.id

  def test_upload_document_and_search(self, research_store):
    project = research_store.create_project("Search Test")
    doc = research_store.add_document(
      project.id,
      "paper.pdf",
      "The Riemann Hypothesis states all non-trivial zeros lie on Re(s)=1/2.",
      page_count=3,
    )
    assert doc.char_count > 0

    results = research_store.search("Riemann zeros", project_id=project.id)
    assert len(results) >= 1
    assert any(r.result_type == "document" for r in results)

  def test_notes_crud(self, research_store):
    project = research_store.create_project("Notes Test")
    note = research_store.create_note(
      project.id,
      title="Key insight",
      body="Functional equation links zeta(s) and zeta(1-s).",
      tags=["zeta", "insight"],
    )
    updated = research_store.update_note(note.id, body="Updated insight about symmetry.")
    assert "symmetry" in updated.body

    notes = research_store.list_notes(project.id)
    assert len(notes) == 1

  def test_resume_session(self, research_store):
    project = research_store.create_project("Session Test")
    doc = research_store.add_document(project.id, "a.pdf", "content", 1)
    session = research_store.resume_session(project.id, active_document_id=doc.id)
    assert session.active_document_id == doc.id

    resumed = research_store.resume_session(project.id)
    assert resumed.project_id == project.id


class TestDocumentSummarizer:
  def test_summarize_nonempty_text(self):
    summarizer = DocumentSummarizer()
    summary = summarizer.summarize(
      "This paper studies the distribution of prime numbers using analytic methods.",
      title="Prime Paper",
    )
    assert len(summary) >= 40


class TestResearchAPI:
  def test_full_vertical_slice(self, client, tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "api_research.db"))
    monkeypatch.setenv("RESEARCH_UPLOAD_DIR", str(tmp_path / "uploads"))

    from axiom.research.pdf_extractor import PdfExtractionResult
    import axiom.services.api_gateway.routes.research as research_routes

    research_routes._store = None
    research_routes._summarizer = None

    def _mock_extract(_self, data: bytes) -> PdfExtractionResult:
      return PdfExtractionResult(
        text="The Riemann zeta function zeta(s) encodes prime distribution. "
        "Non-trivial zeros are conjectured to lie on Re(s)=1/2.",
        page_count=2,
      )

    monkeypatch.setattr(
      research_routes._pdf_extractor.__class__,
      "extract_bytes",
      _mock_extract,
    )

    # 1. Create project
    res = client.post("/research/projects", json={"name": "Demo Project", "description": "E2E test"})
    assert res.status_code == 201, res.text
    project_id = res.json()["id"]

    # 2. Upload PDF
    res = client.post(
      f"/research/projects/{project_id}/documents/upload",
      files={"file": ("sample.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    assert res.status_code == 201, res.text
    document_id = res.json()["id"]

    # 3. Summarize
    res = client.post(f"/research/projects/{project_id}/documents/{document_id}/summarize")
    assert res.status_code == 200
    assert len(res.json()["summary"]) >= 40

    # 4. Create note
    res = client.post(
      f"/research/projects/{project_id}/notes",
      json={
        "title": "Literature note",
        "body": "Riemann zeta zeros and the critical line are central to analytic number theory.",
        "tags": ["zeta", "RH"],
        "document_id": document_id,
      },
    )
    assert res.status_code == 201
    note_id = res.json()["id"]

    # 5. Search
    res = client.get("/research/search", params={"q": "Riemann", "project_id": project_id})
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # 6. Resume session
    res = client.post(
      f"/research/projects/{project_id}/sessions/resume",
      params={"active_document_id": document_id},
    )
    assert res.status_code == 200
    assert res.json()["active_document_id"] == document_id

    res = client.get(f"/research/projects/{project_id}/sessions/current")
    assert res.status_code == 200

    # 7. Update note
    res = client.put(
      f"/research/projects/{project_id}/notes/{note_id}",
      json={"body": "Updated: connections between zeta zeros and prime gaps."},
    )
    assert res.status_code == 200

    # 8. Project detail
    res = client.get(f"/research/projects/{project_id}")
    assert res.status_code == 200
    detail = res.json()
    assert detail["project"]["name"] == "Demo Project"
    assert len(detail["documents"]) == 1
    assert len(detail["notes"]) == 1
    assert detail["session"] is not None

  def test_create_project_requires_auth(self):
    unauth = TestClient(app)
    res = unauth.post("/research/projects", json={"name": "No Auth"})
    assert res.status_code == 401

  def test_reject_non_pdf_upload(self, client, tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "reject.db"))
    import axiom.services.api_gateway.routes.research as research_routes

    research_routes._store = None

    res = client.post("/research/projects", json={"name": "Upload Test"})
    project_id = res.json()["id"]

    res = client.post(
      f"/research/projects/{project_id}/documents/upload",
      files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert res.status_code == 400

  def test_pdf_upload_returns_201(self, client, tmp_path, monkeypatch):
    """Regression: reserved LogRecord keys in logging must not break upload."""
    monkeypatch.setenv("DB_PATH", str(tmp_path / "upload.db"))
    monkeypatch.setenv("RESEARCH_UPLOAD_DIR", str(tmp_path / "uploads"))
    import axiom.services.api_gateway.routes.research as research_routes

    research_routes._store = None

    res = client.post("/research/projects", json={"name": "PDF Upload"})
    assert res.status_code == 201
    project_id = res.json()["id"]

    pdf_bytes = _make_text_pdf_bytes("Riemann zeta function research content.")
    res = client.post(
      f"/research/projects/{project_id}/documents/upload",
      files={"file": ("paper.pdf", pdf_bytes, "application/pdf")},
    )
    assert res.status_code == 201, res.text
    assert res.json()["char_count"] > 0


def _make_text_pdf_bytes(text: str) -> bytes:
  """Build a minimal PDF with extractable text (no external PDF writer)."""
  objects: list[str] = []

  def obj(content: str) -> str:
    objects.append(content)
    return str(len(objects))

  font_id = obj("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
  stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET"
  content_id = obj(f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")
  page_id = obj(
    f"<< /Type /Page /Parent 5 0 R /MediaBox [0 0 612 792] "
    f"/Contents {content_id} 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> >>"
  )
  pages_id = obj(f"<< /Type /Pages /Kids [{page_id} 0 R] /Count 1 >>")
  catalog_id = obj(f"<< /Type /Catalog /Pages {pages_id} 0 R >>")

  out = ["%PDF-1.4\n"]
  xref_positions: list[int] = []
  for i, o in enumerate(objects, start=1):
    xref_positions.append(sum(len(x.encode("latin-1")) for x in out))
    out.append(f"{i} 0 obj\n{o}\nendobj\n")
  xref_start = sum(len(x.encode("latin-1")) for x in out)
  out.append(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n")
  for pos in xref_positions:
    out.append(f"{pos:010d} 00000 n \n")
  out.append(f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n")
  out.append(f"startxref\n{xref_start}\n%%EOF\n")
  return "".join(out).encode("latin-1")
