import Link from "next/link";

/** Verified platform facts — updated with capability audits, not marketing copy. */
const verifiedFacts = [
  { value: "280+", label: "Automated core tests" },
  { value: "7", label: "Research loops with health gates" },
  { value: "1", label: "Production-ready workspace UI" },
  { value: "0", label: "Fake metrics on this page" },
];

type CapabilityStatus = "live" | "partial" | "planned";

interface Capability {
  name: string;
  status: CapabilityStatus;
  description: string;
  href?: string;
}

const availableNow: Capability[] = [
  {
    name: "Research Workspace",
    status: "live",
    description:
      "Create projects, upload PDFs, take notes, full-text search, and Q&A sessions. The primary product surface today.",
    href: "/research",
  },
  {
    name: "Evidence & Reproducibility (E&R)",
    status: "live",
    description:
      "Claim registry, discovery gate, provenance graph, and reproduction engine with explicit verification states.",
  },
  {
    name: "Experiment Sandbox (SEC)",
    status: "live",
    description:
      "Sandboxed experiment execution with resource limits, lifecycle management, and safe failure handling.",
  },
  {
    name: "API Gateway",
    status: "live",
    description:
      "Unified HTTP entry point with health checks, optional auth, and mounted routers for all research loops.",
  },
];

const earlyAccess: Capability[] = [
  {
    name: "Formal Mathematics (FMTP)",
    status: "partial",
    description:
      "Formalization pipeline and proof compilation gate. Lean 4 required for real verification; other provers are stubs.",
  },
  {
    name: "Research Campaigns (FRCE)",
    status: "partial",
    description:
      "Campaign orchestration across research loops. API-complete; no dashboard UI yet.",
  },
  {
    name: "Knowledge Acquisition (SKAI)",
    status: "partial",
    description:
      "Knowledge graph, conflict/gap detection, and literature synthesis. Regex extraction; arXiv not fully wired.",
  },
  {
    name: "Graph Workspace",
    status: "partial",
    description:
      "Interactive knowledge graph canvas with arXiv ingestion and SMT/MCTS demos. Developer prototype.",
    href: "/workspace",
  },
  {
    name: "Model Routing (SIMR)",
    status: "partial",
    description:
      "Deterministic model and tool routing. Falls back to mock model without API keys (by design in v1).",
  },
];

const planned: Capability[] = [
  {
    name: "Campaign Dashboard UI",
    status: "planned",
    description: "Visual interface for long-running research campaigns. API exists; UI not built.",
  },
  {
    name: "Evidence Inspection UI",
    status: "planned",
    description: "Browse claims, provenance chains, and verification status in the browser.",
  },
  {
    name: "Public Waitlist",
    status: "planned",
    description:
      "Email capture for early access. Not implemented — use the research workspace directly for now.",
  },
  {
    name: "Full E2E Browser Suite",
    status: "planned",
    description: "226 browser tests exist but are excluded from CI pending harness work.",
  },
];

const healthGates = [
  { name: "CEL", target: "Core test suite", status: "pass" },
  { name: "E&R", target: "erl-health", status: "pass" },
  { name: "SIMR", target: "simr-health", status: "pass" },
  { name: "FMTP", target: "fmtp-health", status: "pass" },
  { name: "SEC", target: "sec-health", status: "pass" },
  { name: "FRCE", target: "frce-health", status: "pass" },
  { name: "SKAI", target: "skai-health", status: "pass" },
];

function StatusPill({ status }: { status: CapabilityStatus }) {
  const labels = { live: "Available now", partial: "Early access", planned: "Planned" };
  return <span className={`cap-pill cap-pill-${status}`}>{labels[status]}</span>;
}

function CapabilityCard({ cap }: { cap: Capability }) {
  const inner = (
    <>
      <div className="cap-card-header">
        <h3 className="cap-card-title">{cap.name}</h3>
        <StatusPill status={cap.status} />
      </div>
      <p className="cap-card-desc">{cap.description}</p>
      {cap.href && (
        <span className="cap-card-link">
          Open →
        </span>
      )}
    </>
  );

  if (cap.href) {
    return (
      <Link className="cap-card cap-card-clickable" href={cap.href}>
        {inner}
      </Link>
    );
  }
  return <article className="cap-card">{inner}</article>;
}

export default function Home() {
  return (
    <main>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>

      <header className="site-header">
        <Link className="wordmark" href="/" aria-label="AXIOM home">
          <span className="wordmark-mark" aria-hidden="true">
            A
          </span>
          <span>AXIOM</span>
        </Link>
        <nav aria-label="Primary navigation">
          <a href="#available">Capabilities</a>
          <a href="#honesty">Honesty</a>
          <a href="#health">Health</a>
          <Link className="nav-cta" href="/research">
            Research Workspace ↗
          </Link>
        </nav>
      </header>

      <section className="hero" id="main-content" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="eyebrow">AXIOM · AI RESEARCH PLATFORM</p>
          <h1 id="hero-title">
            An honest workspace for{" "}
            <span className="gradient-text">scientific research.</span>
          </h1>
          <p className="hero-summary">
            AXIOM is in active development. What you see here reflects what is
            actually implemented and tested — not aspirational marketing. Start
            with the research workspace, or explore the API-backed research loops
            behind it.
          </p>
          <div className="hero-actions">
            <Link className="btn btn-primary" href="/research">
              Open Research Workspace →
            </Link>
            <Link className="btn btn-secondary" href="/workspace">
              Graph Workspace (prototype)
            </Link>
            <a
              className="btn btn-secondary"
              href="https://github.com/anujjha101296-lang/AXIOM"
              rel="noopener noreferrer"
              target="_blank"
            >
              View source
            </a>
          </div>
          <div className="status-badge">
            <span className="status-dot" aria-hidden="true" />
            Early access · capabilities vary by loop
          </div>
        </div>

        <div className="hero-visual" aria-label="Verified platform facts">
          <div className="terminal-card">
            <div className="terminal-header">
              <span className="dot dot-red" />
              <span className="dot dot-yellow" />
              <span className="dot dot-green" />
              <span className="terminal-title">verified facts</span>
            </div>
            <div className="terminal-body">
              <div>
                <span className="t-dim">#</span>{" "}
                <span className="t-bold">Truth over theater</span>
              </div>
              <div className="t-dim">──────────────────────────────────────</div>
              <div>
                <span className="t-dim">tests:</span>{" "}
                <span className="t-out">280+ core passing</span>{" "}
                <span className="t-dim">(e2e excluded)</span>
              </div>
              <div>
                <span className="t-dim">loops:</span>{" "}
                <span className="t-out">7 health gates</span>{" "}
                <span className="t-dim">(make *-health)</span>
              </div>
              <div>
                <span className="t-dim">workspace:</span>{" "}
                <span className="t-out">/research live</span>
              </div>
              <div>
                <span className="t-dim">LLM Q&A:</span>{" "}
                <span className="t-warn">mock without API keys</span>
              </div>
              <div>
                <span className="t-dim">formal proofs:</span>{" "}
                <span className="t-warn">Lean optional; simulated fallback</span>
              </div>
              <div className="t-dim">──────────────────────────────────────</div>
              <div>
                <span className="t-dim">audit:</span>{" "}
                <span className="t-val">AXIOM_CAPABILITY_MATRIX.md</span>
              </div>
            </div>
          </div>

          <div className="mini-cards">
            {verifiedFacts.map((f) => (
              <div className="mini-card" key={f.label}>
                <div className="mini-card-label">{f.label}</div>
                <div className="mini-card-value">{f.value}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="divider" />

      <div className="container" style={{ padding: "0 clamp(20px,5vw,48px)", maxWidth: "var(--max-w)", margin: "0 auto" }}>
        <div className="metrics-strip" role="list" aria-label="Verified platform metrics">
          {verifiedFacts.map((m) => (
            <div className="metric-item" key={m.label} role="listitem">
              <div className="metric-value">{m.value}</div>
              <div className="metric-label">{m.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="section-full" id="available">
        <section className="section" aria-labelledby="available-title">
          <div className="section-header">
            <p className="section-label">Current capabilities</p>
            <h2 className="section-title" id="available-title">
              What works today.
            </h2>
            <p className="section-subtitle">
              Each item is classified by implementation state from the repository
              capability audit. We do not present planned features as shipped.
            </p>
          </div>

          <h3 className="cap-section-label">Available now</h3>
          <div className="cap-grid">
            {availableNow.map((cap) => (
              <CapabilityCard key={cap.name} cap={cap} />
            ))}
          </div>

          <h3 className="cap-section-label">Early access</h3>
          <div className="cap-grid">
            {earlyAccess.map((cap) => (
              <CapabilityCard key={cap.name} cap={cap} />
            ))}
          </div>

          <h3 className="cap-section-label">Planned</h3>
          <div className="cap-grid">
            {planned.map((cap) => (
              <CapabilityCard key={cap.name} cap={cap} />
            ))}
          </div>
        </section>
      </div>

      <section className="section" id="health" aria-labelledby="health-title">
        <div className="section-header">
          <p className="section-label">Verification</p>
          <h2 className="section-title" id="health-title">
            Health gates, not marketing metrics.
          </h2>
          <p className="section-subtitle">
            Each research loop has an executable health check. Run{" "}
            <code className="inline-code">make &lt;loop&gt;-health</code> locally
            to verify integration.
          </p>
        </div>
        <div className="health-grid">
          {healthGates.map((gate) => (
            <div className="health-card" key={gate.name}>
              <div className="health-card-name">{gate.name}</div>
              <div className="health-card-target">{gate.target}</div>
              <div className={`health-card-status health-${gate.status}`}>
                {gate.status === "pass" ? "Gate exists" : gate.status}
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="divider" />

      <div className="section-full" id="honesty">
        <section className="section" aria-labelledby="honesty-title">
          <div className="section-header centered">
            <p className="section-label">Principles</p>
            <h2 className="section-title" id="honesty-title">
              Truth over theater.
            </h2>
            <p className="section-subtitle">
              AXIOM optimizes for verified scientific capability — not demo
              metrics. Generated, simulated, and formally verified results are
              never conflated. If something is not built yet, we say so.
            </p>
          </div>
          <div className="track-grid">
            {[
              {
                icon: "✓",
                title: "Evidence-first",
                desc: "Every capability has acceptance criteria and executable verification. See VERIFICATION_STATUS.md and AXIOM_CAPABILITY_MATRIX.md.",
              },
              {
                icon: "◎",
                title: "Explicit limitations",
                desc: "Mock LLMs, simulated compilers, and subprocess sandboxes are labeled — not hidden behind polished UI.",
              },
              {
                icon: "→",
                title: "Start with research",
                desc: "The research workspace is the most complete product surface. Everything else supports or extends it.",
              },
            ].map((p) => (
              <article className="track-card" key={p.title}>
                <div className="track-icon indigo" style={{ fontSize: "24px" }} aria-hidden="true">
                  {p.icon}
                </div>
                <h3 className="track-name">{p.title}</h3>
                <p className="track-desc">{p.desc}</p>
              </article>
            ))}
          </div>
        </section>
      </div>

      <section className="cta-section" aria-labelledby="cta-title">
        <div className="cta-card">
          <p className="section-label" style={{ marginBottom: "16px" }}>
            GET STARTED
          </p>
          <h2 id="cta-title">Try the research workspace.</h2>
          <p>
            Create a project, upload a paper, search your notes, and run Q&A
            sessions. No waitlist required — the workspace is available now.
          </p>
          <div className="cta-actions">
            <Link className="btn btn-primary" href="/research">
              Open Research Workspace →
            </Link>
            <a
              className="btn btn-ghost"
              href="https://github.com/anujjha101296-lang/AXIOM"
              rel="noopener noreferrer"
              target="_blank"
            >
              View on GitHub
            </a>
          </div>
          <p className="cta-footnote">
            API documentation available at{" "}
            <code className="inline-code">localhost:8000/docs</code> when running
            locally with <code className="inline-code">make dev</code>.
          </p>
        </div>
      </section>

      <footer>
        <div className="site-footer">
          <Link className="wordmark" href="/" aria-label="AXIOM home">
            <span className="wordmark-mark" aria-hidden="true">
              A
            </span>
            <span>AXIOM</span>
          </Link>
          <nav className="footer-links" aria-label="Footer navigation">
            <Link href="/research">Research Workspace</Link>
            <Link href="/workspace">Graph Workspace</Link>
            <a href="#available">Capabilities</a>
          </nav>
          <p className="footer-copy">© {new Date().getFullYear()} AXIOM Labs · Early access</p>
        </div>
      </footer>
    </main>
  );
}
