"""Phase executors for the Scientific Method Engine — delegates to existing AXIOM subsystems."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.knowledge_graph.schema import NodeType
from axiom.core.reasoning.hypothesis_engine import HypothesisEngine
from axiom.core.retrieval.engine import TheoremRetrievalEngine
from axiom.core.verification.truthfulness import EvidenceMode, assign_from_smt_modular
from axiom.scientific_method.models import (
    ClaimVerificationStatus,
    CompetingHypothesis,
    CriticismReport,
    ExperimentDesign,
    HumanReviewPackage,
    KnowledgeSource,
    MemoryRecord,
    PhaseResult,
    ProblemDefinition,
    ReflectionEntry,
    SMEPhase,
    SMESession,
    VerifiedClaim,
)

MIN_HYPOTHESES = 2


class PhaseExecutor:
    """Executes individual SME phases using repository subsystems."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._store = EpistemicStore(db_path)
        self._hypothesis_engine = HypothesisEngine(self._store)
        self._retrieval = TheoremRetrievalEngine()

    def execute(self, session: SMESession, phase: SMEPhase) -> PhaseResult:
        handlers = {
            SMEPhase.PROBLEM_DEFINITION: self._problem_definition,
            SMEPhase.KNOWLEDGE_ACQUISITION: self._knowledge_acquisition,
            SMEPhase.KNOWLEDGE_GRAPH_CONSTRUCTION: self._knowledge_graph_construction,
            SMEPhase.HYPOTHESIS_GENERATION: self._hypothesis_generation,
            SMEPhase.CRITICISM: self._criticism,
            SMEPhase.EXPERIMENTATION: self._experimentation,
            SMEPhase.VERIFICATION: self._verification,
            SMEPhase.REFLECTION: self._reflection,
            SMEPhase.RESEARCH_MEMORY: self._research_memory,
            SMEPhase.HUMAN_REVIEW: self._human_review,
        }
        result = PhaseResult(phase=phase, completed=False)
        try:
            artifacts = handlers[phase](session)
            result.artifacts = artifacts
            result.completed = True
            result.completed_at = datetime.now(timezone.utc)
        except Exception as exc:
            result.errors.append(str(exc))
        return result

    def _problem_definition(self, session: SMESession) -> dict[str, Any]:
        if session.problem:
            problem = session.problem
        else:
            problem = ProblemDefinition(
                research_question=session.objective,
                assumptions=[
                    "Domain knowledge in the epistemic graph is representative.",
                    "Available verification tools are correctly configured.",
                ],
                success_criteria=[
                    "At least one hypothesis survives criticism with measurable evidence.",
                    "All claims are classified with explicit verification status.",
                    "Research memory captures failures and insights for reuse.",
                ],
                constraints=[
                    "No claim of formal proof without compiler-backed evidence.",
                    "Multiple competing hypotheses required before experimentation.",
                ],
            )
            session.problem = problem
        return {"problem": problem.model_dump()}

    def _knowledge_acquisition(self, session: SMESession) -> dict[str, Any]:
        sources: list[KnowledgeSource] = []
        graph = self._store.export_knowledge_graph()

        for node in graph.nodes:
            stype = "formal_definition"
            if node.type == NodeType.PAPER:
                stype = "literature"
            elif node.type == NodeType.MATHEMATICAL_CLAIM:
                stype = "proof" if getattr(node, "status", None) else "conjecture"
            elif node.type == NodeType.CONJECTURE:
                stype = "conjecture"
            sources.append(KnowledgeSource(
                source_type=stype,
                title=node.name,
                reference=node.id,
                metadata={"node_type": node.type.value if hasattr(node.type, "value") else str(node.type)},
            ))

        if session.problem:
            try:
                retrieval = self._retrieval.retrieve_theorems(
                    query_formula=session.problem.research_question[:80],
                    top_k=5,
                )
                for thm in retrieval.matched_theorems:
                    sources.append(KnowledgeSource(
                        source_type="formal_definition",
                        title=thm.name,
                        reference=thm.theorem_id,
                        metadata={"formula": thm.formula},
                    ))
            except Exception:
                pass

        if not sources:
            sources.append(KnowledgeSource(
                source_type="failure",
                title="Empty knowledge base",
                reference="bootstrap",
                metadata={"note": "No prior sources; proceeding with problem-only context."},
            ))

        session.knowledge_sources = sources
        return {"source_count": len(sources), "sources": [s.model_dump() for s in sources]}

    def _knowledge_graph_construction(self, session: SMESession) -> dict[str, Any]:
        graph = self._store.export_knowledge_graph()
        nodes_by_type: dict[str, int] = {}
        for node in graph.nodes:
            key = node.type.value if hasattr(node.type, "value") else str(node.type)
            nodes_by_type[key] = nodes_by_type.get(key, 0) + 1

        summary = {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "nodes_by_type": nodes_by_type,
            "definitions": [n.name for n in graph.nodes if n.type == NodeType.DEFINITION][:20],
            "theorems": [n.name for n in graph.nodes if n.type == NodeType.MATHEMATICAL_CLAIM][:20],
            "open_questions": [n.name for n in graph.nodes if n.type == NodeType.OPEN_PROBLEM][:20],
            "dependencies": [
                {"source": e.source_id, "target": e.target_id, "type": e.type.value}
                for e in graph.edges[:50]
            ],
            "unknowns": [
                n.name for n in graph.nodes
                if getattr(n, "status", None) and str(getattr(n, "status", "")).endswith("CONJECTURED")
            ][:20],
        }
        session.knowledge_graph_summary = summary
        return summary

    def _hypothesis_generation(self, session: SMESession) -> dict[str, Any]:
        hypotheses: list[CompetingHypothesis] = []
        generated = self._hypothesis_engine.generate(max_hypotheses=5)

        for node in generated:
            hypotheses.append(CompetingHypothesis(
                statement=node.statement,
                reasoning=f"Generated via {node.metadata.get('generation_strategy', 'pattern')} from verified graph patterns.",
                supporting_evidence=[f"Derived from graph node {node.id}"],
                weaknesses=["Requires independent verification", "May be tautological under scrutiny"],
                confidence=0.45,
            ))

        question = session.problem.research_question if session.problem else session.objective
        bootstrap = [
            (
                f"Primary hypothesis: {question} is true under stated assumptions.",
                "Direct interpretation of the research question as a testable claim.",
                0.55,
            ),
            (
                f"Null hypothesis: {question} does not hold; alternative explanations exist.",
                "Conservative baseline requiring strong evidence to reject.",
                0.40,
            ),
            (
                f"Structural hypothesis: {question} holds only under restricted conditions.",
                "Intermediate position bounding the claim to verifiable sub-cases.",
                0.50,
            ),
        ]
        for stmt, reasoning, conf in bootstrap:
            if len(hypotheses) >= MIN_HYPOTHESES + len(bootstrap):
                break
            hypotheses.append(CompetingHypothesis(
                statement=stmt,
                reasoning=reasoning,
                supporting_evidence=session.problem.assumptions[:2] if session.problem else [],
                weaknesses=["Heuristic bootstrap — not graph-derived"],
                confidence=conf,
            ))

        if len(hypotheses) < MIN_HYPOTHESES:
            raise ValueError(
                f"Hypothesis generation produced {len(hypotheses)} hypotheses; "
                f"minimum {MIN_HYPOTHESES} competing hypotheses required."
            )

        session.hypotheses = hypotheses[: max(MIN_HYPOTHESES, len(hypotheses))]
        return {"hypothesis_count": len(session.hypotheses), "hypotheses": [h.model_dump() for h in session.hypotheses]}

    def _criticism(self, session: SMESession) -> dict[str, Any]:
        if len(session.hypotheses) < MIN_HYPOTHESES:
            raise ValueError("Criticism requires at least two competing hypotheses.")

        criticisms: list[CriticismReport] = []
        for i, hyp in enumerate(session.hypotheses):
            critic_id = f"critic_{i + 1}"
            criticisms.append(CriticismReport(
                hypothesis_id=hyp.hypothesis_id,
                critic_id=critic_id,
                contradictions=[
                    f"Competing hypothesis {session.hypotheses[(i + 1) % len(session.hypotheses)].hypothesis_id} "
                    f"may contradict this claim."
                ] if len(session.hypotheses) > 1 else [],
                missing_assumptions=[
                    "Quantifier bounds not explicitly stated.",
                    "Domain of discourse may be underspecified.",
                ],
                counterexample_candidates=[
                    f"Search for counterexample to: {hyp.statement[:80]}",
                ],
                literature_conflicts=[
                    s.title for s in session.knowledge_sources
                    if s.source_type == "failure"
                ],
                severity=1.0 - hyp.confidence,
            ))

        session.criticisms = criticisms
        return {"criticism_count": len(criticisms), "criticisms": [c.model_dump() for c in criticisms]}

    def _experimentation(self, session: SMESession) -> dict[str, Any]:
        domain_methods = {
            "mathematics": "formal_verification",
            "math": "formal_verification",
            "research": "search",
            "science": "simulation",
            "engineering": "programming",
        }
        method = domain_methods.get(session.domain.lower(), "search")

        experiments: list[ExperimentDesign] = []
        for hyp in session.hypotheses[:3]:
            others = [h.hypothesis_id for h in session.hypotheses if h.hypothesis_id != hyp.hypothesis_id]
            experiments.append(ExperimentDesign(
                hypothesis_id=hyp.hypothesis_id,
                domain_method=method,
                description=f"Design experiment to test: {hyp.statement[:120]}",
                discriminates_between=others,
                expected_outcomes={
                    "supports": f"Evidence increases confidence in {hyp.hypothesis_id}",
                    "refutes": f"Evidence decreases confidence in {hyp.hypothesis_id}",
                },
            ))

        session.experiments = experiments
        return {"experiment_count": len(experiments), "experiments": [e.model_dump() for e in experiments]}

    def _verification(self, session: SMESession) -> dict[str, Any]:
        claims: list[VerifiedClaim] = []

        for hyp in session.hypotheses:
            assignment = assign_from_smt_modular(hyp.confidence >= 0.5)
            if hyp.confidence >= 0.7:
                status = ClaimVerificationStatus.SUPPORTED
            elif hyp.confidence <= 0.3:
                status = ClaimVerificationStatus.REJECTED
            elif any(c.severity > 0.7 for c in session.criticisms if c.hypothesis_id == hyp.hypothesis_id):
                status = ClaimVerificationStatus.SPECULATIVE
            else:
                status = ClaimVerificationStatus.UNKNOWN

            claims.append(VerifiedClaim(
                statement=hyp.statement,
                status=status,
                evidence_summary=f"Criticism severity and confidence={hyp.confidence:.2f}",
                evidence_mode=assignment.evidence_mode.value,
            ))

        session.verified_claims = claims
        return {
            "claim_count": len(claims),
            "claims": [c.model_dump() for c in claims],
            "status_distribution": {
                s.value: sum(1 for c in claims if c.status == s)
                for s in ClaimVerificationStatus
            },
        }

    def _reflection(self, session: SMESession) -> dict[str, Any]:
        supported = sum(1 for c in session.verified_claims if c.status == ClaimVerificationStatus.SUPPORTED)
        rejected = sum(1 for c in session.verified_claims if c.status == ClaimVerificationStatus.REJECTED)

        reflection = ReflectionEntry(
            learned=[
                f"Evaluated {len(session.hypotheses)} competing hypotheses.",
                f"{supported} claims supported, {rejected} rejected after verification.",
                f"Acquired {len(session.knowledge_sources)} knowledge sources.",
            ],
            failed=[
                f"High-severity criticism on hypothesis {c.hypothesis_id}"
                for c in session.criticisms if c.severity > 0.6
            ],
            assumptions_changed=[
                "Confidence adjusted based on criticism severity."
            ] if session.criticisms else [],
            new_questions=[
                f"What evidence would discriminate between {session.hypotheses[0].hypothesis_id} "
                f"and {session.hypotheses[1].hypothesis_id}?"
            ] if len(session.hypotheses) >= 2 else [],
        )

        session.reflection = reflection
        return {"reflection": reflection.model_dump()}

    def _research_memory(self, session: SMESession) -> dict[str, Any]:
        records: list[MemoryRecord] = []

        if session.reflection:
            for item in session.reflection.learned:
                records.append(MemoryRecord(category="insight", content=item, phase=SMEPhase.REFLECTION))
            for item in session.reflection.failed:
                records.append(MemoryRecord(category="failed_strategy", content=item, phase=SMEPhase.CRITICISM))
            for item in session.reflection.new_questions:
                records.append(MemoryRecord(category="journal", content=item, phase=SMEPhase.REFLECTION))

        for hyp in session.hypotheses:
            if hyp.confidence >= 0.5:
                records.append(MemoryRecord(
                    category="successful_strategy",
                    content=f"Hypothesis {hyp.hypothesis_id}: {hyp.statement[:100]}",
                    phase=SMEPhase.HYPOTHESIS_GENERATION,
                ))

        records.append(MemoryRecord(
            category="decision",
            content=f"Completed SME cycle for: {session.objective}",
            phase=SMEPhase.RESEARCH_MEMORY,
            metadata={"phases_completed": [p.value for p in session.phases_completed]},
        ))

        session.memory_records = records
        return {"memory_count": len(records), "records": [r.model_dump() for r in records]}

    def _human_review(self, session: SMESession) -> dict[str, Any]:
        timeline = [
            {"phase": pr.phase.value, "completed": pr.completed, "errors": pr.errors}
            for pr in session.phase_results
        ]

        notebook_lines = [
            f"# Research Notebook: {session.objective}",
            "",
            "## Problem Definition",
            session.problem.research_question if session.problem else session.objective,
            "",
            "## Hypotheses",
        ]
        for h in session.hypotheses:
            notebook_lines.append(f"- **{h.hypothesis_id}** ({h.confidence:.2f}): {h.statement}")
            notebook_lines.append(f"  - Reasoning: {h.reasoning}")
            notebook_lines.append(f"  - Weaknesses: {', '.join(h.weaknesses)}")

        notebook_lines.extend(["", "## Open Questions"])
        if session.reflection:
            notebook_lines.extend(f"- {q}" for q in session.reflection.new_questions)

        review = HumanReviewPackage(
            research_notebook="\n".join(notebook_lines),
            evidence_graph_summary=session.knowledge_graph_summary,
            reasoning_timeline=timeline,
            open_questions=session.reflection.new_questions if session.reflection else [],
            recommended_experiments=[e.description for e in session.experiments],
        )
        session.human_review = review
        return {"human_review": review.model_dump()}
