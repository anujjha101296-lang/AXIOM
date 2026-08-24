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


class ExperimentDB(Base):
    __tablename__ = "experiments"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    hypothesis_id = Column(String, ForeignKey("hypotheses.id", ondelete="SET NULL"), nullable=True, index=True)
    prediction_id = Column(String, nullable=True)
    plan_id = Column(String, ForeignKey("verification_plans.id", ondelete="SET NULL"), nullable=True)
    name = Column(String, nullable=False)
    objective = Column(Text, nullable=False)
    code_body = Column(Text, nullable=False)
    method = Column(String, nullable=False, default="numerical_simulation")
    parameters_json = Column(Text, nullable=False, default="{}")
    resource_limits_json = Column(Text, nullable=False, default="{}")
    status = Column(String, nullable=False, default="PLANNED", index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class ExperimentRunDB(Base):
    __tablename__ = "experiment_runs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    experiment_id = Column(String, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    run_number = Column(Integer, nullable=False, default=1)
    status = Column(String, nullable=False, default="PLANNED")
    runtime_ms = Column(Float, nullable=False, default=0.0)
    memory_bytes = Column(Integer, nullable=False, default=0)
    stdout = Column(Text, nullable=False, default="")
    stderr = Column(Text, nullable=False, default="")
    result_data_json = Column(Text, nullable=False, default="{}")
    input_hash = Column(String, nullable=False, default="")
    spec_hash = Column(String, nullable=False, default="")
    seed = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class ExperimentObservationDB(Base):
    __tablename__ = "experiment_observations"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    experiment_id = Column(String, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    run_id = Column(String, ForeignKey("experiment_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    observation_level = Column(String, nullable=False, default="COMPUTATIONAL_OBSERVATION")
    summary = Column(Text, nullable=False)
    metrics_json = Column(Text, nullable=False, default="{}")
    reproducibility_status = Column(String, nullable=False, default="REPRODUCIBLE")
    interpretation_status = Column(String, nullable=False, default="SUPPORTED")
    is_mathematical_proof = Column(Boolean, nullable=False, default=False)
    limitations_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class ExperimentVerificationDB(Base):
    __tablename__ = "experiment_verifications"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    experiment_id = Column(String, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    run_id = Column(String, ForeignKey("experiment_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    verification_status = Column(String, nullable=False, default="VERIFIED")
    independent_method = Column(Text, nullable=False)
    independent_result = Column(Text, nullable=False)
    discrepancy = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class FormalTheoremDB(Base):
    __tablename__ = "formal_theorems"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_id = Column(String, ForeignKey("graph_claims.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String, nullable=False)
    natural_language = Column(Text, nullable=False)
    formal_statement = Column(Text, nullable=False)
    language = Column(String, nullable=False, default="LEAN4")
    status = Column(String, nullable=False, default="FORMALIZED", index=True)
    assumptions_json = Column(Text, nullable=False, default="[]")
    variables_json = Column(Text, nullable=False, default="[]")
    quantifiers_json = Column(Text, nullable=False, default="[]")
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class FormalProofDB(Base):
    __tablename__ = "formal_proofs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    theorem_id = Column(String, ForeignKey("formal_theorems.id", ondelete="CASCADE"), nullable=False, index=True)
    proof_script = Column(Text, nullable=False)
    verifier_output = Column(Text, nullable=False, default="")
    compiler_version = Column(String, nullable=False, default="Lean 4.7.0 / Z3 4.12.2")
    status = Column(String, nullable=False, default="PROOF_IN_PROGRESS")
    is_sorry_free = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class CounterexampleDB(Base):
    __tablename__ = "counterexamples"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    theorem_id = Column(String, ForeignKey("formal_theorems.id", ondelete="CASCADE"), nullable=False, index=True)
    domain = Column(String, nullable=False, default="Finite domain")
    assignment_json = Column(Text, nullable=False, default="{}")
    witness_summary = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class ProofArtifactDB(Base):
    __tablename__ = "proof_artifacts"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    theorem_id = Column(String, ForeignKey("formal_theorems.id", ondelete="CASCADE"), nullable=False, index=True)
    proof_id = Column(String, ForeignKey("formal_proofs.id", ondelete="CASCADE"), nullable=False, index=True)
    hash_id = Column(String, nullable=False, index=True)
    artifact_uri = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class ResearchProblemDB(Base):
    __tablename__ = "long_horizon_problems"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    formal_statement = Column(Text, nullable=False, default="")
    status = Column(String, nullable=False, default="PLANNED", index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class ResearchSubproblemDB(Base):
    __tablename__ = "long_horizon_subproblems"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    problem_id = Column(String, ForeignKey("long_horizon_problems.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    statement = Column(Text, nullable=False)
    dependencies_json = Column(Text, nullable=False, default="[]")
    status = Column(String, nullable=False, default="PLANNED", index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class ResearchTaskDB(Base):
    __tablename__ = "long_horizon_tasks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    subproblem_id = Column(String, ForeignKey("long_horizon_subproblems.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    strategy = Column(String, nullable=False, default="Decomposition")
    state = Column(String, nullable=False, default="PLANNED", index=True)
    budget_steps = Column(Integer, nullable=False, default=10)
    current_step = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class ResearchAttemptDB(Base):
    __tablename__ = "long_horizon_attempts"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, ForeignKey("long_horizon_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    approach_description = Column(Text, nullable=False)
    method = Column(String, nullable=False, default="Direct Proof")
    result_summary = Column(Text, nullable=False, default="")
    status = Column(String, nullable=False, default="PROMISING")
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class ResearchDecisionDB(Base):
    __tablename__ = "long_horizon_decisions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    problem_id = Column(String, ForeignKey("long_horizon_problems.id", ondelete="CASCADE"), nullable=False, index=True)
    decision_type = Column(String, nullable=False)
    rationale = Column(Text, nullable=False)
    critic_recommendation = Column(String, nullable=False, default="CONTINUE")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class ResearchMilestoneDB(Base):
    __tablename__ = "long_horizon_milestones"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    problem_id = Column(String, ForeignKey("long_horizon_problems.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    evidence_summary = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class ApproachMemoryDB(Base):
    __tablename__ = "approach_memories"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    problem_id = Column(String, ForeignKey("long_horizon_problems.id", ondelete="CASCADE"), nullable=False, index=True)
    approach_hash = Column(String, nullable=False, index=True)
    summary = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="FAILED")
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class ChallengeDB(Base):
    __tablename__ = "benchmark_challenges"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    version = Column(String, nullable=False, default="AXIOM-MATH-001", index=True)
    title = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    difficulty_level = Column(String, nullable=False, default="LEVEL_0_BASIC", index=True)
    statement = Column(Text, nullable=False)
    allowed_resources_json = Column(Text, nullable=False, default="[]")
    time_budget_sec = Column(Integer, nullable=False, default=300)
    tool_budget_steps = Column(Integer, nullable=False, default=20)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)


class EvaluationRunDB(Base):
    __tablename__ = "benchmark_evaluation_runs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    challenge_id = Column(String, ForeignKey("benchmark_challenges.id", ondelete="CASCADE"), nullable=False, index=True)
    outcome = Column(String, nullable=False, default="RESEARCH_PROGRESS", index=True)
    score_json = Column(Text, nullable=False, default="{}")
    failure_class = Column(String, nullable=False, default="NONE", index=True)
    runtime_sec = Column(Float, nullable=False, default=0.0)
    steps_used = Column(Integer, nullable=False, default=0)
    proof_verified = Column(Boolean, nullable=False, default=False)
    counterexample_found = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)


class ResearchMissionDB(Base):
    __tablename__ = "research_missions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    objective = Column(Text, nullable=False)
    state = Column(String, nullable=False, default="INITIALIZED", index=True)
    budget_json = Column(Text, nullable=False, default="{}")
    current_iteration = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class MissionCheckpointDB(Base):
    __tablename__ = "mission_checkpoints"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    mission_id = Column(String, ForeignKey("research_missions.id", ondelete="CASCADE"), nullable=False, index=True)
    iteration = Column(Integer, nullable=False)
    checkpoint_hash = Column(String, nullable=False, index=True)
    summary = Column(Text, nullable=False)
    state_snapshot_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)


class MissionTaskDB(Base):
    __tablename__ = "mission_tasks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    mission_id = Column(String, ForeignKey("research_missions.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    assigned_role = Column(String, nullable=False, default="Mathematician")
    state = Column(String, nullable=False, default="PLANNED", index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
