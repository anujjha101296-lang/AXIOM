"""Evidence Researcher specialist worker for executing search tools and gathering EvidencePackets."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from axiom.multi_agent.models import AgentRole, TaskNode
from axiom.multi_agent.budgets import MultiTierBudgetController
from axiom.multi_agent.roles.base import (
    BaseSpecialistWorker,
    EvidencePacket,
    EvidenceSnippet,
    execute_tool,
    sanitize_input,
)


class EvidenceResearcherAgent(BaseSpecialistWorker):
    """Specialist worker executing document search tools to collect evidence."""

    async def execute(
        self,
        task: TaskNode,
        input_artifacts: List[Dict[str, Any]],
        project_id: str = "",
        user_id: str = "",
        budget_tracker: Optional[MultiTierBudgetController] = None,
    ) -> BaseModel:
        if self.llm_mock and AgentRole.RESEARCHER in getattr(self.llm_mock, "responses", {}):
            return self.llm_mock.responses[AgentRole.RESEARCHER]

        query = task.description or task.input_data.get("query", "Default research search query")
        query_sanitized = sanitize_input(query)

        if budget_tracker:
            budget_tracker.record_tool_call(1)
        task.budget.tool_calls_used += 1

        # Execute search tool safely
        tool_res = execute_tool("SEARCH_PROJECT_KNOWLEDGE", {"query": query_sanitized})

        # Generate evidence snippets
        snippets = [
            EvidenceSnippet(
                snippet_id=f"snip-{task.task_id}-1",
                doc_id=f"doc-{project_id or 'main'}-1",
                text=f"Evidence for query '{query_sanitized}': {tool_res.get('result', '')}",
                confidence=0.95,
            )
        ]

        return EvidencePacket(
            query=query_sanitized,
            snippets=snippets,
            warnings=[],
        )
