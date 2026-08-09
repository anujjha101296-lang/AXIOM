"""Scientific Knowledge Acquisition & Intelligence Loop API."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.security.deps import skai_route_auth
from axiom.skai.models import KnowledgeScope, SourceType
from axiom.skai.orchestrator import SkaiOrchestrator

router = APIRouter(
    prefix="/skai",
    tags=["scientific-knowledge-acquisition"],
    dependencies=[Depends(skai_route_auth)],
)


class AcquireTextRequest(BaseModel):
    title: str
    content: str
    research_question: str = ""
    source_type: str = "researcher_document"
    identifier: str | None = None
    is_latex: bool = False
    campaign_id: str | None = None
    scope: str = "global"
    bridge_to_egs: bool = True
    bridge_to_er: bool = True


class AcquireUrlRequest(BaseModel):
    url: str = Field(..., min_length=8, max_length=2000)
    research_question: str = ""
    campaign_id: str | None = None
    scope: str = "global"
    bridge_to_egs: bool = True
    bridge_to_er: bool = True


class SynthesizeRequest(BaseModel):
    research_question: str
    campaign_id: str | None = None


class RetrieveRequest(BaseModel):
    research_goal: str
    goal_type: str = "prove_theorem"
    campaign_id: str | None = None
    limit: int = Field(default=50, ge=1, le=200)


def _orchestrator() -> SkaiOrchestrator:
    return SkaiOrchestrator(settings.db_path)


@router.get("/manifest")
def get_manifest() -> dict[str, Any]:
    return _orchestrator().manifest()


@router.post("/acquire")
def acquire_from_text(body: AcquireTextRequest) -> dict[str, Any]:
    try:
        result = _orchestrator().acquire_from_text(
            body.title,
            body.content,
            research_question=body.research_question,
            source_type=SourceType(body.source_type),
            identifier=body.identifier,
            is_latex=body.is_latex,
            campaign_id=body.campaign_id,
            scope=KnowledgeScope(body.scope),
            bridge_to_egs=body.bridge_to_egs,
            bridge_to_er=body.bridge_to_er,
        )
        return result.to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/acquire-url")
def acquire_from_url(body: AcquireUrlRequest) -> dict[str, Any]:
    """Controlled HTTPS fetch → parse → cite/store as UNTRUSTED web source."""
    from axiom.research.web_fetch import WebFetchError

    try:
        result = _orchestrator().acquire_from_url(
            body.url,
            research_question=body.research_question,
            campaign_id=body.campaign_id,
            scope=KnowledgeScope(body.scope),
            bridge_to_egs=body.bridge_to_egs,
            bridge_to_er=body.bridge_to_er,
        )
        return result.to_dict()
    except WebFetchError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/allowed-hosts")
def list_allowed_hosts() -> dict[str, Any]:
    from axiom.research.web_fetch import DEFAULT_ALLOWED_HOSTS

    return {
        "allowed_hosts": sorted(DEFAULT_ALLOWED_HOSTS),
        "scheme": "https",
        "notes": [
            "Fetched content is always treated as UNTRUSTED.",
            "Private/link-local DNS resolutions are blocked (SSRF guard).",
            "Duplicates are detected by content hash and final URL.",
        ],
    }


@router.post("/synthesize")
def synthesize_knowledge(body: SynthesizeRequest) -> dict[str, Any]:
    return _orchestrator().synthesize_knowledge(
        body.research_question,
        campaign_id=body.campaign_id,
    )


@router.post("/retrieve")
def retrieve_for_research(body: RetrieveRequest) -> dict[str, Any]:
    from axiom.skai.retrieval import retrieve_for_research as _retrieve
    from axiom.skai.store import get_skai_store

    return _retrieve(
        get_skai_store(settings.db_path),
        body.research_goal,
        goal_type=body.goal_type,
        campaign_id=body.campaign_id,
        limit=body.limit,
    )


@router.get("/sources")
def list_sources(scope: str | None = None, campaign_id: str | None = None, limit: int = 100) -> dict[str, Any]:
    from axiom.skai.store import get_skai_store

    sources = get_skai_store(settings.db_path).list_sources(
        scope=scope, campaign_id=campaign_id, limit=limit,
    )
    return {"count": len(sources), "sources": [s.to_dict() for s in sources]}


@router.get("/entities")
def list_entities(entity_type: str | None = None, source_id: str | None = None, limit: int = 200) -> dict[str, Any]:
    from axiom.skai.store import get_skai_store

    entities = get_skai_store(settings.db_path).list_entities(
        entity_type=entity_type, source_id=source_id, limit=limit,
    )
    return {"count": len(entities), "entities": [e.to_dict() for e in entities]}


@router.get("/conflicts")
def list_conflicts(status: str | None = None, limit: int = 50) -> dict[str, Any]:
    from axiom.skai.store import get_skai_store

    conflicts = get_skai_store(settings.db_path).list_conflicts(status=status, limit=limit)
    return {"count": len(conflicts), "conflicts": [c.to_dict() for c in conflicts]}


@router.get("/gaps")
def list_gaps(campaign_id: str | None = None, limit: int = 50) -> dict[str, Any]:
    from axiom.skai.store import get_skai_store

    gaps = get_skai_store(settings.db_path).list_gaps(campaign_id=campaign_id, limit=limit)
    return {"count": len(gaps), "gaps": [g.to_dict() for g in gaps]}


@router.get("/graph")
def graph_summary() -> dict[str, Any]:
    from axiom.skai.store import get_skai_store
    return get_skai_store(settings.db_path).graph_summary()


@router.post("/conflicts/detect")
def detect_conflicts() -> dict[str, Any]:
    from axiom.skai.conflicts import detect_conflicts as _detect
    from axiom.skai.store import get_skai_store

    conflicts = _detect(get_skai_store(settings.db_path))
    return {"count": len(conflicts), "conflicts": [c.to_dict() for c in conflicts]}


@router.post("/gaps/detect")
def detect_gaps(campaign_id: str | None = None) -> dict[str, Any]:
    from axiom.skai.gaps import detect_gaps as _detect
    from axiom.skai.store import get_skai_store

    gaps = _detect(get_skai_store(settings.db_path), campaign_id=campaign_id)
    return {"count": len(gaps), "gaps": [g.to_dict() for g in gaps]}


@router.post("/expand-question")
def expand_question(research_question: str) -> dict[str, Any]:
    from axiom.skai.expansion import expand_research_question

    expanded = expand_research_question(research_question)
    return {"research_question": research_question, "sub_questions": expanded}
