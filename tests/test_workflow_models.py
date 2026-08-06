"""Tests for workflow domain models."""

from axiom.workflow.models import (
    Artifact,
    ArtifactType,
    Task,
    TaskStatus,
    Workflow,
    WorkflowContext,
    WorkflowStatus,
    WorkerResult,
)


def test_task_defaults():
    task = Task(title="Analyze paper", worker_type="researcher")
    assert task.id
    assert task.status == TaskStatus.PENDING
    assert task.max_retries == 2
    assert task.timeout_s == 300.0


def test_workflow_get_task():
    wf = Workflow(objective="Test objective")
    task = Task(title="Step 1", worker_type="planner", workflow_id=wf.id)
    wf.tasks.append(task)
    assert wf.get_task(task.id) is task
    assert wf.get_task("missing") is None


def test_workflow_get_tasks_by_status():
    wf = Workflow(objective="Test")
    t1 = Task(title="A", worker_type="w", status=TaskStatus.PENDING)
    t2 = Task(title="B", worker_type="w", status=TaskStatus.COMPLETED)
    wf.tasks = [t1, t2]
    pending = wf.get_tasks_by_status(TaskStatus.PENDING)
    assert len(pending) == 1
    assert pending[0].title == "A"


def test_workflow_is_terminal():
    wf = Workflow(objective="Test")
    assert not wf.is_terminal()
    wf.status = WorkflowStatus.COMPLETED
    assert wf.is_terminal()
    wf.status = WorkflowStatus.FAILED
    assert wf.is_terminal()
    wf.status = WorkflowStatus.RUNNING
    assert not wf.is_terminal()


def test_workflow_context_defaults():
    ctx = WorkflowContext(objective="Research synthesis")
    assert ctx.domain == "general"
    assert ctx.working_memory == {}


def test_artifact_creation():
    art = Artifact(
        task_id="t1",
        workflow_id="w1",
        artifact_type=ArtifactType.REPORT,
        title="Final report",
        text_content="Summary text",
    )
    assert art.id
    assert art.version == 1
    assert art.artifact_type == ArtifactType.REPORT


def test_worker_result_success():
    result = WorkerResult(success=True, outputs={"key": "value"})
    assert result.success
    assert result.artifacts == []
    assert result.error is None
