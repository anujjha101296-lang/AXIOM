"use client";

import type { DemoExperiment, DemoHypothesis, DemoPaper } from "@/lib/demo-types";

interface Props {
  projectName: string;
  papers: DemoPaper[];
  hypotheses: DemoHypothesis[];
  experiments: DemoExperiment[];
  visibleDepth: number;
}

export default function ResearchTree({
  projectName,
  papers,
  hypotheses,
  experiments,
  visibleDepth,
}: Props) {
  const expMap = Object.fromEntries(experiments.map((e) => [e.id, e]));

  return (
    <div className="demo-tree" role="tree" aria-label="Research tree">
      <div className={`demo-tree-node demo-tree-root ${visibleDepth >= 1 ? "demo-visible" : ""}`}>
        <span className="demo-tree-icon">📁</span>
        <span className="demo-tree-label">{projectName}</span>
      </div>
      <div className="demo-tree-children">
        {papers.map((p, i) => (
          <div
            key={p.id}
            className={`demo-tree-node ${visibleDepth >= 2 ? "demo-visible" : ""}`}
            style={{ animationDelay: `${i * 120}ms` }}
          >
            <span className="demo-tree-line" />
            <span className="demo-tree-icon">📄</span>
            <span className="demo-tree-label">{p.title}</span>
            <span className="demo-tree-meta">{p.authors} · {p.year}</span>
          </div>
        ))}
        {hypotheses.map((h, i) => (
          <div
            key={h.id}
            className={`demo-tree-node demo-tree-hyp ${visibleDepth >= 3 ? "demo-visible" : ""}`}
            style={{ animationDelay: `${i * 150}ms` }}
          >
            <span className="demo-tree-line" />
            <span className="demo-tree-icon">💡</span>
            <span className="demo-tree-label">{h.statement.slice(0, 60)}…</span>
            <span className="demo-tree-badge">{Math.round(h.confidence * 100)}%</span>
            {h.experiment_id && expMap[h.experiment_id] && visibleDepth >= 4 && (
              <div className="demo-tree-child-exp demo-visible">
                <span className="demo-tree-icon">🧪</span>
                <span className="demo-tree-label">{expMap[h.experiment_id].title}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
