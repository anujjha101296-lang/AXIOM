"""Async Multi-Agent Execution Engine for Phase 9 Controlled Research System."""

import asyncio
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from axiom.multi_agent.models import AgentRole, TaskGraph, TaskNode, TaskState
from axiom.multi_agent.graph import resolve_dependencies, topological_sort, TaskGraphCycleError
from axiom.multi_agent.budgets import MultiTierBudgetController, BudgetExceededError
from axiom.multi_agent.cancellation import AsyncCancellationGateway
from axiom.multi_agent.roles import (
    BaseSpecialistWorker,
    OrchestratorAgent,
    EvidenceResearcherAgent,
    AnalystAgent,
    CriticAgent,
    VerifierAgent,
    SynthesisAgent,
    DeterministicLLMMock,
)


class MultiAgentExecutionEngine:
    """Async execution engine running topological sort, dependency resolution, worker dispatch, budget enforcement, and cancellation."""

    def __init__(
        self,
        db_session: Optional[Any] = None,
        llm_mock: Optional[Any] = None,
        cancellation_token: Optional[AsyncCancellationGateway] = None,
    ):
        self.db_session = db_session
        self.llm_mock = llm_mock or DeterministicLLMMock()
        self.cancellation_token = cancellation_token or AsyncCancellationGateway()

        self.workers: Dict[AgentRole, BaseSpecialistWorker] = {
            AgentRole.ORCHESTRATOR: OrchestratorAgent(llm_mock=self.llm_mock),
            AgentRole.RESEARCHER: EvidenceResearcherAgent(llm_mock=self.llm_mock),
            AgentRole.ANALYST: AnalystAgent(llm_mock=self.llm_mock),
            AgentRole.CRITIC: CriticAgent(llm_mock=self.llm_mock),
            AgentRole.VERIFIER: VerifierAgent(llm_mock=self.llm_mock),
            AgentRole.SYNTHESIS: SynthesisAgent(llm_mock=self.llm_mock),
        }

    async def execute_run(
        self,
        run_id: str,
        graph: TaskGraph,
        budget_controller: Optional[MultiTierBudgetController] = None,
    ) -> str:
        """Execute a TaskGraph to completion, enforcing budget limits and cancellation tokens.

        Returns:
            str: Final run status string ("COMPLETED", "FAILED", "BUDGET_EXCEEDED", "CANCELLED").
        """
        if self.cancellation_token.is_cancelled:
            self.cancellation_token.apply_cancellation(graph)
            return "CANCELLED"

        budget = budget_controller or MultiTierBudgetController()

        # Step 1: Initial dependency resolution
        resolve_dependencies(graph)

        try:
            topo_order = topological_sort(graph)
        except (TaskGraphCycleError, ValueError):
            return "FAILED"

        artifact_store: Dict[str, Any] = {}

        for task_id in topo_order:
            if self.cancellation_token.is_cancelled:
                self.cancellation_token.apply_cancellation(graph)
                return "CANCELLED"

            node = graph.get_node(task_id)
            if not node or node.state != TaskState.READY:
                continue

            # Check node-level step budget
            if node.budget.max_steps <= 0 or node.budget.steps_used >= node.budget.max_steps:
                node.transition_to(TaskState.BUDGET_EXCEEDED, error_message="Task step limit reached.")
                resolve_dependencies(graph)
                continue

            node.transition_to(TaskState.RUNNING)

            try:
                budget.record_step(1)
                node.budget.steps_used += 1

                # Gather upstream artifacts
                input_artifacts = [
                    artifact_store[dep_id]
                    for dep_id in node.depends_on
                    if dep_id in artifact_store
                ]

                # Dispatch specialist role worker
                worker = self.workers.get(node.agent_role)
                if worker is None:
                    raise ValueError(f"No registered specialist worker for role: {node.agent_role}")

                artifact = await worker.execute(
                    node,
                    input_artifacts=input_artifacts,
                    budget_tracker=budget,
                )

                artifact_dict = artifact.model_dump() if hasattr(artifact, "model_dump") else (
                    artifact.dict() if hasattr(artifact, "dict") else artifact
                )
                artifact_store[task_id] = artifact_dict
                node.output_artifact_id = f"art-{task_id}"

                node.transition_to(TaskState.COMPLETED)
            except BudgetExceededError as be:
                node.transition_to(TaskState.BUDGET_EXCEEDED, error_message=str(be))
            except Exception as e:
                node.transition_to(TaskState.FAILED, error_message=str(e))

            resolve_dependencies(graph)

        # Evaluate final graph status
        states = {n.state for n in graph.nodes.values()}
        if TaskState.FAILED in states:
            return "FAILED"
        if TaskState.BUDGET_EXCEEDED in states:
            return "BUDGET_EXCEEDED"
        if TaskState.CANCELLED in states:
            return "CANCELLED"
        if all(s == TaskState.COMPLETED for s in states):
            return "COMPLETED"
        return "COMPLETED"
