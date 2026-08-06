"use client";

import type { DemoTimelineEvent } from "@/lib/demo-types";

interface Props {
  events: DemoTimelineEvent[];
  activeIndex: number;
}

export default function ResearchTimeline({ events, activeIndex }: Props) {
  return (
    <ol className="demo-timeline" aria-label="Research progress timeline">
      {events.map((ev, i) => {
        const state =
          i < activeIndex ? "done" : i === activeIndex ? "active" : "pending";
        return (
          <li
            key={ev.id}
            className={`demo-timeline-item demo-timeline-${state}`}
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <span className="demo-timeline-dot" aria-hidden="true" />
            <span className="demo-timeline-icon">{ev.icon}</span>
            <div className="demo-timeline-body">
              <strong>{ev.title}</strong>
              <p>{ev.description}</p>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
