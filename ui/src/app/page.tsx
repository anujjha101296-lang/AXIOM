const capabilityCards = [
  {
    title: "Research workspace",
    body: "A working interface for inspecting a research graph, tracing relationships, and keeping active investigation close to its evidence.",
  },
  {
    title: "Evidence graph",
    body: "Prototype knowledge storage connects mathematical claims, concepts, and publications so research context does not disappear into a chat transcript.",
  },
  {
    title: "Verification-aware workflows",
    body: "Experimental reasoning and proof tooling are designed to show what was generated, checked heuristically, simulated, or formally verified.",
  },
];

export default function Home() {
  return (
    <main>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>

      <header className="site-header">
        <Link className="wordmark" href="/" aria-label="AXIOM home">
          <span className="wordmark-mark" aria-hidden="true">A</span>
          <span>AXIOM</span>
        </Link>
        <nav aria-label="Primary navigation">
          <a href="#today">Today</a>
          <a href="#approach">Approach</a>
          <a className="nav-link-emphasis" href="/workspace">Open workspace <span aria-hidden="true">↗</span></a>
        </nav>
      </header>

      <section className="hero" id="main-content" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="eyebrow">AXIOM LABS · RESEARCH PLATFORM</p>
          <h1 id="hero-title">A workspace for frontier mathematical and scientific research.</h1>
          <p className="hero-summary">
            AXIOM helps researchers turn questions into inspectable work: connect knowledge,
            explore hypotheses, and keep verification status visible at every step.
          </p>
          <div className="hero-actions">
            <a className="button button-primary" href="/workspace">Explore the development workspace <span aria-hidden="true">→</span></a>
            <a className="button button-secondary" href="#today">See what exists today</a>
          </div>
          <p className="availability-note">
            <span className="status-dot" aria-hidden="true" /> In active research development. The workspace is a prototype, not a claim of autonomous scientific discovery.
          </p>
        </div>

        <div className="research-surface" aria-label="Illustration of an evidence graph with research artifacts">
          <div className="surface-topline">
            <span>RESEARCH CONTEXT</span>
            <span className="surface-live"><i aria-hidden="true" /> EVIDENCE-LED</span>
          </div>
          <div className="surface-grid" aria-hidden="true" />
          <div className="graph-line graph-line-one" aria-hidden="true" />
          <div className="graph-line graph-line-two" aria-hidden="true" />
          <div className="graph-line graph-line-three" aria-hidden="true" />
          <div className="graph-node graph-node-paper"><span>01</span><strong>Literature</strong><small>Source context</small></div>
          <div className="graph-node graph-node-claim"><span>02</span><strong>Claim</strong><small>Open question</small></div>
          <div className="graph-node graph-node-check"><span>03</span><strong>Check</strong><small>Status shown</small></div>
          <div className="surface-caption">
            <span className="caption-rule" aria-hidden="true" />
            Build a traceable path from source to claim.
          </div>
        </div>
      </section>

      <section className="section section-today" id="today" aria-labelledby="today-title">
        <div className="section-heading">
          <p className="eyebrow">THE PLATFORM TODAY</p>
          <h2 id="today-title">Useful research infrastructure, with its limits made clear.</h2>
        </div>
        <p className="section-intro">
          Our first technical wedge is mathematical intelligence. These capabilities are early-stage
          prototypes: they are being measured and improved, not presented as validated discoveries.
        </p>
        <div className="capability-grid">
          {capabilityCards.map((card, index) => (
            <article className="capability-card" key={card.title}>
              <span className="card-number">0{index + 1}</span>
              <h3>{card.title}</h3>
              <p>{card.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section approach-section" id="approach" aria-labelledby="approach-title">
        <div className="section-heading">
          <p className="eyebrow">HOW AXIOM WORKS</p>
          <h2 id="approach-title">Research should retain its reasoning.</h2>
        </div>
        <ol className="approach-list">
          <li>
            <span>01</span>
            <div><h3>Start with evidence</h3><p>Capture source material, assumptions, and the question before generating an answer.</p></div>
          </li>
          <li>
            <span>02</span>
            <div><h3>Explore bounded hypotheses</h3><p>Use computational tools to search, compare, and challenge specific claims—not to obscure uncertainty.</p></div>
          </li>
          <li>
            <span>03</span>
            <div><h3>Keep verification explicit</h3><p>Separate proposed, heuristic, simulated, independently checked, and formally verified results.</p></div>
          </li>
        </ol>
      </section>

      <section className="closing-section" aria-labelledby="closing-title">
        <p className="eyebrow">THE LONG VIEW</p>
        <h2 id="closing-title">Build the organization that can make real discoveries.</h2>
        <p>
          AXIOM is building toward a durable scientific discovery platform. Prize-backed problems are
          a long-horizon capability test—not a product promise or a solved claim.
        </p>
        <a className="button button-primary" href="/workspace">View the prototype workspace <span aria-hidden="true">→</span></a>
      </section>

      <footer className="site-footer">
        <Link className="wordmark" href="/" aria-label="AXIOM home"><span className="wordmark-mark" aria-hidden="true">A</span><span>AXIOM</span></Link>
        <p>Evidence-led tools for difficult problems.</p>
        <p>© {new Date().getFullYear()} AXIOM Labs</p>
      </footer>
    </main>
  );
}
import Link from "next/link";
