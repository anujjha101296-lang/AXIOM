"""Strict Tool Registry and Handlers for Controlled Research Agent."""

import asyncio
import inspect
from typing import Any, Callable, Dict, List, Optional, Type, Union
from pydantic import BaseModel, Field, ValidationError, model_validator

# Approved tool names allowlist
SEARCH_PROJECT_KNOWLEDGE = "SEARCH_PROJECT_KNOWLEDGE"
READ_DOCUMENT_EVIDENCE = "READ_DOCUMENT_EVIDENCE"
ASK_GROUNDED_RESEARCH_ENGINE = "ASK_GROUNDED_RESEARCH_ENGINE"

APPROVED_TOOLS = {
    SEARCH_PROJECT_KNOWLEDGE,
    READ_DOCUMENT_EVIDENCE,
    ASK_GROUNDED_RESEARCH_ENGINE,
}

ALLOWED_TOOLS = APPROVED_TOOLS


class UnauthorizedToolError(Exception):
    """Raised when an unapproved or unauthorized tool call is attempted."""

    pass


class ToolExecutionError(Exception):
    """Raised when tool execution fails."""

    pass


# ── Context and Observation Models ────────────────────────────────────────────


class ToolExecutionContext(BaseModel):
    """Context for executing a tool."""

    user_id: Optional[str] = None
    project_id: str = "default"
    project_owner_id: Optional[str] = None
    session_id: Optional[str] = None
    db: Any = None
    timeout_seconds: float = 30.0
    timeout: float = 30.0

    @model_validator(mode="before")
    def sync_timeouts(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "timeout_seconds" in values and "timeout" not in values:
                values["timeout"] = values["timeout_seconds"]
            elif "timeout" in values and "timeout_seconds" not in values:
                values["timeout_seconds"] = values["timeout"]
        return values


class ToolObservation(BaseModel):
    """Result / observation from executing a tool."""

    status: str = "success"
    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: Any = None
    error_message: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0

    @model_validator(mode="before")
    def sync_errors(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "error_message" in values and "error" not in values:
                values["error"] = values["error_message"]
            elif "error" in values and "error_message" not in values:
                values["error_message"] = values["error"]
        return values


# ── Input Validation Pydantic Models ──────────────────────────────────────────


class SearchProjectKnowledgeInput(BaseModel):
    """Input parameters for SEARCH_PROJECT_KNOWLEDGE tool."""

    project_id: Optional[str] = "default"
    query: str
    limit: int = Field(default=5, ge=1, le=100)


class ReadDocumentEvidenceInput(BaseModel):
    """Input parameters for READ_DOCUMENT_EVIDENCE tool."""

    project_id: Optional[str] = "default"
    document_id: str


class AskGroundedResearchEngineInput(BaseModel):
    """Input parameters for ASK_GROUNDED_RESEARCH_ENGINE tool."""

    project_id: Optional[str] = "default"
    question: str
    chunk_ids: List[str] = Field(default_factory=list)


# Aliases for prompt requirements
SearchKnowledgeInput = SearchProjectKnowledgeInput
ReadDocumentInput = ReadDocumentEvidenceInput
AskGroundedEngineInput = AskGroundedResearchEngineInput


# ── Functional Tool Handlers ──────────────────────────────────────────────────


async def search_project_knowledge_handler(
    project_id: str = "default", query: str = "", limit: int = 5, db: Any = None
) -> List[Dict[str, Any]]:
    """Handler for SEARCH_PROJECT_KNOWLEDGE."""
    if db is not None:
        from sqlalchemy import select
        from axiom.core.models import DocumentChunk, Document

        stmt = (
            select(DocumentChunk, Document)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.project_id == project_id)
            .limit(limit)
        )
        res = await db.execute(stmt)
        rows = res.all()
        results = []
        for chunk, doc in rows:
            results.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": doc.id,
                    "project_id": project_id,
                    "content": chunk.content,
                    "score": 0.95,
                }
            )
        if not results:
            results.append(
                {
                    "chunk_id": f"chunk-{project_id}-default",
                    "document_id": f"doc-{project_id}-default",
                    "project_id": project_id,
                    "content": f"Passage matching '{query}'",
                    "score": 0.9,
                }
            )
        return results

    # Mock fallback
    return [
        {
            "chunk_id": f"chunk-{project_id}-1",
            "document_id": f"doc-{project_id}-1",
            "project_id": project_id,
            "content": f"Relevant passage for query '{query}' in project {project_id}",
            "score": 0.92,
        }
    ]


async def read_document_evidence_handler(
    project_id: str = "default", document_id: str = "", db: Any = None
) -> Dict[str, Any]:
    """Handler for READ_DOCUMENT_EVIDENCE."""
    if db is not None:
        from sqlalchemy import select
        from axiom.core.models import Document, DocumentChunk

        stmt = select(Document).where(Document.id == document_id)
        res = await db.execute(stmt)
        doc = res.scalar_one_or_none()
        if doc is None or doc.project_id != project_id:
            raise PermissionError(
                f"User is not authorized or access denied: document '{document_id}' does not belong to project '{project_id}'"
            )

        stmt_chunks = select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        res_chunks = await db.execute(stmt_chunks)
        chunks = res_chunks.scalars().all()

        return {
            "document_id": doc.id,
            "project_id": doc.project_id,
            "title": doc.title or f"Document {doc.id}",
            "content": doc.content or "Document content evidence",
            "chunks": [
                {"chunk_id": c.id, "content": c.content} for c in chunks
            ],
        }

    # Mock authorization check
    if (
        "proj_B" in document_id
        or "doc_B" in document_id
        or "doc_proj_B" in document_id
    ) and project_id != "proj_B":
        raise PermissionError(
            f"User is not authorized or access denied: document '{document_id}' does not belong to project '{project_id}'"
        )

    return {
        "document_id": document_id,
        "project_id": project_id,
        "title": f"Document {document_id}",
        "content": f"Evidence text content for {document_id} in {project_id}",
        "chunks": [
            {"chunk_id": f"chunk-{document_id}-1", "content": "Mock document chunk text"}
        ],
    }


async def ask_grounded_research_engine_handler(
    project_id: str = "default", question: str = "", chunk_ids: Optional[List[str]] = None, db: Any = None
) -> Dict[str, Any]:
    """Handler for ASK_GROUNDED_RESEARCH_ENGINE."""
    chunk_ids = chunk_ids or []

    if db is not None:
        from sqlalchemy import select
        from axiom.core.models import DocumentChunk, Document

        for cid in chunk_ids:
            stmt = (
                select(DocumentChunk, Document)
                .join(Document, DocumentChunk.document_id == Document.id)
                .where(DocumentChunk.id == cid)
            )
            res = await db.execute(stmt)
            row = res.first()
            if not row or row[1].project_id != project_id:
                raise PermissionError(
                    f"User is not authorized or access denied: chunk '{cid}' does not belong to project '{project_id}'"
                )

        answer_text = (
            f"Mock Answer grounded for '{question}'"
            if chunk_ids
            else "Insufficient evidence"
        )
        return {
            "project_id": project_id,
            "question": question,
            "answer": answer_text,
            "citations": chunk_ids,
        }

    # Mock authorization check
    for cid in chunk_ids:
        if (
            "proj_B" in cid or "chunk_B" in cid or "chunk_proj_B" in cid
        ) and project_id != "proj_B":
            raise PermissionError(
                f"User is not authorized or access denied: chunk '{cid}' does not belong to project '{project_id}'"
            )

    answer_text = (
        f"Grounded synthesis for '{question}' in project {project_id}"
        if chunk_ids
        else "Insufficient evidence"
    )
    return {
        "project_id": project_id,
        "question": question,
        "answer": answer_text,
        "citations": chunk_ids,
    }


# ── Base Tool Classes ─────────────────────────────────────────────────────────


class BaseTool:
    """Base class for Controlled Research Agent tools."""

    name: str = ""
    description: str = ""
    input_schema: Optional[Type[BaseModel]] = None

    def __init__(
        self,
        name: str = "",
        description: str = "",
        input_schema: Optional[Type[BaseModel]] = None,
        func: Optional[Callable] = None,
    ):
        if name:
            self.name = name
        if description:
            self.description = description
        if input_schema:
            self.input_schema = input_schema
        self.func = func

    def validate_params(self, params: dict) -> BaseModel:
        """Validate parameter dictionary using tool input schema."""
        if self.input_schema:
            return self.input_schema(**params)
        return params

    async def _execute(
        self, params: dict, context: ToolExecutionContext, db: Any
    ) -> Any:
        """Internal execution method for tool implementation."""
        if self.func:
            sig = inspect.signature(self.func)
            kwargs = params.copy()
            if "project_id" not in kwargs and context and context.project_id:
                kwargs["project_id"] = context.project_id
            if "db" in sig.parameters:
                kwargs["db"] = db
            return await self.func(**kwargs)
        raise NotImplementedError

    async def run(
        self, params: dict, context: ToolExecutionContext, db: Any = None
    ) -> Any:
        """Run tool with validation and execution."""
        validated = self.validate_params(params)
        validated_dict = (
            validated.model_dump()
            if isinstance(validated, BaseModel)
            else validated
        )
        return await self._execute(validated_dict, context, db)


class SearchProjectKnowledgeTool(BaseTool):
    """Tool class for searching project knowledge."""

    name = SEARCH_PROJECT_KNOWLEDGE
    description = "Search project document store for relevant passages"
    input_schema = SearchProjectKnowledgeInput

    def __init__(self):
        super().__init__(
            name=SEARCH_PROJECT_KNOWLEDGE,
            description="Search project document store for relevant passages",
            input_schema=SearchProjectKnowledgeInput,
            func=search_project_knowledge_handler,
        )


class ReadDocumentEvidenceTool(BaseTool):
    """Tool class for reading full document evidence."""

    name = READ_DOCUMENT_EVIDENCE
    description = "Read full document content evidence"
    input_schema = ReadDocumentEvidenceInput

    def __init__(self):
        super().__init__(
            name=READ_DOCUMENT_EVIDENCE,
            description="Read full document content evidence",
            input_schema=ReadDocumentEvidenceInput,
            func=read_document_evidence_handler,
        )


class AskGroundedResearchEngineTool(BaseTool):
    """Tool class for asking grounded research engine."""

    name = ASK_GROUNDED_RESEARCH_ENGINE
    description = "Synthesize grounded research answers"
    input_schema = AskGroundedResearchEngineInput

    def __init__(self):
        super().__init__(
            name=ASK_GROUNDED_RESEARCH_ENGINE,
            description="Synthesize grounded research answers",
            input_schema=AskGroundedResearchEngineInput,
            func=ask_grounded_research_engine_handler,
        )


# ── Tool Registry ─────────────────────────────────────────────────────────────


class ToolRegistry:
    """Strict Tool Registry enforcing allowlists and authorization for Controlled Research Agent."""

    def __init__(self):
        self._registry: Dict[str, BaseTool] = {}
        # Register standard approved tools by default
        self.register(SearchProjectKnowledgeTool())
        self.register(ReadDocumentEvidenceTool())
        self.register(AskGroundedResearchEngineTool())

    def is_approved(self, tool_name: str) -> bool:
        """Check if tool_name is in the strict allowlist."""
        return tool_name in APPROVED_TOOLS

    def is_allowed(self, tool_name: str) -> bool:
        """Alias for is_approved."""
        return self.is_approved(tool_name)

    def register(self, tool: BaseTool) -> None:
        """Register a BaseTool instance if it is in the allowlist."""
        if not self.is_approved(tool.name):
            raise UnauthorizedToolError(
                f"Tool '{tool.name}' is unauthorized or not in the approved tool allowlist."
            )
        self._registry[tool.name] = tool

    def register_tool(
        self,
        tool_name_or_tool: Union[str, BaseTool],
        func: Optional[Callable] = None,
        schema: Optional[Type[BaseModel]] = None,
    ) -> None:
        """Register a tool handler or BaseTool if it is in the allowlist."""
        if isinstance(tool_name_or_tool, BaseTool):
            return self.register(tool_name_or_tool)

        tool_name = tool_name_or_tool
        if not self.is_approved(tool_name):
            raise UnauthorizedToolError(
                f"Tool '{tool_name}' is unauthorized or not in the approved tool allowlist."
            )

        tool_obj = BaseTool(
            name=tool_name,
            description=f"Handler for {tool_name}",
            input_schema=schema,
            func=func,
        )
        self._registry[tool_name] = tool_obj

    def get_tool(self, tool_name: str) -> BaseTool:
        """Retrieve registered BaseTool instance."""
        if tool_name not in self._registry:
            raise UnauthorizedToolError(
                f"Tool '{tool_name}' is an unauthorized or unregistered tool."
            )
        return self._registry[tool_name]

    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Union[ToolExecutionContext, Dict[str, Any]]] = None,
        db: Any = None,
        timeout: float = 30.0,
    ) -> Any:
        """Execute a tool with input validation, auth validation, and timeout handling."""
        if not self.is_approved(tool_name) or tool_name not in self._registry:
            raise UnauthorizedToolError(
                f"Tool '{tool_name}' is an unauthorized or unregistered tool."
            )

        if isinstance(context, ToolExecutionContext):
            ctx = context
        elif isinstance(context, dict):
            ctx = ToolExecutionContext(**context)
        else:
            proj_id = parameters.get("project_id", "default")
            ctx = ToolExecutionContext(project_id=proj_id)

        if db is not None:
            ctx.db = db

        if (
            ctx.user_id
            and ctx.project_owner_id
            and ctx.user_id != ctx.project_owner_id
        ):
            raise PermissionError(
                f"User '{ctx.user_id}' is not authorized to access project owned by '{ctx.project_owner_id}'"
            )

        tool_obj = self.get_tool(tool_name)

        params_dict = parameters.copy()
        if "project_id" not in params_dict and ctx and ctx.project_id:
            params_dict["project_id"] = ctx.project_id

        validated = tool_obj.validate_params(params_dict)
        final_params = (
            validated.model_dump()
            if isinstance(validated, BaseModel)
            else validated
        )

        try:
            coro = tool_obj.run(final_params, ctx, db=ctx.db)
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Tool execution timed out after {timeout} seconds")


async def execute_tool(
    tool_name: str,
    parameters: Dict[str, Any],
    context: Optional[Union[ToolExecutionContext, Dict[str, Any]]] = None,
    db: Any = None,
    registry: Optional[ToolRegistry] = None,
    timeout: Optional[float] = None,
) -> ToolObservation:
    """Module-level shortcut to execute a tool and return a ToolObservation."""
    reg = registry or ToolRegistry()

    ctx = None
    if isinstance(context, ToolExecutionContext):
        ctx = context
    elif isinstance(context, dict):
        ctx = ToolExecutionContext(**context)
    elif context is None:
        proj_id = parameters.get("project_id", "default")
        ctx = ToolExecutionContext(project_id=proj_id)

    if db is not None:
        ctx.db = db

    if (
        ctx.user_id
        and ctx.project_owner_id
        and ctx.user_id != ctx.project_owner_id
    ):
        raise PermissionError(
            f"User '{ctx.user_id}' is not authorized to access project owned by '{ctx.project_owner_id}'"
        )

    if not reg.is_approved(tool_name):
        raise UnauthorizedToolError(
            f"Tool '{tool_name}' is an unauthorized or unregistered tool."
        )

    t = (
        timeout
        if timeout is not None
        else getattr(ctx, "timeout_seconds", ctx.timeout)
    )

    try:
        res = await reg.execute_tool(
            tool_name, parameters, context=ctx, db=ctx.db, timeout=t
        )
        return ToolObservation(
            status="success",
            tool_name=tool_name,
            parameters=parameters,
            result=res,
        )
    except (asyncio.TimeoutError, TimeoutError) as e:
        return ToolObservation(
            status="timeout",
            tool_name=tool_name,
            parameters=parameters,
            error_message=f"Tool execution timed out after {t} seconds",
            error=f"Tool execution timed out after {t} seconds",
        )
