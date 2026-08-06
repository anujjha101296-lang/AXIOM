"""
AXIOM Workflow Engine — Demo: GNN Paper Research
=================================================
Demonstrates the full workflow engine with a real research task.

Input: "Read 5 research papers about graph neural networks."
Workers:
    plan → [read_paper_1 ... read_paper_5 (parallel)] → review → merge → store → report

Run:
    python -m axiom.workflow.demos.gnn_paper_research
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

# Ensure axiom is on the Python path when run directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from axiom.workflow.engine import WorkflowEngine
from axiom.workflow.models import Task, WorkflowStatus
from axiom.workflow.registry import build_default_registry


GNN_PAPERS = [
    {
        "title": "Semi-supervised Classification with Graph Convolutional Networks",
        "url": "https://arxiv.org/abs/1609.02907",
        "topic": "graph convolutional networks node classification",
    },
    {
        "title": "Graph Attention Networks",
        "url": "https://arxiv.org/abs/1710.10903",
        "topic": "graph attention mechanisms multi-head attention",
    },
    {
        "title": "Inductive Representation Learning on Large Graphs (GraphSAGE)",
        "url": "https://arxiv.org/abs/1706.02216",
        "topic": "inductive learning graph sampling aggregation",
    },
    {
        "title": "How Powerful are Graph Neural Networks?",
        "url": "https://arxiv.org/abs/1810.00826",
        "topic": "GNN expressiveness Weisfeiler-Leman graph isomorphism",
    },
    {
        "title": "Deep Graph Infomax",
        "url": "https://arxiv.org/abs/1809.10341",
        "topic": "self-supervised graph representation mutual information",
    },
]


def build_gnn_workflow(engine: WorkflowEngine):
    """
    Build the GNN research workflow with explicit task DAG:

    plan (id=t0)
      ├── read_paper_1 (t1, depends=[t0])
      ├── read_paper_2 (t2, depends=[t0])  ← parallel
      ├── read_paper_3 (t3, depends=[t0])  ← parallel
      ├── read_paper_4 (t4, depends=[t0])  ← parallel
      └── read_paper_5 (t5, depends=[t0])  ← parallel
              └── review_extractions (t6, depends=[t1,t2,t3,t4,t5])
                      └── merge_knowledge (t7, depends=[t6])
                              └── generate_report (t8, depends=[t7])
    """
    workflow = engine.create_workflow(
        objective="Read 5 research papers about graph neural networks.",
        domain="research",
        metadata={"demo": True, "paper_count": 5},
    )

    # Task IDs for dependency wiring
    t_ids = [Task(title="placeholder", worker_type="researcher").id for _ in range(9)]

    # t0: Plan (handled automatically by engine._run_planning, but we'll build manually)
    # We build tasks explicitly here to demonstrate the DAG structure
    tasks = []

    # Read tasks (parallel — all depend only on t0, which we skip since we're building directly)
    read_task_ids = []
    for i, paper in enumerate(GNN_PAPERS):
        read_task = Task(
            workflow_id=workflow.id,
            title=f"Read paper: {paper['title'][:50]}",
            description=f"Extract key findings from: {paper['title']}",
            worker_type="researcher",
            inputs={
                "topic": paper["topic"],
                "source_url": paper["url"],
                "objective": workflow.objective,
                "domain": "research",
            },
            depends_on=[],  # All run in parallel (no planner dependency in demo)
            max_retries=1,
            timeout_s=60.0,
        )
        tasks.append(read_task)
        read_task_ids.append(read_task.id)

    # Review task (depends on all reads completing)
    review_task = Task(
        workflow_id=workflow.id,
        title="Review extractions",
        description="Validate quality of extracted knowledge from all 5 papers",
        worker_type="reviewer",
        inputs={
            "min_claims": 3,
            "min_concepts": 5,
        },
        depends_on=read_task_ids,
        timeout_s=30.0,
    )
    tasks.append(review_task)

    # Merge task
    merge_task = Task(
        workflow_id=workflow.id,
        title="Merge knowledge",
        description="Deduplicate and merge knowledge from all 5 papers",
        worker_type="merger",
        inputs={"source_count": 5},
        depends_on=[review_task.id],
        timeout_s=30.0,
    )
    tasks.append(merge_task)

    # Final report
    report_task = Task(
        workflow_id=workflow.id,
        title="Generate research report",
        description="Synthesize findings into a final GNN research report",
        worker_type="reporter",
        inputs={
            "title": "Graph Neural Networks: Survey of 5 Foundational Papers",
        },
        depends_on=[merge_task.id],
        timeout_s=30.0,
    )
    tasks.append(report_task)

    # Save tasks to workflow
    workflow.tasks = tasks
    engine.store.save(workflow)

    return workflow


async def run_demo():
    print("=" * 60)
    print("AXIOM Workflow Engine — GNN Paper Research Demo")
    print("=" * 60)
    print()

    registry = build_default_registry()
    engine = WorkflowEngine(registry=registry)

    print("📋 Building workflow...")
    workflow = build_gnn_workflow(engine)

    print(f"   Workflow ID: {workflow.id}")
    print(f"   Objective:   {workflow.objective}")
    print(f"   Tasks:       {len(workflow.tasks)}")
    print()

    # Show the schedule
    from axiom.workflow.scheduler import WorkflowScheduler
    scheduler = WorkflowScheduler()
    plan = scheduler.build_plan(workflow.id, workflow.tasks)

    print("📊 Execution Plan:")
    for batch in plan.batches:
        parallel = len(batch.tasks) > 1
        indicator = "║" if parallel else "→"
        print(f"  Batch {batch.batch_index} [{indicator} {'parallel' if parallel else 'sequential'}]:")
        for task in batch.tasks:
            print(f"    • [{task.worker_type}] {task.title}")
    print()
    print(f"   Total tasks: {plan.total_tasks}")
    print(f"   Max parallelism: {plan.max_parallelism}")
    print()

    print("🚀 Executing workflow...")
    result = await engine.run(workflow.id)
    print()

    # Show results
    status_icon = "✅" if result.status == WorkflowStatus.COMPLETED else "❌"
    print(f"{status_icon} Workflow {result.status.value.upper()}")
    print(f"   Duration:         {result.duration_s:.2f}s")
    print(f"   Tasks completed:  {result.completed_tasks}/{result.total_tasks}")
    print(f"   Tasks failed:     {result.failed_tasks}")
    print(f"   Artifacts:        {len(result.artifacts)}")
    print()

    # Show artifacts
    if result.artifacts:
        print("📦 Artifacts produced:")
        for artifact in result.artifacts:
            print(f"   [{artifact.artifact_type.value:20s}] {artifact.title[:60]} (v{artifact.version})")
        print()

    # Show final report
    if result.final_report:
        print("📄 Final Report (excerpt):")
        print("-" * 50)
        report_text = result.final_report.text_content
        # Print first 40 lines
        lines = report_text.split("\n")
        for line in lines[:40]:
            print(line)
        if len(lines) > 40:
            print(f"  ... ({len(lines) - 40} more lines)")
        print("-" * 50)

    # Show events
    events = engine.get_events(workflow.id)
    print(f"\n📡 Event Log ({len(events)} events):")
    for event in events:
        print(f"   {event.event_type.value:<35} {event.timestamp.strftime('%H:%M:%S.%f')[:-3]}")

    return result


if __name__ == "__main__":
    result = asyncio.run(run_demo())
    sys.exit(0 if result.status == WorkflowStatus.COMPLETED else 1)
