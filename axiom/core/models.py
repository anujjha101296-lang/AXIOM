import json
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum, Integer, Boolean, Float
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
    embedding = Column(Text, nullable=True)          # JSON float array
    chunk_index = Column(Integer, nullable=False, default=0)
    char_start = Column(Integer, nullable=True)
    char_end = Column(Integer, nullable=True)
    embedding_dim = Column(Integer, nullable=True)   # dimension of stored vector
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


class GraphEntityDB(Base):
    __tablename__ = "graph_entities"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False, default="concept")
    domain = Column(String, nullable=False, default="general")
    description = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class GraphEntityAliasDB(Base):
    __tablename__ = "graph_entity_aliases"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    entity_id = Column(String, ForeignKey("graph_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    alias = Column(String, nullable=False, index=True)
    source_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class GraphClaimDB(Base):
    __tablename__ = "graph_claims"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_text = Column(Text, nullable=False)
    claim_type = Column(String, nullable=False, default="FACTUAL")
    epistemic_status = Column(String, nullable=False, default="EXTRACTED")
    confidence_score = Column(Float, nullable=False, default=1.0)
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class GraphClaimEvidenceDB(Base):
    __tablename__ = "graph_claim_evidences"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    claim_id = Column(String, ForeignKey("graph_claims.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(String, ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)
    source_id = Column(String, nullable=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    supports = Column(Boolean, nullable=False, default=True)
    snippet = Column(Text, nullable=False, default="")
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class GraphRelationshipDB(Base):
    __tablename__ = "graph_relationships"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_entity_id = Column(String, ForeignKey("graph_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    object_entity_id = Column(String, ForeignKey("graph_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    predicate = Column(String, nullable=False, default="RELATED_TO")
    status = Column(String, nullable=False, default="EXTRACTED")
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class GraphRelationshipEvidenceDB(Base):
    __tablename__ = "graph_relationship_evidences"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    relationship_id = Column(String, ForeignKey("graph_relationships.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(String, ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)
    source_id = Column(String, nullable=True)
    snippet = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class GraphContradictionDB(Base):
    __tablename__ = "graph_contradictions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_a_id = Column(String, ForeignKey("graph_claims.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_b_id = Column(String, ForeignKey("graph_claims.id", ondelete="CASCADE"), nullable=False, index=True)
    contradiction_type = Column(String, nullable=False, default="DIRECT")
    reasoning = Column(Text, nullable=False, default="")
    resolved = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class GraphResearchGapDB(Base):
    __tablename__ = "graph_research_gaps"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    gap_type = Column(String, nullable=False, default="NO_EVIDENCE")
    description = Column(Text, nullable=False)
    severity = Column(String, nullable=False, default="MEDIUM")
    target_entity_id = Column(String, nullable=True)
    target_claim_id = Column(String, nullable=True)
    target_question_id = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class HypothesisDB(Base):
    __tablename__ = "hypotheses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    question_id = Column(String, nullable=True)
    gap_id = Column(String, nullable=True)
    claim = Column(Text, nullable=False)
    motivation = Column(Text, nullable=False, default="")
    assumptions_json = Column(Text, nullable=False, default="[]")
    verification_strategy = Column(Text, nullable=False, default="")
    status = Column(String, nullable=False, default="PROPOSED", index=True)
    confidence_score = Column(Float, nullable=False, default=0.5)
    rationale = Column(Text, nullable=False, default="")
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class HypothesisEvidenceDB(Base):
    __tablename__ = "hypothesis_evidences"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    hypothesis_id = Column(String, ForeignKey("hypotheses.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_id = Column(String, nullable=True)
    chunk_id = Column(String, ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)
    source_id = Column(String, nullable=True)
    supports = Column(Boolean, nullable=False, default=True)
    snippet = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class HypothesisPredictionDB(Base):
    __tablename__ = "hypothesis_predictions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    hypothesis_id = Column(String, ForeignKey("hypotheses.id", ondelete="CASCADE"), nullable=False, index=True)
    prediction_text = Column(Text, nullable=False)
    expected_observation = Column(Text, nullable=False)
    conditions = Column(Text, nullable=False, default="")
    measurement = Column(Text, nullable=False, default="")
    falsifying_observation = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class HypothesisCritiqueDB(Base):
    __tablename__ = "hypothesis_critiques"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    hypothesis_id = Column(String, ForeignKey("hypotheses.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String, nullable=False, default="VALID")
    critique_text = Column(Text, nullable=False)
    unsupported_assumptions_json = Column(Text, nullable=False, default="[]")
    scope_errors_json = Column(Text, nullable=False, default="[]")
    is_falsifiable = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class HypothesisRevisionDB(Base):
    __tablename__ = "hypothesis_revisions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    hypothesis_id = Column(String, ForeignKey("hypotheses.id", ondelete="CASCADE"), nullable=False, index=True)
    revision_index = Column(Integer, nullable=False, default=1)
    previous_claim = Column(Text, nullable=False)
    new_claim = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class VerificationPlanDB(Base):
    __tablename__ = "verification_plans"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    hypothesis_id = Column(String, ForeignKey("hypotheses.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    hypothesis_summary = Column(Text, nullable=False)
    required_evidence_json = Column(Text, nullable=False, default="[]")
    predictions_json = Column(Text, nullable=False, default="[]")
    method = Column(String, nullable=False, default="literature_research")
    data_sources_json = Column(Text, nullable=False, default="[]")
    success_criteria = Column(Text, nullable=False, default="")
    failure_criteria = Column(Text, nullable=False, default="")
    limitations_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
