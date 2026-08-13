import json
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    owner_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    
    owner = relationship("User", back_populates="projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    sessions = relationship("ResearchSession", back_populates="project", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)
    indexing_status = Column(String, default="pending", server_default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    
    project = relationship("Project", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    
    document = relationship("Document", back_populates="chunks")

class ResearchSession(Base):
    __tablename__ = "research_sessions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String, default="CREATED", nullable=False, index=True)
    goal = Column(Text, nullable=False, default="")
    max_steps = Column(Integer, default=10, nullable=False)
    max_tool_calls = Column(Integer, default=15, nullable=False)
    max_runtime_seconds = Column(Integer, default=120, nullable=False)
    step_count = Column(Integer, default=0, nullable=False)
    tool_call_count = Column(Integer, default=0, nullable=False)
    cancellation_requested = Column(Boolean, default=False, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    project = relationship("Project", back_populates="sessions")
    artifacts = relationship("ResearchArtifact", back_populates="session", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        kwargs.setdefault("status", "CREATED")
        kwargs.setdefault("max_steps", 10)
        kwargs.setdefault("max_tool_calls", 15)
        kwargs.setdefault("max_runtime_seconds", 120)
        kwargs.setdefault("step_count", 0)
        kwargs.setdefault("tool_call_count", 0)
        kwargs.setdefault("cancellation_requested", False)
        super().__init__(**kwargs)

class ResearchArtifact(Base):
    __tablename__ = "research_artifacts"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    type = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    
    session = relationship("ResearchSession", back_populates="artifacts")

    @property
    def json_content(self) -> dict:
        """Parse stringified JSON content into a dictionary."""
        try:
            val = json.loads(self.content)
            if isinstance(val, dict):
                return val
            return {"data": val}
        except Exception:
            return {"raw": self.content}
