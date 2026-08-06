"use client";

import Link from "next/link";
import type { AxiomOperationMode } from "@/lib/modes";

interface Props {
  mode: AxiomOperationMode;
  disclaimer: string;
  /** Compact strip for nested pages */
  compact?: boolean;
}

export default function OperationModeBanner({ mode, disclaimer, compact = false }: Props) {
  const isDemo = mode === "demo";

  return (
    <div
      className={`axiom-mode-banner axiom-mode-${mode}${compact ? " axiom-mode-compact" : ""}`}
      role="status"
      aria-live="polite"
      data-operation-mode={mode}
    >
      <div className="axiom-mode-banner-inner">
        <span className="axiom-mode-badge" aria-label={`${isDemo ? "Demo" : "Research"} Mode active`}>
          {isDemo ? "DEMO MODE" : "RESEARCH MODE"}
        </span>
        <p className="axiom-mode-text">{disclaimer}</p>
        {!compact && (
          <div className="axiom-mode-links">
            {isDemo ? (
              <Link href="/research" className="axiom-mode-link">
                Switch to Research Mode →
              </Link>
            ) : (
              <Link href="/demo" className="axiom-mode-link axiom-mode-link-demo">
                View presentation demo →
              </Link>
            )}
          </div>
        )}
      </div>
      <style jsx>{`
        .axiom-mode-banner {
          border-bottom: 2px solid;
          padding: 0.65rem 1.5rem;
          font-size: 0.85rem;
          line-height: 1.45;
        }
        .axiom-mode-demo {
          background: linear-gradient(90deg, rgba(245, 158, 11, 0.12), rgba(244, 63, 94, 0.08));
          border-color: rgba(245, 158, 11, 0.45);
          color: #fcd34d;
        }
        .axiom-mode-research {
          background: linear-gradient(90deg, rgba(34, 211, 238, 0.08), rgba(99, 102, 241, 0.08));
          border-color: rgba(34, 211, 238, 0.35);
          color: #a5f3fc;
        }
        .axiom-mode-compact {
          padding: 0.5rem 1rem;
          font-size: 0.8rem;
        }
        .axiom-mode-banner-inner {
          max-width: 1400px;
          margin: 0 auto;
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 0.75rem 1rem;
        }
        .axiom-mode-badge {
          font-size: 0.7rem;
          font-weight: 800;
          letter-spacing: 0.12em;
          padding: 0.25rem 0.6rem;
          border-radius: 6px;
          flex-shrink: 0;
        }
        .axiom-mode-demo .axiom-mode-badge {
          background: rgba(245, 158, 11, 0.25);
          color: #fbbf24;
          border: 1px solid rgba(245, 158, 11, 0.5);
        }
        .axiom-mode-research .axiom-mode-badge {
          background: rgba(34, 211, 238, 0.15);
          color: #22d3ee;
          border: 1px solid rgba(34, 211, 238, 0.4);
        }
        .axiom-mode-text {
          flex: 1;
          margin: 0;
          min-width: 200px;
          color: inherit;
          opacity: 0.95;
        }
        .axiom-mode-links {
          flex-shrink: 0;
        }
        .axiom-mode-link {
          color: #818cf8;
          text-decoration: none;
          font-weight: 600;
          font-size: 0.8rem;
          white-space: nowrap;
        }
        .axiom-mode-link:hover {
          text-decoration: underline;
        }
        .axiom-mode-link-demo {
          color: #fbbf24;
        }
      `}</style>
    </div>
  );
}
