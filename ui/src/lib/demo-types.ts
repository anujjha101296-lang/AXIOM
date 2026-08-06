/** Types mirroring axiom/demo/schema.py */

export interface DemoPaper {
  id: string;
  title: string;
  authors: string;
  year: number;
  filename: string;
  pages: number;
  summary: string;
  key_findings: string[];
  status: string;
}

export interface DemoKnowledgeNode {
  id: string;
  label: string;
  node_type: string;
  description: string;
  evidence_tier: string;
  source_papers: string[];
}

export interface DemoKnowledgeEdge {
  id: string;
  source: string;
  target: string;
  relation: string;
  strength: number;
}

export interface DemoNote {
  id: string;
  title: string;
  body: string;
  tags: string[];
  linked_paper_id?: string;
}

export interface DemoHypothesis {
  id: string;
  statement: string;
  rationale: string;
  confidence: number;
  status: string;
  experiment_id?: string;
}

export interface DemoExperiment {
  id: string;
  title: string;
  objective: string;
  method: string;
  expected_outcome: string;
  status: string;
}

export interface DemoTimelineEvent {
  id: string;
  phase: string;
  title: string;
  description: string;
  timestamp_offset_sec: number;
  icon: string;
}

export interface DemoContradiction {
  id: string;
  claim_a: string;
  claim_b: string;
  source_a: string;
  source_b: string;
  resolution: string;
}

export interface DemoGap {
  id: string;
  area: string;
  description: string;
  priority: string;
}

export interface DemoReportSection {
  heading: string;
  content: string;
}

export interface DemoResearchReport {
  title: string;
  abstract: string;
  sections: DemoReportSection[];
  generated_at: string;
}

export interface DemoTourStep {
  id: string;
  title: string;
  body: string;
  highlight: string;
  duration_sec: number;
}

export interface DemoProject {
  id: string;
  name: string;
  description: string;
  research_question: string;
  created_at: string;
}

export interface DemoState {
  version: string;
  mode: string;
  project: DemoProject;
  papers: DemoPaper[];
  knowledge_nodes: DemoKnowledgeNode[];
  knowledge_edges: DemoKnowledgeEdge[];
  notes: DemoNote[];
  contradictions: DemoContradiction[];
  gaps: DemoGap[];
  hypotheses: DemoHypothesis[];
  experiments: DemoExperiment[];
  timeline: DemoTimelineEvent[];
  report: DemoResearchReport;
  tour_steps: DemoTourStep[];
  stats: Record<string, number>;
}

export type DemoPhase =
  | "intro"
  | "question"
  | "papers"
  | "extracting"
  | "graph"
  | "notes"
  | "contradictions"
  | "gaps"
  | "hypotheses"
  | "experiments"
  | "report"
  | "complete";

export const PHASE_ORDER: DemoPhase[] = [
  "intro",
  "question",
  "papers",
  "extracting",
  "graph",
  "notes",
  "contradictions",
  "gaps",
  "hypotheses",
  "experiments",
  "report",
  "complete",
];

export const PHASE_LABELS: Record<DemoPhase, string> = {
  intro: "Starting",
  question: "Research Question",
  papers: "Uploading Papers",
  extracting: "Extracting Knowledge",
  graph: "Building Graph",
  notes: "Creating Notes",
  contradictions: "Finding Contradictions",
  gaps: "Identifying Gaps",
  hypotheses: "Generating Hypotheses",
  experiments: "Planning Experiments",
  report: "Synthesizing Report",
  complete: "Complete",
};
