"""Pydantic models for the research workspace vertical slice."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ResearchProject(BaseModel):
    id: str
    name: str
    description: str = ""
    created_at: str
    updated_at: str
    last_session_at: Optional[str] = None
    document_count: int = 0
    note_count: int = 0


class ResearchDocument(BaseModel):
    id: str
    project_id: str
    filename: str
    text_content: str = ""
    summary: str = ""
    page_count: int = 0
    char_count: int = 0
    uploaded_at: str
    summarized_at: Optional[str] = None


class ResearchNote(BaseModel):
    id: str
    project_id: str
    document_id: Optional[str] = None
    title: str
    body: str
    tags: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str


class ResearchSession(BaseModel):
    id: str
    project_id: str
    started_at: str
    last_active_at: str
    active_document_id: Optional[str] = None
    active_conversation_id: Optional[str] = None
    context: dict = Field(default_factory=dict)


class ResearchMessage(BaseModel):
    id: str
    conversation_id: str
    role: str  # "user" | "assistant"
    content: str
    sources: List[str] = Field(default_factory=list)
    created_at: str


class ResearchConversation(BaseModel):
    id: str
    project_id: str
    title: str
    document_id: Optional[str] = None
    message_count: int = 0
    created_at: str
    updated_at: str


class ConversationDetail(BaseModel):
    conversation: ResearchConversation
    messages: List[ResearchMessage] = Field(default_factory=list)


class AskQuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    document_id: Optional[str] = None
    conversation_id: Optional[str] = None


class AskQuestionResponse(BaseModel):
    answer: str
    conversation_id: str
    message_id: str
    sources: List[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    result_type: str  # "document" | "note"
    id: str
    project_id: str
    title: str
    snippet: str
    score: float = 0.0


class ProjectDetail(BaseModel):
    project: ResearchProject
    documents: List[ResearchDocument] = Field(default_factory=list)
    notes: List[ResearchNote] = Field(default_factory=list)
    session: Optional[ResearchSession] = None
    conversations: List[ResearchConversation] = Field(default_factory=list)
    active_conversation: Optional[ConversationDetail] = None


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)


class CreateNoteRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    body: str = Field(default="", max_length=50000)
    document_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class UpdateNoteRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    body: Optional[str] = Field(default=None, max_length=50000)
    tags: Optional[List[str]] = None
