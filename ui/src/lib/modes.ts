/**
 * AXIOM operation modes — Demo vs Research honesty contract.
 * Demo Mode must never be confused with live scientific capability.
 */

export type AxiomOperationMode = "demo" | "research";

export interface OperationModeContract {
  mode: AxiomOperationMode;
  label: string;
  purpose: string;
  data_source: string;
  uses_live_models: boolean;
  uses_curated_data: boolean;
  deterministic: boolean;
  represents_scientific_capability: boolean;
  uncertainty_expected: boolean;
  disclaimer: string;
  evidence_required: boolean;
  suitable_for: string[];
}

export interface DemoOperationModeInfo {
  mode: "demo";
  label: string;
  represents_scientific_capability: boolean;
  data_source: string;
  disclaimer: string;
  suitable_for: string[];
}

/** Static fallback when API is unavailable — keeps honesty contract visible. */
export const DEMO_MODE_FALLBACK: OperationModeContract = {
  mode: "demo",
  label: "Demo Mode",
  purpose: "Presentation reliability for conferences, investors, YC interviews, and onboarding.",
  data_source: "Curated sample dataset (pre-authored, in-memory). Not live ingestion.",
  uses_live_models: false,
  uses_curated_data: true,
  deterministic: true,
  represents_scientific_capability: false,
  uncertainty_expected: false,
  disclaimer:
    "DEMO MODE — All outputs on this page are curated for presentation reliability. " +
    "They do not represent live AI reasoning, measured scientific capability, or verified research results.",
  evidence_required: false,
  suitable_for: ["conferences", "investor presentations", "YC interviews", "onboarding"],
};

export const RESEARCH_MODE_FALLBACK: OperationModeContract = {
  mode: "research",
  label: "Research Mode",
  purpose: "Real scientific work with live documents, models, and honest uncertainty.",
  data_source: "Live user uploads (PDFs), SQLite persistence, ModelClient inference.",
  uses_live_models: true,
  uses_curated_data: false,
  deterministic: false,
  represents_scientific_capability: true,
  uncertainty_expected: true,
  disclaimer:
    "RESEARCH MODE — Live PDFs, real retrieval, and actual AI models. Results may be incomplete, " +
    "uncertain, or incorrect. Verify every claim against source documents.",
  evidence_required: true,
  suitable_for: ["daily researcher workflows", "lab pilots", "paper reading"],
};
