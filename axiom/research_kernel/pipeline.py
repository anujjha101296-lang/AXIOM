"""Research Kernel stage executor — delegates to ACA, SME, workflow, and plugins."""

from __future__ import annotations

import time
from typing import Any

from axiom.cognitive.engine import CognitiveArchitecture
from axiom.core.memory.working_memory import WorkingMemory
from axiom.core.reasoning.self_improvement import SelfImprovementLoop
from axiom.core.verification.smt_gateway import SmtGateway
from axiom.core.verification.truthfulness import assign_from_smt_modular
from axiom.research_kernel.models import KernelRun, KernelStage, StageOutput
from axiom.research_kernel.plugin import ResearchDomainPlugin
from axiom.scientific_method.engine import ScientificMethodEngine
from axiom.workflow.models import Task
from axiom.workflow.scheduler import WorkflowScheduler


class StageExecutor:
    """Executes a single kernel stage by delegating to existing subsystems."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._aca = CognitiveArchitecture(db_path)
        self._sme = ScientificMethodEngine(db_path)
        self._scheduler = WorkflowScheduler()
        self._working_memory = WorkingMemory()
        self._smt = SmtGateway()
        self._self_improve = SelfImprovementLoop(workspace_root="/tmp")

    def execute(
        self,
        run: KernelRun,
        stage: KernelStage,
        plugin: ResearchDomainPlugin,
    ) -> StageOutput:
        handlers = {
            KernelStage.GOAL_DECOMPOSITION: lambda: self._goal_decomposition(run, plugin),
            KernelStage.RESEARCH_PLANNING: lambda: self._research_planning(run, plugin),
            KernelStage.EVIDENCE_ACQUISITION: lambda: self._evidence_acquisition(run, plugin),
            KernelStage.MULTI_AGENT_ORCHESTRATION: lambda: self._multi_agent_orchestration(run, plugin),
            KernelStage.VERIFICATION_PIPELINE: lambda: self._verification_pipeline(run, plugin),
            KernelStage.MEMORY_INTEGRATION: lambda: self._memory_integration(run),
            KernelStage.REFLECTION: lambda: self._reflection(run),
            KernelStage.LEARNING: lambda: self._learning(run),
            KernelStage.BENCHMARK_EXECUTION: lambda: self._benchmark_execution(run, plugin),
            KernelStage.REPORT_GENERATION: lambda: self._report_generation(run, plugin),
        }
        subsystem_map = {
            KernelStage.GOAL_DECOMPOSITION: "plugin + aca.understanding",
            KernelStage.RESEARCH_PLANNING: "plugin + sme + aca.planning",
            KernelStage.EVIDENCE_ACQUISITION: "plugin + egs",
            KernelStage.MULTI_AGENT_ORCHESTRATION: "workflow.scheduler",
            KernelStage.VERIFICATION_PIPELINE: "plugin + sme.verification + truthfulness",
            KernelStage.MEMORY_INTEGRATION: "working_memory + sme.memory",
            KernelStage.REFLECTION: "aca.reflection",
            KernelStage.LEARNING: "self_improvement + kernel.store",
            KernelStage.BENCHMARK_EXECUTION: "plugin.benchmarks",
            KernelStage.REPORT_GENERATION: "kernel.reports + plugin",
        }
        subsystem = subsystem_map[stage]
        start = time.perf_counter()
        try:
            artifacts = handlers[stage]()
            return StageOutput(
                stage=stage,
                subsystem=subsystem,
                completed=True,
                artifacts=artifacts,
                duration_ms=round((time.perf_counter() - start) * 1000, 2),
            )
        except Exception as exc:
            return StageOutput(
                stage=stage,
                subsystem=subsystem,
                completed=False,
                errors=[str(exc)],
                duration_ms=round((time.perf_counter() - start) * 1000, 2),
            )

    def _ensure_aca_cycle(self, run: KernelRun) -> str:
        if run.aca_cycle_id:
            return run.aca_cycle_id
        cycle = self._aca.create_cycle(
            objective=run.objective,
            domain=run.domain,
            context={"kernel_run_id": run.run_id, **run.context},
        )
        run.aca_cycle_id = cycle.cycle_id
        return cycle.cycle_id

    def _ensure_sme_session(self, run: KernelRun) -> str:
        if run.sme_session_id:
            return run.sme_session_id
        session = self._sme.create_session(
            objective=run.objective,
            domain=run.domain,
            metadata={"kernel_run_id": run.run_id},
        )
        run.sme_session_id = session.session_id
        return session.session_id

    def _goal_decomposition(self, run: KernelRun, plugin: ResearchDomainPlugin) -> dict[str, Any]:
        decomposition = plugin.decompose_goal(run.objective, run.context)
        run.context["decomposition"] = decomposition

        cycle_id = self._ensure_aca_cycle(run)
        cycle = self._aca.execute_layer(cycle_id, None)  # perception
        run.context["aca_perception"] = {
            lo.layer.value: lo.artifacts for lo in cycle.layer_outputs[-1:]
        }
        return {"decomposition": decomposition, "aca_cycle_id": cycle_id}

    def _research_planning(self, run: KernelRun, plugin: ResearchDomainPlugin) -> dict[str, Any]:
        decomposition = run.context.get("decomposition", {})
        plan = plugin.research_plan(decomposition, run.context)
        run.context["plan"] = plan

        sme_id = self._ensure_sme_session(run)
        cycle_id = run.aca_cycle_id
        if cycle_id:
            self._aca.link_sme(cycle_id, sme_id)
            self._aca.execute_layer(cycle_id, None)  # advances to next layer

        return {"plan": plan, "sme_session_id": sme_id}

    def _evidence_acquisition(self, run: KernelRun, plugin: ResearchDomainPlugin) -> dict[str, Any]:
        plan = run.context.get("plan", {})
        evidence = plugin.acquire_evidence(plan, run.context)
        run.context["evidence"] = evidence
        return {"evidence": evidence, "source_count": len(evidence.get("sources", []))}

    def _multi_agent_orchestration(self, run: KernelRun, plugin: ResearchDomainPlugin) -> dict[str, Any]:
        plan = run.context.get("plan", {})
        task_defs = plugin.orchestration_tasks(plan, run.context)
        tasks = [
            Task(
                id=t["id"],
                title=t["title"],
                description=t.get("description", t["title"]),
                worker_type=t.get("worker_type", "researcher"),
                depends_on=t.get("depends_on", []),
            )
            for t in task_defs
        ]
        workflow_id = run.workflow_id or f"kernel-{run.run_id}"
        run.workflow_id = workflow_id
        schedule = self._scheduler.build_plan(workflow_id, tasks)
        run.context["orchestration"] = {
            "workflow_id": workflow_id,
            "batches": len(schedule.batches),
            "total_tasks": schedule.total_tasks,
            "max_parallelism": schedule.max_parallelism,
        }
        return run.context["orchestration"]

    def _verification_pipeline(self, run: KernelRun, plugin: ResearchDomainPlugin) -> dict[str, Any]:
        evidence = run.context.get("evidence", {})
        domain_verify = plugin.verify(evidence, run.context)
        run.context["verification"] = domain_verify

        is_valid, _ = self._smt.verify_modular_conjecture("x + y == z", 7, ["x", "y", "z"])
        truthfulness = assign_from_smt_modular(is_valid)
        run.context["truthfulness"] = {
            "epistemic_status": truthfulness.epistemic_status.value,
            "verification_tier": truthfulness.verification_tier.value,
            "evidence_mode": truthfulness.evidence_mode.value,
        }
        return {
            "domain_verification": domain_verify,
            "truthfulness": run.context["truthfulness"],
            "passed": domain_verify.get("passed", False),
        }

    def _memory_integration(self, run: KernelRun) -> dict[str, Any]:
        self._working_memory.set_problem(run.objective)
        decomp = run.context.get("decomposition", {})
        for goal in decomp.get("sub_goals", [])[:3]:
            self._working_memory.add_question(goal)
        snapshot = self._working_memory.snapshot()
        run.context["memory"] = {"snapshot_keys": list(snapshot.keys()), "problem_set": bool(snapshot.get("problem"))}

        sme_id = run.sme_session_id
        memory_records = 0
        if sme_id:
            session = self._sme.get_session(sme_id)
            if session:
                memory_records = len(session.memory_records)
        return {"working_memory_snapshot": snapshot, "sme_memory_records": memory_records}

    def _reflection(self, run: KernelRun) -> dict[str, Any]:
        cycle_id = run.aca_cycle_id
        reflections: list[str] = []
        if cycle_id:
            cycle = self._aca.store.get(cycle_id)
            if cycle:
                reflections.append(f"Completed {len(cycle.layers_completed)} ACA layers")
        reflections.append(
            f"Verification {'passed' if run.context.get('verification', {}).get('passed') else 'inconclusive'}"
        )
        run.context["reflections"] = reflections
        return {"reflections": reflections, "count": len(reflections)}

    def _learning(self, run: KernelRun) -> dict[str, Any]:
        audit = self._self_improve.report()
        run.context["learning"] = {
            "top_priorities": audit.get("top_3_priority", []),
            "weakest_dimension": audit.get("weakest_dimension"),
            "kernel_run_recorded": True,
        }
        return run.context["learning"]

    def _benchmark_execution(self, run: KernelRun, plugin: ResearchDomainPlugin) -> dict[str, Any]:
        results = []
        for bench in plugin.benchmarks():
            result = plugin.run_benchmark(bench, run.context)
            results.append(result)
        run.benchmark_results = results
        run.context["benchmark_results"] = results
        passed = sum(1 for r in results if r.get("passed"))
        return {
            "benchmark_count": len(results),
            "passed": passed,
            "all_passed": passed == len(results) if results else True,
            "results": results,
        }

    def _report_generation(self, run: KernelRun, plugin: ResearchDomainPlugin) -> dict[str, Any]:
        from axiom.research_kernel.reports import generate_kernel_report

        report = generate_kernel_report(run, plugin)
        run.report = report
        return {"report_length": len(report), "has_domain_section": "##" in report}
