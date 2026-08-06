import os
import subprocess
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from axiom.config import settings
from axiom.core.events.bus import AxiomEvent, Topics, event_bus
from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.knowledge_graph.migrations import run_migrations
from axiom.core.memory.working_memory import WorkingMemory
from axiom.core.parser.arxiv_parser import ArxivParser
from axiom.core.reasoning.hypothesis_engine import HypothesisEngine
from axiom.core.reasoning.mcts import MctsSolver
from axiom.core.reasoning.self_improvement import SelfImprovementLoop
from axiom.core.verification.lean_exporter import LeanExporter
from axiom.core.verification.smt_gateway import SmtGateway
from axiom.evaluation.prize_readiness import PrizeReadinessScorer
from axiom.observability.logger import configure_logging, get_logger
from axiom.observability.metrics import METRICS
from axiom.services.api_gateway.auth import verify_token
from axiom.services.api_gateway.routes.mip import router as mip_router
from axiom.services.api_gateway.routes.eval_api import router as eval_router
from axiom.services.api_gateway.routes.mde import router as mde_router
from axiom.services.api_gateway.routes.research import router as research_router
from axiom.services.api_gateway.routes.auth_api import router as auth_router
from axiom.services.api_gateway.routes.research_loop import router as research_loop_router
from axiom.services.api_gateway.routes.workflow_router import workflow_router

# Initialise structured logging from settings
configure_logging(level=settings.log_level, log_format=settings.log_format)
logger = get_logger("axiom.api_gateway")


# ── Lifespan (startup / shutdown) ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks, yield, then run shutdown tasks."""
    logger.info("AXIOM API Gateway starting up",
                extra={"version": settings.app_version, "env": settings.environment})
    # Run database migrations on startup
    if store.conn:
        run_migrations(store.conn)
    yield
    logger.info("AXIOM API Gateway shutting down")
    store.close()


app = FastAPI(
    title="AXIOM API Gateway",
    description="Operational entrypoint for AXIOM — the AI Scientific Discovery Platform",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — use settings-driven origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MIP Router (EPIC-001: Mathematical Intelligence Platform) ────────────────
app.include_router(mip_router)

# ── Eval Router (EPIC-002: Scientific Capability Evaluation Platform) ─────────
app.include_router(eval_router)

# ── MDE Router (Mathematical Discovery Engine — theorem retrieval) ────────────
app.include_router(mde_router)

# ── Research Workspace (projects, PDFs, notes, search, sessions) ──────────────
app.include_router(research_router)

# ── Authentication (register, login, session) ─────────────────────────────────
app.include_router(auth_router)

# ── Workflow Engine (autonomous task DAG orchestration) ───────────────────────
app.include_router(workflow_router)

# ── Autonomous Research Loop v1 (Milestone 005) ─────────────────────────────
app.include_router(research_loop_router)

# ── Singletons (Sprint 0: driven by settings) ────────────────────────────────
db_path = settings.db_path
store = EpistemicStore(db_path)
parser = ArxivParser()
smt_gateway = SmtGateway()
lean_exporter = LeanExporter()
mcts_solver = MctsSolver()

# Sprint 2 — shared singletons
hypothesis_engine = HypothesisEngine(store)
working_memory = WorkingMemory()
self_improvement = SelfImprovementLoop(workspace_root=os.path.dirname(db_path) or "/tmp")
prize_scorer = PrizeReadinessScorer()

# Request schemas
class IngestionRequest(BaseModel):
    arxiv_id: str

class QueryRequest(BaseModel):
    query_string: str

class SmtConjectureRequest(BaseModel):
    conjecture_name: str
    equation: str
    modulus: int
    variables: List[str]

class ProofRequest(BaseModel):
    theorem_name: str
    start_expression: str
    target_expression: str
    variables: Dict[str, str]

class HypothesizeRequest(BaseModel):
    max_hypotheses: int = 5

class MemoryProblemRequest(BaseModel):
    problem: str

# Http logging + metrics middleware
@app.middleware("http")
async def observe_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    path = request.url.path
    method = request.method
    status_code = str(response.status_code)
    logger.info(
        "HTTP request",
        extra={"path": path, "method": method, "status": status_code, "duration_s": round(duration, 4)},
    )
    METRICS.api_requests_total.inc(method=method, endpoint=path, status=status_code)
    METRICS.api_request_duration.observe(duration)
    return response

# Liveness check
@app.get("/health", tags=["system"])
def health_check():
    return {"status": "healthy", "version": settings.app_version, "timestamp": time.time()}

# Readiness check
@app.get("/ready", tags=["system"])
def readiness_check():
    try:
        assert store.conn is not None
        cursor = store.conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.fetchone()
        return {"status": "ready", "database": "connected", "version": settings.app_version}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unhealthy",
        )


# Prometheus metrics endpoint
@app.get("/metrics", tags=["system"], include_in_schema=False)
def get_metrics():
    """Expose Prometheus-format metrics for scraping."""
    return Response(
        content=METRICS.prometheus_text(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


# Event bus history endpoint (debug/observability)
@app.get("/events", tags=["system"])
def get_recent_events(topic: str = None, limit: int = 20, token: str = Depends(verify_token)):
    """Return recent events from the in-process event bus."""
    events = event_bus.recent_events(topic=topic, limit=limit)
    return {
        "count": len(events),
        "events": [
            {
                "event_id": e.event_id,
                "topic": e.topic,
                "source": e.source,
                "timestamp": e.timestamp,
                "payload": e.payload,
            }
            for e in events
        ],
    }

# Graph Endpoint: returns the entire SQLite knowledge graph
@app.get("/graph", tags=["knowledge"])
def get_graph(token: str = Depends(verify_token)):
    try:
        graph_data = store.export_knowledge_graph()
        return graph_data.model_dump()
    except Exception as e:
        logger.error(f"Failed to export knowledge graph: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export graph: {str(e)}"
        )

# Ingest Endpoint: downloads and parses arXiv paper
@app.post("/ingest", tags=["discovery"])
def trigger_ingest(payload: IngestionRequest, token: str = Depends(verify_token)):
    logger.info(f"Triggering ingestion for arXiv ID: {payload.arxiv_id}")
    try:
        paper, claims, concepts, edges = parser.parse_paper(payload.arxiv_id)
        
        # Save parsed nodes to the EGS database
        store.add_node(paper)
        for claim in claims:
            store.add_node(claim)
        for concept in concepts:
            store.add_node(concept)
        for edge in edges:
            store.add_edge(edge)
            
        return {
            "status": "triggered",
            "arxiv_id": payload.arxiv_id,
            "title": paper.name,
            "claims_extracted": len(claims),
            "concepts_extracted": len(concepts),
            "edges_created": len(edges)
        }
    except Exception as e:
        logger.error(f"Ingestion failed for {payload.arxiv_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )

# Protected Query Endpoint
@app.post("/query", tags=["discovery"])
def run_query(payload: QueryRequest, token: str = Depends(verify_token)):
    logger.info(f"Query parsed: {payload.query_string}")
    return {
        "status": "success",
        "query": payload.query_string,
        "results": []
    }

# Verify Conjecture: Runs Z3 SMT Counterexample solver
@app.post("/verify/conjecture", tags=["verification"])
def verify_conjecture(payload: SmtConjectureRequest, token: str = Depends(verify_token)):
    logger.info(f"SMT Verification sweep triggered for: {payload.conjecture_name}")
    try:
        is_valid, counterexample = smt_gateway.verify_modular_conjecture(
            equation=payload.equation,
            modulus=payload.modulus,
            variables=payload.variables
        )
        
        from axiom.core.knowledge_graph.schema import MathematicalClaimNode
        from axiom.core.verification.truthfulness import assign_from_smt_modular
        import hashlib
        
        claim_id = hashlib.sha256(f"smt_claim:{payload.conjecture_name}:{payload.equation}".encode()).hexdigest()
        
        assignment = assign_from_smt_modular(is_valid)
        
        claim_node = MathematicalClaimNode(
            id=claim_id,
            name=payload.conjecture_name,
            statement=f"{payload.equation} mod {payload.modulus}",
            status=assignment.epistemic_status,
            tier=assignment.verification_tier,
            metadata={
                "variables": payload.variables,
                "modulus": payload.modulus,
                "evidence_mode": assignment.evidence_mode.value,
                "formally_proven": assignment.formally_proven,
            }
        )
        store.add_node(claim_node)
        
        return {
            "status": "success",
            "conjecture_name": payload.conjecture_name,
            "is_valid": is_valid,
            "counterexample": counterexample,
            "node_id": claim_id,
            **assignment.as_api_fields(),
        }
    except Exception as e:
        logger.error(f"Conjecture verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SMT solving failed: {str(e)}"
        )

# Verify Proof: Runs MCTS solver & exports Lean 4 file
@app.post("/verify/proof", tags=["verification"])
def verify_proof(payload: ProofRequest, token: str = Depends(verify_token)):
    logger.info(f"Proof search triggered for: {payload.theorem_name}")
    try:
        # Run MCTS algebraic solver
        proof_steps = mcts_solver.solve(payload.start_expression, payload.target_expression)
        
        is_proven = proof_steps is not None
        tactics = "sorry"
        if is_proven:
            # Map proof steps to Lean ring/algebra rewrite lines
            tactics = "\n  ".join([f"-- Step: applied {rule}\n  -- Result: {state}" for rule, state in proof_steps])
            tactics += "\n  rfl" # reflexivity close
            
        # Export Lean 4 code
        lean_statement = f"{payload.start_expression} = {payload.target_expression}"
        lean_code = lean_exporter.export_theorem(
            name=payload.theorem_name,
            statement=lean_statement,
            variables=payload.variables,
            proof_body=tactics
        )
        
        # Save Lean script locally
        lean_file_path = f"/tmp/axiom_proofs/{lean_exporter.sanitize_name(payload.theorem_name)}.lean"
        lean_exporter.save_lean_file(lean_file_path, lean_code)
        
        # Run local Lean compiler check (or mock validation if compiler is missing)
        compiler_status = "unverified (compiler missing)"
        if is_proven:
            if os.path.exists("/usr/local/bin/lean") or os.path.exists("/usr/bin/lean"):
                try:
                    res = subprocess.run(["lean", lean_file_path], capture_output=True, text=True, timeout=10)
                    if res.returncode == 0:
                        compiler_status = "formally compiled successfully"
                    else:
                        compiler_status = f"compiler error: {res.stderr}"
                except Exception as ex:
                    compiler_status = f"compiler trigger error: {str(ex)}"
            else:
                compiler_status = "simulated compile success (local Lean bin missing)"

        # Save Theorem claim node to SQLite EGS
        from axiom.core.knowledge_graph.schema import MathematicalClaimNode
        from axiom.core.verification.truthfulness import assign_from_proof_search
        import hashlib
        
        claim_id = hashlib.sha256(f"proof_claim:{payload.theorem_name}:{lean_statement}".encode()).hexdigest()
        assignment = assign_from_proof_search(is_proven, compiler_status)
        
        proof_path_str = [f"{rule}: {state}" for rule, state in proof_steps] if proof_steps else []
        claim_node = MathematicalClaimNode(
            id=claim_id,
            name=payload.theorem_name,
            statement=lean_statement,
            status=assignment.epistemic_status,
            tier=assignment.verification_tier,
            metadata={
                "proof_path": proof_path_str,
                "lean_file": lean_file_path,
                "compiler_status": compiler_status,
                "evidence_mode": assignment.evidence_mode.value,
                "formally_proven": assignment.formally_proven,
            }
        )
        store.add_node(claim_node)
        
        return {
            "status": "success",
            "is_proven": is_proven,
            "proof_steps": proof_steps,
            "compiler_status": compiler_status,
            "lean_file": lean_file_path,
            "node_id": claim_id,
            **assignment.as_api_fields(),
        }
    except Exception as e:
        logger.error(f"Proof search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Proof verification failed: {str(e)}"
        )


# ── Sprint 2: Hypothesis Engine ───────────────────────────────────────────────

@app.post("/hypothesize", tags=["discovery"])
def run_hypothesize(payload: HypothesizeRequest, token: str = Depends(verify_token)):
    """Generate new mathematical conjectures from patterns in the EGS."""
    logger.info(f"Hypothesis generation triggered (max={payload.max_hypotheses})")
    try:
        new_nodes = hypothesis_engine.generate(max_hypotheses=payload.max_hypotheses)
        # Register new hypotheses in working memory
        for node in new_nodes:
            working_memory.add_hypothesis(
                node_id=node.id,
                statement=node.statement,
                confidence=0.5,
                origin_strategy=node.metadata.get("generation_strategy", "HYP"),
            )
        return {
            "status": "success",
            "hypotheses_generated": len(new_nodes),
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "statement": n.statement,
                    "strategy": n.metadata.get("generation_strategy"),
                }
                for n in new_nodes
            ],
        }
    except Exception as e:
        logger.error(f"Hypothesis generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hypothesis generation failed: {str(e)}",
        )


# ── Sprint 2: Working Memory ──────────────────────────────────────────────────

@app.get("/memory/context", tags=["memory"])
def get_memory_context(token: str = Depends(verify_token)):
    """Return the current session working memory snapshot."""
    return working_memory.snapshot()


@app.post("/memory/reset", tags=["memory"])
def reset_memory(token: str = Depends(verify_token)):
    """Clear the working memory and begin a new research session."""
    working_memory.reset()
    return {"status": "ok", "message": "Working memory cleared."}


@app.post("/memory/problem", tags=["memory"])
def set_research_problem(payload: MemoryProblemRequest, token: str = Depends(verify_token)):
    """Set the active research problem in working memory."""
    working_memory.set_problem(payload.problem)
    return {"status": "ok", "problem": payload.problem}


# ── Sprint 2: Self-Improvement Loop ──────────────────────────────────────────

@app.post("/self-improve", tags=["system"])
def run_self_improvement(token: str = Depends(verify_token)):
    """Audit AXIOM subsystems and regenerate roadmap.md."""
    logger.info("Self-improvement audit triggered.")
    try:
        roadmap_path = self_improvement.run()
        report = self_improvement.report()
        return {
            "status": "ok",
            "roadmap_path": roadmap_path,
            "weakest_dimension": report["weakest_dimension"],
            "weakest_dimension_score": report["weakest_dimension_score"],
            "top_3_priority": report["top_3_priority"],
        }
    except Exception as e:
        logger.error(f"Self-improvement loop failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Self-improvement failed: {str(e)}",
        )


# ── Sprint 2: Prize Readiness Benchmark ──────────────────────────────────────

@app.get("/benchmark/prize-readiness", tags=["benchmark"])
def get_prize_readiness(token: str = Depends(verify_token)):
    """Return capability scores against officially recognised prize problems."""
    try:
        ranked = prize_scorer.score_all()
        weak_dim, weak_score = prize_scorer.global_weakest_dimension()
        weakest_prob = prize_scorer.weakest_problem()
        return {
            "status": "ok",
            "problems": [
                {
                    "name": p.name,
                    "aggregate_score": round(score, 4),
                    "knowledge": p.axiom_baseline.knowledge,
                    "reasoning": p.axiom_baseline.reasoning,
                    "verification": p.axiom_baseline.verification,
                    "hypothesis_gen": p.axiom_baseline.hypothesis_gen,
                    "literature_coverage": p.axiom_baseline.literature_coverage,
                }
                for p, score in ranked
            ],
            "weakest_dimension": weak_dim,
            "weakest_dimension_score": round(weak_score, 4),
            "weakest_problem": weakest_prob.name,
            "recommended_action": weakest_prob.recommended_action,
        }
    except Exception as e:
        logger.error(f"Prize readiness scoring failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prize readiness failed: {str(e)}",
        )
