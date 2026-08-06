"""Pydantic models for the Golden Demo payload."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class DemoPaper(BaseModel):
    id: str
    title: str
    authors: str
    year: int
    filename: str
    pages: int
    summary: str
    key_findings: List[str] = Field(default_factory=list)
    status: Literal["queued", "reading", "extracted"] = "extracted"


class DemoKnowledgeNode(BaseModel):
    id: str
    label: str
    node_type: Literal["concept", "method", "finding", "gap", "contradiction"]
    description: str
    evidence_tier: Literal["supported", "speculative", "contradicted"] = "supported"
    source_papers: List[str] = Field(default_factory=list)


class DemoKnowledgeEdge(BaseModel):
    id: str
    source: str
    target: str
    relation: str
    strength: float = Field(ge=0.0, le=1.0)


class DemoNote(BaseModel):
    id: str
    title: str
    body: str
    tags: List[str] = Field(default_factory=list)
    linked_paper_id: Optional[str] = None


class DemoHypothesis(BaseModel):
    id: str
    statement: str
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
    status: Literal["proposed", "testing", "supported", "rejected"] = "proposed"
    experiment_id: Optional[str] = None


class DemoExperiment(BaseModel):
    id: str
    title: str
    objective: str
    method: str
    expected_outcome: str
    status: Literal["planned", "running", "complete"] = "planned"


class DemoTimelineEvent(BaseModel):
    id: str
    phase: str
    title: str
    description: str
    timestamp_offset_sec: int
    icon: str = "●"


class DemoContradiction(BaseModel):
    id: str
    claim_a: str
    claim_b: str
    source_a: str
    source_b: str
    resolution: str


class DemoGap(BaseModel):
    id: str
    area: str
    description: str
    priority: Literal["high", "medium", "low"] = "medium"


class DemoReportSection(BaseModel):
    heading: str
    content: str


class DemoResearchReport(BaseModel):
    title: str
    abstract: str
    sections: List[DemoReportSection] = Field(default_factory=list)
    generated_at: str
    illustrative_only: bool = True
    mode_notice: str = (
        "DEMO MODE — This report is a curated illustration for presentation purposes. "
        "It does not represent output from live AI models or verified scientific work."
    )


class DemoTourStep(BaseModel):
    id: str
    title: str
    body: str
    highlight: str
    duration_sec: int = 8


class DemoProject(BaseModel):
    id: str
    name: str
    description: str
    research_question: str
    created_at: str


class OperationModeInfo(BaseModel):
    """Embedded in every demo response so clients cannot confuse modes."""

    mode: Literal["demo"] = "demo"
    label: str = "Demo Mode"
    represents_scientific_capability: bool = False
    data_source: str = "curated"
    disclaimer: str
    suitable_for: List[str] = Field(default_factory=list)


class DemoState(BaseModel):
    version: str = "0.5-demo"
    operation_mode: OperationModeInfo
    project: DemoProject
    papers: List[DemoPaper]
    knowledge_nodes: List[DemoKnowledgeNode]
    knowledge_edges: List[DemoKnowledgeEdge]
    notes: List[DemoNote]
    contradictions: List[DemoContradiction]
    gaps: List[DemoGap]
    hypotheses: List[DemoHypothesis]
    experiments: List[DemoExperiment]
    timeline: List[DemoTimelineEvent]
    report: DemoResearchReport
    tour_steps: List[DemoTourStep]
    stats: dict = Field(default_factory=dict)
