"use client";

import type { DemoKnowledgeEdge, DemoKnowledgeNode } from "@/lib/demo-types";

const NODE_COLORS: Record<string, string> = {
  concept: "#6366f1",
  method: "#8b5cf6",
  finding: "#10b981",
  gap: "#f59e0b",
  contradiction: "#f43f5e",
};

interface Props {
  nodes: DemoKnowledgeNode[];
  edges: DemoKnowledgeEdge[];
  visible: boolean;
  animate?: boolean;
}

function layoutNodes(nodes: DemoKnowledgeNode[], width: number, height: number) {
  const cx = width / 2;
  const cy = height / 2;
  const r = Math.min(width, height) * 0.36;
  return nodes.map((n, i) => {
    const angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2;
    return {
      ...n,
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle),
    };
  });
}

export default function EvidenceGraph({ nodes, edges, visible, animate = true }: Props) {
  const W = 520;
  const H = 340;
  const positioned = layoutNodes(nodes, W, H);
  const posMap = Object.fromEntries(positioned.map((n) => [n.id, n]));

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className={`demo-graph-svg ${visible ? "demo-visible" : ""} ${animate ? "demo-animate" : ""}`}
      role="img"
      aria-label="Evidence knowledge graph"
    >
      <defs>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      {edges.map((e, i) => {
        const s = posMap[e.source];
        const t = posMap[e.target];
        if (!s || !t) return null;
        return (
          <g key={e.id} className="demo-edge-group" style={{ animationDelay: `${i * 80}ms` }}>
            <line
              x1={s.x}
              y1={s.y}
              x2={t.x}
              y2={t.y}
              stroke="rgba(99,102,241,0.35)"
              strokeWidth={1 + e.strength * 2}
            />
            <text
              x={(s.x + t.x) / 2}
              y={(s.y + t.y) / 2 - 4}
              fill="#5a5a80"
              fontSize="9"
              textAnchor="middle"
            >
              {e.relation.replace(/_/g, " ")}
            </text>
          </g>
        );
      })}
      {positioned.map((n, i) => (
        <g
          key={n.id}
          className="demo-node-group"
          style={{ animationDelay: `${i * 100 + 200}ms` }}
        >
          <circle
            cx={n.x}
            cy={n.y}
            r={22}
            fill={NODE_COLORS[n.node_type] || "#6366f1"}
            fillOpacity={0.2}
            stroke={NODE_COLORS[n.node_type] || "#6366f1"}
            strokeWidth={2}
            filter="url(#glow)"
          />
          <text
            x={n.x}
            y={n.y + 34}
            fill="#e8e8ef"
            fontSize="10"
            fontWeight="600"
            textAnchor="middle"
          >
            {n.label.length > 18 ? n.label.slice(0, 16) + "…" : n.label}
          </text>
          <text x={n.x} y={n.y + 4} fill="#fff" fontSize="8" textAnchor="middle" opacity={0.7}>
            {n.node_type}
          </text>
        </g>
      ))}
    </svg>
  );
}
