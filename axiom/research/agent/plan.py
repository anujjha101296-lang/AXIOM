"""Structured planning schemas and plan parser for Controlled Research Agent."""

from datetime import datetime, timezone
from enum import Enum
import json
import re
from typing import Any, Dict, List, Optional, Union
import uuid
from pydantic import BaseModel, Field, model_validator


class SubtaskStatus(str, Enum):
    """Status states for research subtasks."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchSubtask(BaseModel):
    """Structured subtask item within a ResearchPlan."""

    subtask_id: str = Field(default="", alias="id")
    description: str = ""
    expected_evidence: str = ""
    tool_names: List[str] = Field(default_factory=list, alias="recommended_tools")
    success_criteria: str = ""
    status: Union[SubtaskStatus, str] = SubtaskStatus.PENDING

    # Additional fields for compatibility
    title: Optional[str] = None
    goal: Optional[str] = None
    tool_name: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "use_enum_values": True,
        "arbitrary_types_allowed": True,
    }

    @model_validator(mode="before")
    @classmethod
    def _remap_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # subtask_id / id remap
            if "id" in data and "subtask_id" not in data:
                data["subtask_id"] = data["id"]
            elif "subtask_id" in data and "id" not in data:
                data["id"] = data["subtask_id"]
            elif not data.get("subtask_id") and not data.get("id"):
                gen_id = f"st-{uuid.uuid4().hex[:6]}"
                data["subtask_id"] = gen_id
                data["id"] = gen_id

            # tool_names / recommended_tools / tools / required_tools / tool_name remap
            tool_list = []
            if "tool_names" in data and isinstance(data["tool_names"], list):
                tool_list = data["tool_names"]
            elif "recommended_tools" in data and isinstance(data["recommended_tools"], list):
                tool_list = data["recommended_tools"]
            elif "tools" in data and isinstance(data["tools"], list):
                tool_list = data["tools"]
            elif "required_tools" in data and isinstance(data["required_tools"], list):
                tool_list = data["required_tools"]
            elif "tool_name" in data and isinstance(data["tool_name"], str):
                tool_list = [data["tool_name"]]

            data["tool_names"] = tool_list
            data["recommended_tools"] = tool_list

            # description / goal / title sync
            if "description" not in data or not data["description"]:
                data["description"] = data.get("goal") or data.get("title") or ""
            if "goal" not in data or not data["goal"]:
                data["goal"] = data.get("description") or ""

            # Ensure status is lowercase string e.g. "pending"
            if "status" in data:
                val = data["status"]
                if isinstance(val, SubtaskStatus):
                    data["status"] = val.value
                elif isinstance(val, str):
                    data["status"] = val.lower()

        return data

    @property
    def id(self) -> str:
        return self.subtask_id

    @property
    def recommended_tools(self) -> List[str]:
        return self.tool_names

    @property
    def tools(self) -> List[str]:
        return self.tool_names

    @property
    def required_tools(self) -> List[str]:
        return self.tool_names


class ResearchPlan(BaseModel):
    """Structured machine-readable research plan for Controlled Research Agent."""

    session_id: Optional[str] = None
    plan_id: Optional[str] = None
    goal: str = ""
    subtasks: List[ResearchSubtask] = Field(default_factory=list)
    overall_success_criteria: str = ""
    expected_evidence: List[str] = Field(default_factory=list)
    allowed_tools: List[str] = Field(default_factory=list)
    tools_required: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True,
        "use_enum_values": True,
        "arbitrary_types_allowed": True,
    }

    @model_validator(mode="before")
    @classmethod
    def _sync_plan_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("plan_id"):
                data["plan_id"] = f"plan-{uuid.uuid4().hex[:8]}"
        return data

    def to_dict(self) -> Dict[str, Any]:
        """Convert plan instance into serializable dictionary."""
        if hasattr(self, "model_dump"):
            res = self.model_dump()
        else:
            res = self.dict()

        if isinstance(res.get("created_at"), datetime):
            res["created_at"] = res["created_at"].isoformat()
        if isinstance(res.get("updated_at"), datetime):
            res["updated_at"] = res["updated_at"].isoformat()

        res["tools_required"] = self.allowed_tools or self.tools_required
        return res

    def to_json(self) -> str:
        """Serialize plan instance to JSON string."""
        if hasattr(self, "model_dump_json"):
            return self.model_dump_json()
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchPlan":
        """Construct a ResearchPlan instance from a dictionary."""
        if hasattr(cls, "model_validate"):
            return cls.model_validate(data)
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "ResearchPlan":
        """Parse a ResearchPlan instance from JSON string or Markdown fence."""
        return parse_plan_json(json_str)

    def get_subtask(self, subtask_id: str) -> Optional[ResearchSubtask]:
        """Retrieve subtask by ID or alias."""
        for st in self.subtasks:
            if st.subtask_id == subtask_id or st.id == subtask_id:
                return st
        return None

    def update_subtask_status(
        self, subtask_id: str, status: Union[str, SubtaskStatus]
    ) -> bool:
        """Update status of a subtask by ID."""
        target_status = status.value if isinstance(status, SubtaskStatus) else str(status).lower()
        subtask = self.get_subtask(subtask_id)
        if subtask:
            subtask.status = target_status
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False

    def mark_subtask_completed(self, subtask_id: str) -> bool:
        """Mark subtask as completed."""
        return self.update_subtask_status(subtask_id, SubtaskStatus.COMPLETED)

    def mark_subtask_failed(self, subtask_id: str) -> bool:
        """Mark subtask as failed."""
        return self.update_subtask_status(subtask_id, SubtaskStatus.FAILED)

    def get_subtasks_by_status(
        self, status: Union[str, SubtaskStatus]
    ) -> List[ResearchSubtask]:
        """Filter subtasks by status state."""
        target_status = status.value if isinstance(status, SubtaskStatus) else str(status).lower()
        return [
            st for st in self.subtasks
            if st.status == target_status or str(getattr(st.status, "value", st.status)).lower() == target_status
        ]

    def get_pending_subtasks(self) -> List[ResearchSubtask]:
        """Get list of subtasks with pending status."""
        return self.get_subtasks_by_status(SubtaskStatus.PENDING)

    def get_in_progress_subtasks(self) -> List[ResearchSubtask]:
        """Get list of subtasks with in_progress status."""
        return self.get_subtasks_by_status(SubtaskStatus.IN_PROGRESS)

    def get_completed_subtasks(self) -> List[ResearchSubtask]:
        """Get list of subtasks with completed status."""
        return self.get_subtasks_by_status(SubtaskStatus.COMPLETED)

    def get_failed_subtasks(self) -> List[ResearchSubtask]:
        """Get list of subtasks with failed status."""
        return self.get_subtasks_by_status(SubtaskStatus.FAILED)

    @property
    def is_completed(self) -> bool:
        """Check if all subtasks in plan are completed."""
        if not self.subtasks:
            return False
        return all(
            st.status == SubtaskStatus.COMPLETED or str(getattr(st.status, "value", st.status)).lower() == "completed"
            for st in self.subtasks
        )

    @property
    def is_failed(self) -> bool:
        """Check if any subtask in plan has failed status."""
        return any(
            st.status == SubtaskStatus.FAILED or str(getattr(st.status, "value", st.status)).lower() == "failed"
            for st in self.subtasks
        )

    @property
    def is_complete(self) -> bool:
        """Alias for is_completed."""
        return self.is_completed


def generate_initial_plan(
    goal: str,
    document_summaries: Optional[List[str]] = None,
    max_steps: Optional[int] = None,
) -> ResearchPlan:
    """Construct a structured machine-readable research plan given a research goal."""
    summaries = document_summaries or []
    summary_context = f" across {len(summaries)} documents" if summaries else ""

    subtasks = [
        ResearchSubtask(
            subtask_id="subtask-1",
            description=f"Search project knowledge base for context and evidence related to: {goal}{summary_context}",
            expected_evidence="Relevant document chunks, passage citations, and text snippets",
            tool_names=["SEARCH_PROJECT_KNOWLEDGE"],
            success_criteria="Retrieved relevant knowledge chunks covering key aspects of the research goal",
            status=SubtaskStatus.PENDING,
        ),
        ResearchSubtask(
            subtask_id="subtask-2",
            description=f"Read and extract specific evidence statements for goal: {goal}",
            expected_evidence="Verbatim text evidence, source document IDs, and contextual passages",
            tool_names=["READ_DOCUMENT_EVIDENCE"],
            success_criteria="Extracted concrete evidence and documented source citations",
            status=SubtaskStatus.PENDING,
        ),
        ResearchSubtask(
            subtask_id="subtask-3",
            description=f"Synthesize findings and address core research goal: {goal}",
            expected_evidence="Grounded research answers and verified evidence taxonomy classification",
            tool_names=["ASK_GROUNDED_RESEARCH_ENGINE"],
            success_criteria="Generated comprehensive research synthesis supported by document evidence",
            status=SubtaskStatus.PENDING,
        ),
    ]

    overall_success_criteria = (
        f"All subtasks completed with verified evidence addressing research goal: '{goal}'"
    )

    now = datetime.now(timezone.utc)
    tools = ["SEARCH_PROJECT_KNOWLEDGE", "READ_DOCUMENT_EVIDENCE", "ASK_GROUNDED_RESEARCH_ENGINE"]
    return ResearchPlan(
        goal=goal,
        subtasks=subtasks,
        overall_success_criteria=overall_success_criteria,
        allowed_tools=tools,
        tools_required=tools,
        created_at=now,
        updated_at=now,
    )


def parse_plan_json(json_str: str) -> ResearchPlan:
    """Parse and validate a ResearchPlan from a JSON string or Markdown code block."""
    if not json_str or not json_str.strip():
        raise ValueError("Cannot parse plan from empty string.")

    cleaned = json_str.strip()

    # Extract JSON if wrapped in markdown code fence (```json ... ``` or ``` ...)
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if match:
        cleaned = match.group(1).strip()

    try:
        if hasattr(ResearchPlan, "model_validate_json"):
            return ResearchPlan.model_validate_json(cleaned)
        else:
            data = json.loads(cleaned)
            return ResearchPlan(**data)
    except Exception as exc:
        try:
            data = json.loads(cleaned)
            if hasattr(ResearchPlan, "model_validate"):
                return ResearchPlan.model_validate(data)
            return ResearchPlan(**data)
        except Exception as inner_exc:
            raise ValueError(f"Failed to parse ResearchPlan JSON: {exc}") from inner_exc
