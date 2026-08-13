"""Orchestrator specialist worker for goal decomposition and DAG generation."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from axiom.multi_agent.models import AgentRole, TaskGraph, TaskNode, TaskState
from axiom.multi_agent.graph import topological_sort
from axiom.multi_agent.budgets import MultiTierBudgetController
from axiom.multi_agent.roles.base import BaseSpecialistWorker


class OrchestratorAgent(BaseSpecialistWorker):
    """Specialist worker responsible for goal decomposition into a valid DAG TaskGraph."""

    async def execute(
        self,
        task: TaskNode,
        input_artifacts: List[Dict[str, Any]],
        project_id: str = "",
        user_id: str = "",
        budget_tracker: Optional[MultiTierBudgetController] = None,
    ) -> BaseModel:
        if self.llm_mock and AgentRole.ORCHESTRATOR in getattr(self.llm_mock, "responses", {}):
            return self.llm_mock.responses[AgentRole.ORCHESTRATOR]

        goal = task.description or task.input_data.get("goal", "Research research project")
        graph = TaskGraph()
        
        # Decompose into clean research pipeline nodes
        n1 = TaskNode(
            task_id=f"{task.task_id}-search",
            agent_role=AgentRole.RESEARCHER,
            description=f"Gather evidence on: {goal}",
        )
        n2 = TaskNode(
            task_id=f"{task.task_id}-analyze",
            agent_role=AgentRole.ANALYST,
            description=f"Extract grounded claims from evidence for: {goal}",
            depends_on=[n1.task_id],
        )
        n3 = TaskNode(
            task_id=f"{task.task_id}-critic",
            agent_role=AgentRole.CRITIC,
            description=f"Review and challenge extracted claims for: {goal}",
            depends_on=[n2.task_id],
        )
        n4 = TaskNode(
            task_id=f"{task.task_id}-verify",
            agent_role=AgentRole.VERIFIER,
            description=f"Classify truthfulness tiers for verified claims for: {goal}",
            depends_on=[n3.task_id],
        )
        n5 = TaskNode(
            task_id=f"{task.task_id}-synthesis",
            agent_role=AgentRole.SYNTHESIS,
            description=f"Compile final synthesis artifact for: {goal}",
            depends_on=[n4.task_id],
        )

        for node in [n1, n2, n3, n4, n5]:
            graph.add_node(node)

        # Validate DAG acyclicity via topological sort
        topological_sort(graph)
        return graph
