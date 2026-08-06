"use client";

import type { DemoTourStep } from "@/lib/demo-types";

interface Props {
  steps: DemoTourStep[];
  current: number;
  onNext: () => void;
  onPrev: () => void;
  onClose: () => void;
  onJump: (index: number) => void;
}

export default function InteractiveTour({
  steps,
  current,
  onNext,
  onPrev,
  onClose,
  onJump,
}: Props) {
  if (!steps.length) return null;
  const step = steps[current];
  const progress = ((current + 1) / steps.length) * 100;

  return (
    <div className="demo-tour-overlay" role="dialog" aria-label="Interactive tour">
      <div className="demo-tour-backdrop" onClick={onClose} aria-hidden="true" />
      <div className="demo-tour-card">
        <div className="demo-tour-progress">
          <div className="demo-tour-progress-bar" style={{ width: `${progress}%` }} />
        </div>
        <span className="demo-tour-step-count">
          Step {current + 1} of {steps.length}
        </span>
        <h3>{step.title}</h3>
        <p>{step.body}</p>
        <div className="demo-tour-dots">
          {steps.map((s, i) => (
            <button
              key={s.id}
              type="button"
              className={i === current ? "active" : ""}
              onClick={() => onJump(i)}
              aria-label={`Go to step ${i + 1}: ${s.title}`}
            />
          ))}
        </div>
        <div className="demo-tour-actions">
          <button type="button" className="demo-btn-ghost" onClick={onClose}>
            Skip tour
          </button>
          <div className="demo-tour-nav">
            <button
              type="button"
              className="demo-btn-secondary"
              onClick={onPrev}
              disabled={current === 0}
            >
              Back
            </button>
            <button
              type="button"
              className="demo-btn-primary"
              onClick={current === steps.length - 1 ? onClose : onNext}
            >
              {current === steps.length - 1 ? "Finish" : "Next"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
