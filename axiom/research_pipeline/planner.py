"""Research Planner for Phase 13 Pipeline."""
from typing import List
from axiom.research_pipeline.models import (
    ResearchQuestion,
    ResearchPlan,
    QuerySet,
    SearchQuery,
    SourceType,
)


class ResearchPlanner:
    """Decomposes research questions into structured plans and queries."""

    def create_plan(self, question: ResearchQuestion) -> ResearchPlan:
        """Generate sub-questions and target domains based on question text."""
        q_text = question.question
        sub_questions = [
            f"What is the theoretical baseline for '{q_text}'?",
            f"What empirical evidence exists for '{q_text}'?",
            f"What are the state-of-the-art implementations of '{q_text}'?",
        ]
        return ResearchPlan(
            question_id=question.id,
            sub_questions=sub_questions,
            target_domains=["arxiv.org", "wikipedia.org", "github.com", "nature.com"],
            required_source_types=[SourceType.PAPER, SourceType.WEB, SourceType.DATASET],
        )

    def generate_queries(self, plan: ResearchPlan) -> QuerySet:
        """Convert plan into concrete search queries."""
        queries: List[SearchQuery] = []
        for sq in plan.sub_questions:
            queries.append(
                SearchQuery(
                    query=sq,
                    target_source_type=SourceType.PAPER,
                    sub_question=sq,
                )
            )
            queries.append(
                SearchQuery(
                    query=f"{sq} benchmark dataset",
                    target_source_type=SourceType.DATASET,
                    sub_question=sq,
                )
            )
        return QuerySet(question_id=plan.question_id, queries=queries)
