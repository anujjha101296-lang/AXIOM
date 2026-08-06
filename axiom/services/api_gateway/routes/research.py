"""Research workspace API routes."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from axiom.config import settings
from axiom.observability.logger import get_logger
from axiom.research.pdf_extractor import PdfExtractor
from axiom.research.schema import (
    CreateNoteRequest,
    CreateProjectRequest,
    ProjectDetail,
    ResearchDocument,
    ResearchNote,
    ResearchProject,
    ResearchSession,
    SearchResult,
    UpdateNoteRequest,
)
from axiom.research.store import ResearchStore
from axiom.research.summarizer import DocumentSummarizer
from axiom.services.api_gateway.auth import verify_token
from axiom.services.model_gateway.client import ModelClient

logger = get_logger("axiom.api.research")

router = APIRouter(prefix="/research", tags=["research"])

_store: ResearchStore | None = None
_pdf_extractor = PdfExtractor()
_summarizer: DocumentSummarizer | None = None


def get_research_store() -> ResearchStore:
    global _store
    if _store is None:
        _store = ResearchStore(settings.db_path, settings.research_upload_dir)
    return _store


def get_summarizer() -> DocumentSummarizer:
    global _summarizer
    if _summarizer is None:
        _summarizer = DocumentSummarizer(ModelClient())
    return _summarizer


def _not_found(resource: str, identifier: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found: {identifier}",
    )


@router.post("/projects", response_model=ResearchProject, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: CreateProjectRequest,
    token: str = Depends(verify_token),
    store: ResearchStore = Depends(get_research_store),
) -> ResearchProject:
    try:
        return store.create_project(payload.name, payload.description)
    except Exception as exc:
        logger.error("Failed to create project", extra={"error": str(exc)}, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create project") from exc


@router.get("/projects", response_model=List[ResearchProject])
def list_projects(
    token: str = Depends(verify_token),
    store: ResearchStore = Depends(get_research_store),
) -> List[ResearchProject]:
    return store.list_projects()


@router.get("/projects/{project_id}", response_model=ProjectDetail)
def get_project(
    project_id: str,
    token: str = Depends(verify_token),
    store: ResearchStore = Depends(get_research_store),
) -> ProjectDetail:
    try:
        return store.get_project_detail(project_id)
    except KeyError:
        raise _not_found("Project", project_id)


@router.post(
    "/projects/{project_id}/documents/upload",
    response_model=ResearchDocument,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    token: str = Depends(verify_token),
    store: ResearchStore = Depends(get_research_store),
) -> ResearchDocument:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    try:
        raw = file.file.read()
        if not raw:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        if len(raw) > settings.research_max_upload_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum size of {settings.research_max_upload_bytes} bytes",
            )

        extraction = _pdf_extractor.extract_bytes(raw)
        if not extraction.text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No extractable text found in PDF (may be scanned/image-only)",
            )

        document = store.add_document(
            project_id=project_id,
            filename=file.filename,
            text_content=extraction.text,
            page_count=extraction.page_count,
            file_bytes=raw,
        )
        logger.info(
            "PDF uploaded",
            extra={
                "project_id": project_id,
                "document_id": document.id,
                "pages": extraction.page_count,
            },
        )
        return document
    except KeyError as exc:
        detail = str(exc)
        if "Project" in detail:
            raise _not_found("Project", project_id) from exc
        if "Document" in detail:
            raise HTTPException(status_code=404, detail=detail) from exc
        raise HTTPException(status_code=404, detail=detail) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("PDF upload failed", extra={"project_id": project_id, "error": str(exc)})
        raise HTTPException(status_code=500, detail="Failed to process PDF upload") from exc


@router.post(
    "/projects/{project_id}/documents/{document_id}/summarize",
    response_model=ResearchDocument,
)
def summarize_document(
    project_id: str,
    document_id: str,
    token: str = Depends(verify_token),
    store: ResearchStore = Depends(get_research_store),
    summarizer: DocumentSummarizer = Depends(get_summarizer),
) -> ResearchDocument:
    try:
        doc = store.get_document(document_id)
        if doc.project_id != project_id:
            raise _not_found("Document", document_id)
        summary = summarizer.summarize(doc.text_content, title=doc.filename)
        return store.update_document_summary(document_id, summary)
    except KeyError:
        raise _not_found("Document", document_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Summarization failed", extra={"document_id": document_id, "error": str(exc)})
        raise HTTPException(status_code=500, detail="Failed to generate summary") from exc


@router.get("/projects/{project_id}/documents", response_model=List[ResearchDocument])
def list_documents(
    project_id: str,
    token: str = Depends(verify_token),
    store: ResearchStore = Depends(get_research_store),
) -> List[ResearchDocument]:
    try:
        store.get_project(project_id)
        return store.list_documents(project_id)
    except KeyError:
        raise _not_found("Project", project_id)


@router.post(
    "/projects/{project_id}/notes",
    response_model=ResearchNote,
    status_code=status.HTTP_201_CREATED,
)
def create_note(
    project_id: str,
    payload: CreateNoteRequest,
    token: str = Depends(verify_token),
    store: ResearchStore = Depends(get_research_store),
) -> ResearchNote:
    try:
        return store.create_note(
            project_id=project_id,
            title=payload.title,
            body=payload.body,
            document_id=payload.document_id,
            tags=payload.tags,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/projects/{project_id}/notes", response_model=List[ResearchNote])
def list_notes(
    project_id: str,
    token: str = Depends(verify_token),
    store: ResearchStore = Depends(get_research_store),
) -> List[ResearchNote]:
    try:
        store.get_project(project_id)
        return store.list_notes(project_id)
    except KeyError:
        raise _not_found("Project", project_id)


@router.put("/projects/{project_id}/notes/{note_id}", response_model=ResearchNote)
def update_note(
    project_id: str,
    note_id: str,
    payload: UpdateNoteRequest,
    token: str = Depends(verify_token),
    store: ResearchStore = Depends(get_research_store),
) -> ResearchNote:
    try:
        note = store.get_note(note_id)
        if note.project_id != project_id:
            raise _not_found("Note", note_id)
        return store.update_note(
            note_id,
            title=payload.title,
            body=payload.body,
            tags=payload.tags,
        )
    except KeyError:
        raise _not_found("Note", note_id)


@router.get("/search", response_model=List[SearchResult])
def search_research(
    q: str = Query(..., min_length=1, description="Search query"),
    project_id: Optional[str] = Query(None, description="Limit to project"),
    limit: int = Query(20, ge=1, le=100),
    token: str = Depends(verify_token),
    store: ResearchStore = Depends(get_research_store),
) -> List[SearchResult]:
    if project_id:
        try:
            store.get_project(project_id)
        except KeyError:
            raise _not_found("Project", project_id)
    return store.search(q, project_id=project_id, limit=limit)


@router.post("/projects/{project_id}/sessions/resume", response_model=ResearchSession)
def resume_session(
    project_id: str,
    active_document_id: Optional[str] = Query(None),
    token: str = Depends(verify_token),
    store: ResearchStore = Depends(get_research_store),
) -> ResearchSession:
    try:
        return store.resume_session(project_id, active_document_id=active_document_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/projects/{project_id}/sessions/current", response_model=ResearchSession)
def get_current_session(
    project_id: str,
    token: str = Depends(verify_token),
    store: ResearchStore = Depends(get_research_store),
) -> ResearchSession:
    try:
        store.get_project(project_id)
        session = store.get_session(project_id)
        if not session:
            session = store.resume_session(project_id)
        return session
    except KeyError:
        raise _not_found("Project", project_id)
