"""Curated Golden Demo dataset — Graph Neural Networks for Drug Discovery."""

from __future__ import annotations

from axiom.demo.schema import (
    DemoContradiction,
    DemoExperiment,
    DemoGap,
    DemoHypothesis,
    DemoKnowledgeEdge,
    DemoKnowledgeNode,
    DemoNote,
    DemoPaper,
    DemoProject,
    DemoReportSection,
    DemoResearchReport,
    DemoState,
    DemoTimelineEvent,
    DemoTourStep,
)


def build_demo_state() -> DemoState:
    """Return the complete Golden Demo payload."""
    project = DemoProject(
        id="demo-gnn-drug-discovery",
        name="GNN Generalization for Molecular Property Prediction",
        description=(
            "Investigating when graph neural networks transfer across chemical scaffolds "
            "and which inductive biases improve out-of-distribution drug discovery benchmarks."
        ),
        research_question=(
            "Under what structural conditions do message-passing GNNs generalize to unseen "
            "molecular scaffolds on ADMET prediction tasks?"
        ),
        created_at="2026-08-06T10:00:00Z",
    )

    papers = [
        DemoPaper(
            id="paper-gilmer",
            title="Neural Message Passing for Quantum Chemistry",
            authors="Gilmer et al.",
            year=2017,
            filename="gilmer2017_message_passing.pdf",
            pages=12,
            summary=(
                "Introduces the MPNN framework unifying graph convolutions for molecular graphs. "
                "Demonstrates competitive performance on QM9 regression with learned message functions."
            ),
            key_findings=[
                "Message-passing unifies several GNN variants",
                "Edge features improve quantum property prediction",
                "Depth beyond 4 layers shows diminishing returns on QM9",
            ],
        ),
        DemoPaper(
            id="paper-hu",
            title="Strategies for Pre-training Graph Neural Networks",
            authors="Hu et al.",
            year=2020,
            filename="hu2020_pretraining_gnns.pdf",
            pages=18,
            summary=(
                "Proposes multi-level pre-training (node, edge, graph) on large molecular corpora. "
                "Fine-tuned models outperform from-scratch training on downstream MoleculeNet tasks."
            ),
            key_findings=[
                "Context prediction pre-training improves transfer",
                "Graph-level supervised pre-training helps classification",
                "Pre-training gains largest on data-scarce targets",
            ],
        ),
        DemoPaper(
            id="paper-sun",
            title="Out-of-Distribution Generalization on Molecular Graphs",
            authors="Sun et al.",
            year=2022,
            filename="sun2022_ood_molecular.pdf",
            pages=15,
            summary=(
                "Benchmarks GNN OOD performance under scaffold splits. Shows standard GNNs "
                "fail sharply when test scaffolds are disjoint from training, questioning deployment claims."
            ),
            key_findings=[
                "Scaffold split drops AUC by 15–30% vs random split",
                "Invariant risk minimization partially recovers OOD AUC",
                "Substructure frequency correlates with generalization gap",
            ],
        ),
    ]

    nodes = [
        DemoKnowledgeNode(
            id="n-mpnn",
            label="Message Passing NN",
            node_type="method",
            description="Iterative neighborhood aggregation on molecular graphs",
            source_papers=["paper-gilmer"],
        ),
        DemoKnowledgeNode(
            id="n-pretrain",
            label="GNN Pre-training",
            node_type="method",
            description="Self-supervised objectives on large unlabeled molecular graphs",
            source_papers=["paper-hu"],
        ),
        DemoKnowledgeNode(
            id="n-scaffold-split",
            label="Scaffold Split",
            node_type="concept",
            description="Train/test partition by Bemis-Murcko scaffolds to test OOD generalization",
            source_papers=["paper-sun"],
        ),
        DemoKnowledgeNode(
            id="n-qm9",
            label="QM9 Benchmark",
            node_type="finding",
            description="In-distribution quantum chemistry regression; strong MPNN baselines",
            evidence_tier="supported",
            source_papers=["paper-gilmer"],
        ),
        DemoKnowledgeNode(
            id="n-ood-gap",
            label="OOD Generalization Gap",
            node_type="finding",
            description="Large performance drop when molecular scaffolds differ between train and test",
            evidence_tier="supported",
            source_papers=["paper-sun"],
        ),
        DemoKnowledgeNode(
            id="n-pretrain-transfer",
            label="Transfer from Pre-training",
            node_type="finding",
            description="Pre-training improves low-data downstream tasks but OOD scaffold gains are mixed",
            evidence_tier="speculative",
            source_papers=["paper-hu", "paper-sun"],
        ),
        DemoKnowledgeNode(
            id="n-substructure",
            label="Substructure Frequency",
            node_type="concept",
            description="Rare substructures in test set predict larger generalization error",
            source_papers=["paper-sun"],
        ),
        DemoKnowledgeNode(
            id="n-gap-invariant",
            label="Invariant Representations",
            node_type="gap",
            description="No consensus on which invariances guarantee scaffold OOD robustness",
            evidence_tier="speculative",
        ),
        DemoKnowledgeNode(
            id="n-contradict-depth",
            label="Optimal Model Depth",
            node_type="contradiction",
            description="Gilmer: depth saturates at 4 layers; Hu: deeper pre-trained encoders help transfer",
            evidence_tier="contradicted",
            source_papers=["paper-gilmer", "paper-hu"],
        ),
    ]

    edges = [
        DemoKnowledgeEdge(id="e1", source="n-mpnn", target="n-qm9", relation="evaluated_on", strength=0.92),
        DemoKnowledgeEdge(id="e2", source="n-pretrain", target="n-pretrain-transfer", relation="enables", strength=0.78),
        DemoKnowledgeEdge(id="e3", source="n-scaffold-split", target="n-ood-gap", relation="reveals", strength=0.95),
        DemoKnowledgeEdge(id="e4", source="n-substructure", target="n-ood-gap", relation="explains", strength=0.81),
        DemoKnowledgeEdge(id="e5", source="n-mpnn", target="n-pretrain", relation="extended_by", strength=0.88),
        DemoKnowledgeEdge(id="e6", source="n-ood-gap", target="n-gap-invariant", relation="motivates", strength=0.74),
        DemoKnowledgeEdge(id="e7", source="n-contradict-depth", target="n-mpnn", relation="challenges", strength=0.65),
        DemoKnowledgeEdge(id="e8", source="n-pretrain-transfer", target="n-ood-gap", relation="partially_addresses", strength=0.55),
    ]

    notes = [
        DemoNote(
            id="note-1",
            title="MPNN as unified molecular encoder",
            body="Gilmer frames all GNN variants as message-passing. Edge networks critical for bond types.",
            tags=["architecture", "baseline"],
            linked_paper_id="paper-gilmer",
        ),
        DemoNote(
            id="note-2",
            title="Pre-training ≠ OOD fix",
            body="Hu pre-training helps data efficiency but Sun shows scaffold OOD remains hard. Need joint evaluation.",
            tags=["pre-training", "ood", "contradiction"],
            linked_paper_id="paper-sun",
        ),
        DemoNote(
            id="note-3",
            title="Substructure hypothesis",
            body="Track rare Murcko scaffolds in test set — correlate with AUC drop. Candidate feature for risk scoring.",
            tags=["hypothesis", "experiment"],
            linked_paper_id="paper-sun",
        ),
        DemoNote(
            id="note-4",
            title="Missing: ADMET multi-task",
            body="None of the three papers jointly evaluate hERG + solubility under scaffold split. Gap for our project.",
            tags=["gap", "admet"],
        ),
    ]

    contradictions = [
        DemoContradiction(
            id="c1",
            claim_a="GNN depth beyond 4 layers does not improve QM9 performance",
            claim_b="Deeper pre-trained GNN encoders improve downstream molecular property transfer",
            source_a="Gilmer et al. 2017",
            source_b="Hu et al. 2020",
            resolution=(
                "Context-dependent: depth helps representation learning at scale; "
                "from-scratch QM9 may saturate earlier. Test depth × pre-training interaction."
            ),
        ),
        DemoContradiction(
            id="c2",
            claim_a="Pre-training universally improves molecular GNN transfer",
            claim_b="Scaffold OOD gaps persist even with pre-trained encoders",
            source_a="Hu et al. 2020",
            source_b="Sun et al. 2022",
            resolution=(
                "Pre-training improves in-distribution and low-data regimes but does not "
                "eliminate scaffold shift. Invariant objectives may be required."
            ),
        ),
    ]

    gaps = [
        DemoGap(
            id="g1",
            area="ADMET multi-property OOD",
            description="No unified benchmark for hERG, solubility, and permeability under scaffold split",
            priority="high",
        ),
        DemoGap(
            id="g2",
            area="Substructure-aware invariance",
            description="Lack of architectures explicitly invariant to scaffold frequency shift",
            priority="high",
        ),
        DemoGap(
            id="g3",
            area="Evidence-backed deployment criteria",
            description="Industry claims of GNN readiness rarely report scaffold-split metrics",
            priority="medium",
        ),
    ]

    hypotheses = [
        DemoHypothesis(
            id="h1",
            statement="Pre-trained MPNN encoders reduce scaffold OOD error when fine-tuned with substructure-aware contrastive loss",
            rationale="Combines Hu pre-training with Sun's substructure correlation signal",
            confidence=0.72,
            status="proposed",
            experiment_id="exp-1",
        ),
        DemoHypothesis(
            id="h2",
            statement="Generalization gap scales linearly with test-scaffold novelty score",
            rationale="Sun correlates rare substructures with error; quantify with Murcko distance",
            confidence=0.68,
            status="testing",
            experiment_id="exp-2",
        ),
        DemoHypothesis(
            id="h3",
            statement="Depth beyond 6 layers hurts OOD performance without pre-training",
            rationale="Reconciles Gilmer depth saturation with transfer settings",
            confidence=0.55,
            status="proposed",
            experiment_id="exp-3",
        ),
    ]

    experiments = [
        DemoExperiment(
            id="exp-1",
            title="Substructure-contrastive fine-tuning",
            objective="Test if contrastive scaffold alignment improves OOD AUC on BBBP",
            method="MPNN encoder (Hu init) + scaffold-balanced contrastive head; scaffold split eval",
            expected_outcome="≥5% OOD AUC lift over fine-tune-only baseline",
            status="planned",
        ),
        DemoExperiment(
            id="exp-2",
            title="Scaffold novelty correlation study",
            objective="Quantify relationship between Murcko distance and per-molecule error",
            method="Compute scaffold distance histogram; Spearman vs prediction error on 5 MoleculeNet sets",
            expected_outcome="ρ > 0.4 on at least 3 datasets",
            status="planned",
        ),
        DemoExperiment(
            id="exp-3",
            title="Depth ablation under scaffold split",
            objective="Reconcile depth findings across papers under OOD protocol",
            method="Train MPNN depths 2–8, with/without pre-training; scaffold split on Tox21",
            expected_outcome="Optimal depth shifts +2 layers with pre-training",
            status="planned",
        ),
    ]

    timeline = [
        DemoTimelineEvent(
            id="t1", phase="setup", title="Project Created",
            description="Research question defined: GNN generalization across molecular scaffolds",
            timestamp_offset_sec=0, icon="📁",
        ),
        DemoTimelineEvent(
            id="t2", phase="ingest", title="Papers Uploaded",
            description="3 foundational papers ingested (Gilmer, Hu, Sun)",
            timestamp_offset_sec=15, icon="📄",
        ),
        DemoTimelineEvent(
            id="t3", phase="extract", title="Knowledge Extracted",
            description="9 concepts, 8 relationships, 12 key findings identified",
            timestamp_offset_sec=45, icon="🧠",
        ),
        DemoTimelineEvent(
            id="t4", phase="synthesize", title="Notes & Links Created",
            description="4 structured notes with cross-paper tags",
            timestamp_offset_sec=75, icon="📝",
        ),
        DemoTimelineEvent(
            id="t5", phase="analyze", title="Contradictions Detected",
            description="2 conflicting claims flagged with resolution paths",
            timestamp_offset_sec=105, icon="⚡",
        ),
        DemoTimelineEvent(
            id="t6", phase="discover", title="Gaps Identified",
            description="3 open research gaps ranked by priority",
            timestamp_offset_sec=130, icon="🔍",
        ),
        DemoTimelineEvent(
            id="t7", phase="hypothesize", title="Hypotheses Generated",
            description="3 testable hypotheses with confidence scores",
            timestamp_offset_sec=160, icon="💡",
        ),
        DemoTimelineEvent(
            id="t8", phase="plan", title="Experiments Planned",
            description="3 experiments designed with expected outcomes",
            timestamp_offset_sec=190, icon="🧪",
        ),
        DemoTimelineEvent(
            id="t9", phase="report", title="Research Report",
            description="Professional report synthesized with evidence classification",
            timestamp_offset_sec=220, icon="📊",
        ),
    ]

    report = DemoResearchReport(
        title="Generalization Limits of Graph Neural Networks for Molecular Property Prediction",
        abstract=(
            "We synthesize evidence from message-passing architectures, pre-training strategies, "
            "and out-of-distribution benchmarks to characterize when GNNs reliably support drug discovery "
            "workflows. Scaffold-split evaluation reveals persistent generalization gaps not resolved by "
            "standard pre-training alone. We propose three experiments combining substructure-aware "
            "contrastive learning with depth ablations under rigorous OOD protocols."
        ),
        sections=[
            DemoReportSection(
                heading="1. Introduction",
                content=(
                    "Graph neural networks have become the default encoder for molecular property prediction. "
                    "However, deployment in drug discovery requires generalization to novel chemical scaffolds — "
                    "a regime where standard random-split benchmarks overstate performance."
                ),
            ),
            DemoReportSection(
                heading="2. Evidence Summary",
                content=(
                    "Gilmer et al. established MPNNs as a unified framework with strong QM9 baselines. "
                    "Hu et al. demonstrated pre-training gains on data-scarce downstream tasks. "
                    "Sun et al. showed scaffold splits reduce AUC by 15–30%, with substructure frequency "
                    "as a predictive factor for error."
                ),
            ),
            DemoReportSection(
                heading="3. Contradictions & Open Questions",
                content=(
                    "Depth recommendations conflict across in-distribution and pre-trained transfer settings. "
                    "Pre-training improves low-data performance but does not eliminate scaffold OOD gaps. "
                    "No existing work jointly evaluates multi-property ADMET under scaffold split."
                ),
            ),
            DemoReportSection(
                heading="4. Proposed Research Program",
                content=(
                    "Experiment 1: Substructure-contrastive fine-tuning on BBBP scaffold split. "
                    "Experiment 2: Scaffold novelty correlation across MoleculeNet. "
                    "Experiment 3: Depth ablation with/without pre-training on Tox21."
                ),
            ),
            DemoReportSection(
                heading="5. Conclusion",
                content=(
                    "AXIOM identified actionable hypotheses and a phased experimental plan from three papers "
                    "in under four minutes. All claims are evidence-classified; contradictions are explicit. "
                    "This report is ready for lab review and pilot collaboration."
                ),
            ),
        ],
        generated_at="2026-08-06T10:04:00Z",
    )

    tour_steps = [
        DemoTourStep(
            id="s1", title="Welcome to AXIOM",
            body="This is a live research session. Watch AXIOM ingest papers, extract knowledge, and plan science — no slides required.",
            highlight="hero", duration_sec=6,
        ),
        DemoTourStep(
            id="s2", title="Research Question",
            body="Every project starts with a precise question. AXIOM keeps it visible as the north star.",
            highlight="question", duration_sec=7,
        ),
        DemoTourStep(
            id="s3", title="Paper Ingestion",
            body="Upload PDFs. AXIOM reads, extracts text, and surfaces summaries automatically.",
            highlight="papers", duration_sec=8,
        ),
        DemoTourStep(
            id="s4", title="Knowledge Graph",
            body="Concepts and relationships build in real time. Evidence tiers are always visible.",
            highlight="graph", duration_sec=9,
        ),
        DemoTourStep(
            id="s5", title="Structured Notes",
            body="Insights become searchable, tagged notes linked to source papers.",
            highlight="notes", duration_sec=7,
        ),
        DemoTourStep(
            id="s6", title="Contradictions",
            body="AXIOM flags conflicting claims across papers — with resolution paths, not hand-waving.",
            highlight="contradictions", duration_sec=8,
        ),
        DemoTourStep(
            id="s7", title="Research Gaps",
            body="Missing work is ranked by priority so you know where to contribute.",
            highlight="gaps", duration_sec=7,
        ),
        DemoTourStep(
            id="s8", title="Hypotheses",
            body="Testable hypotheses with confidence scores, grounded in extracted evidence.",
            highlight="hypotheses", duration_sec=8,
        ),
        DemoTourStep(
            id="s9", title="Experiment Plan",
            body="Concrete experiments with methods and expected outcomes — ready for the lab.",
            highlight="experiments", duration_sec=8,
        ),
        DemoTourStep(
            id="s10", title="Research Report",
            body="A professional report synthesizes everything. AXIOM remembers the full session.",
            highlight="report", duration_sec=10,
        ),
    ]

    return DemoState(
        project=project,
        papers=papers,
        knowledge_nodes=nodes,
        knowledge_edges=edges,
        notes=notes,
        contradictions=contradictions,
        gaps=gaps,
        hypotheses=hypotheses,
        experiments=experiments,
        timeline=timeline,
        report=report,
        tour_steps=tour_steps,
        stats={
            "papers_ingested": len(papers),
            "concepts_extracted": len(nodes),
            "relationships": len(edges),
            "notes_created": len(notes),
            "contradictions_found": len(contradictions),
            "gaps_identified": len(gaps),
            "hypotheses_generated": len(hypotheses),
            "experiments_planned": len(experiments),
            "elapsed_minutes": 4,
        },
    )
