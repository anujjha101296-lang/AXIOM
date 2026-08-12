"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const features = [
  {
    num: "01",
    title: "Epistemic Knowledge Graph",
    desc: "Every theorem, lemma, definition, and conjecture lives in a typed, verifiable graph — with dependency edges, proof lineages, and epistemic status always visible.",
  },
  {
    num: "02",
    title: "Formal Proof Generation",
    desc: "Translate mathematical claims into Lean 4, Coq, and Isabelle proof scripts. Generate tactic suggestions and compile verification reports automatically.",
  },
  {
    num: "03",
    title: "SMT Counterexample Search",
    desc: "Run Z3-backed parameter sweeps over bounded domains to search for counterexamples to conjectures. Refutation results are stored and linked back to the graph.",
  },
  {
    num: "04",
    title: "MCTS Algebraic Proof Search",
    desc: "Monte Carlo Tree Search explores proof tactic sequences for algebraic identities. Successful proof paths are exported as compilable Lean 4 scripts.",
  },
  {
    num: "05",
    title: "Conjecture Generation Engine",
    desc: "Autonomously generate mathematically novel conjectures from patterns in the knowledge graph, scored by a novelty index and filtered for non-tautologies.",
  },
  {
    num: "06",
    title: "Scientific Capability Benchmarks",
    desc: "A live evaluation engine measuring 8 capability dimensions (L0–L5) with composite scoring, prize readiness tracking, and regression detection for every sprint.",
  },
];

const tracks = [
  {
    letter: "Track A",
    name: "Artificial Scientist",
    icon: "🧠",
    iconClass: "indigo",
    desc: "Long-term research infrastructure that continuously improves AXIOM's ability to reason formally about mathematics and generate novel scientific insights.",
    milestones: [
      "Formal proof compilation (Lean 4, Coq)",
      "MCTS proof search over open problems",
      "Zeta zero verification framework",
      "Autonomous conjecture discovery loop",
    ],
  },
  {
    letter: "Track B",
    name: "Research Workspace",
    icon: "🔬",
    iconClass: "violet",
    desc: "Tools that frontier researchers can use today — an interactive spatial canvas for inspecting knowledge graphs, tracing evidence, and validating reasoning.",
    milestones: [
      "Interactive knowledge graph canvas",
      "arXiv paper ingestion & parsing",
      "Verification status dashboard",
      "Collaborative research context sharing",
    ],
  },
  {
    letter: "Track C",
    name: "Organization & GTM",
    icon: "🚀",
    iconClass: "cyan",
    desc: "Build the company: early users, documentation, technical blog posts, and the credibility needed to attract researchers and funding.",
    milestones: [
      "Public landing page & waitlist",
      "Technical blog & research reports",
      "Institutional pilot programs",
      "YC-ready application materials",
    ],
  },
];

const milestones = [
  {
    time: "Month 1–2",
    active: true,
    title: "Foundation & MVP",
    items: [
      "Working research workspace",
      "Knowledge graph + arXiv ingestion",
      "SMT counterexample sweeps",
      "Website & waitlist live",
      "10–20 early research users",
    ],
  },
  {
    time: "Month 3–6",
    active: false,
    title: "Public Alpha",
    items: [
      "Formal proof pipeline (Lean 4)",
      "Conjecture discovery engine",
      "Scientific capability benchmarks",
      "First institutional pilots",
      "YC-ready technical demo",
    ],
  },
  {
    time: "Month 6–12",
    active: false,
    title: "Research Platform",
    items: [
      "Autonomous discovery loop",
      "Prize readiness tracking live",
      "First technical blog publications",
      "Growing research community",
    ],
  },
  {
    time: "Year 1–3",
    active: false,
    title: "Scientific Contributions",
    items: [
      "Original research feature contributions",
      "Expanding scientific domains",
      "Researcher trust & adoption",
      "Credible approaches to open problems",
    ],
  },
];

const metrics = [
  { value: "8", label: "Capability Dimensions Tracked" },
  { value: "32", label: "Automated Benchmarks" },
  { value: "6", label: "Prize Problems Scored" },
  { value: "L2", label: "Current Capability Level" },
];

export default function Home() {
  const router = useRouter();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (authMode === "register") {
        const res = await fetch(`${API_BASE}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || "Registration failed");
        }
        
        // Auto login after register
        const loginRes = await fetch(`${API_BASE}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ username: email, password }),
        });
        
        if (!loginRes.ok) throw new Error("Auto-login failed");
        
        const loginData = await loginRes.json();
        localStorage.setItem("token", loginData.access_token);
        router.push("/workspace");
      } else {
        const res = await fetch(`${API_BASE}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ username: email, password }),
        });
        
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || "Login failed");
        }
        
        const data = await res.json();
        localStorage.setItem("token", data.access_token);
        router.push("/workspace");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
  };

  return (
    <main>
      <a className="skip-link" href="#main-content">Skip to content</a>

      {showAuthModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 p-8 rounded-lg shadow-2xl w-full max-w-md relative">
            <button 
              onClick={() => setShowAuthModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              ✕
            </button>
            <h2 className="text-2xl font-bold text-white mb-2">
              {authMode === "login" ? "Welcome Back" : "Create Account"}
            </h2>
            <p className="text-slate-400 text-sm mb-6">
              {authMode === "login" 
                ? "Sign in to access your research workspace." 
                : "Join AXIOM to start your mathematical research."}
            </p>

            <form onSubmit={handleAuth} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Email</label>
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Password</label>
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white"
                  required
                />
              </div>
              
              {error && <div className="text-red-400 text-sm p-2 bg-red-400/10 rounded">{error}</div>}
              
              <button 
                type="submit" 
                disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 rounded transition-colors disabled:opacity-50"
              >
                {loading ? "Processing..." : (authMode === "login" ? "Sign In" : "Register")}
              </button>
            </form>

            <div className="mt-6 text-center text-sm text-slate-400">
              {authMode === "login" ? (
                <>Don't have an account? <button onClick={() => setAuthMode("register")} className="text-indigo-400 hover:text-indigo-300">Register</button></>
              ) : (
                <>Already have an account? <button onClick={() => setAuthMode("login")} className="text-indigo-400 hover:text-indigo-300">Sign in</button></>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Header ─────────────────────────────────────────────── */}
      <header className="site-header">
        <Link className="wordmark" href="/" aria-label="AXIOM home">
          <span className="wordmark-mark" aria-hidden="true">A</span>
          <span>AXIOM</span>
        </Link>
        <nav aria-label="Primary navigation" className="flex items-center gap-4">
          <a href="#platform">Platform</a>
          <a href="#roadmap">Roadmap</a>
          <a href="#mission">Mission</a>
          {isAuthenticated ? (
            <>
              <Link className="nav-link" href="/workspace">Dashboard</Link>
              <button onClick={handleLogout} className="text-slate-400 hover:text-white text-sm font-medium ml-4">Logout</button>
            </>
          ) : (
            <button 
              onClick={() => { setAuthMode("login"); setShowAuthModal(true); }} 
              className="text-white text-sm font-medium ml-4 border border-slate-700 px-3 py-1 rounded hover:bg-slate-800 transition-colors"
            >
              Sign In
            </button>
          )}
        </nav>
      </header>

      {/* ── Hero ───────────────────────────────────────────────── */}
      <section className="hero" id="main-content" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="eyebrow">AXIOM LABS · RESEARCH PLATFORM</p>
          <h1 id="hero-title">
            The AI workspace for{" "}
            <span className="gradient-text">frontier mathematical research.</span>
          </h1>
          <p className="hero-summary">
            AXIOM gives researchers an interactive environment to connect knowledge,
            explore hypotheses, verify proofs, and track their distance from the
            world's hardest open problems — with every reasoning step made visible.
          </p>
          <div className="hero-actions">
            {isAuthenticated ? (
              <Link className="btn btn-primary" href="/workspace">
                Open Workspace Dashboard →
              </Link>
            ) : (
              <button className="btn btn-primary" onClick={() => { setAuthMode("register"); setShowAuthModal(true); }}>
                Start Research Project →
              </button>
            )}
            <a className="btn btn-secondary" href="#platform">
              Explore the Platform
            </a>
          </div>
          <div className="status-badge">
            <span className="status-dot" aria-hidden="true" />
            In active development · Milestone 1 in progress
          </div>
        </div>

        {/* Terminal visual */}
        <div className="hero-visual" aria-label="AXIOM capability evaluation terminal output">
          <div className="terminal-card">
            <div className="terminal-header">
              <span className="dot dot-red" />
              <span className="dot dot-yellow" />
              <span className="dot dot-green" />
              <span className="terminal-title">axiom evaluation run</span>
            </div>
            <div className="terminal-body">
              <div><span className="t-dim">$</span> <span className="t-cmd">python -m axiom.evaluation.run_benchmarks</span></div>
              <div className="t-dim">══════════════════════════════════════</div>
              <div><span className="t-dim">[1/5]</span> <span className="t-bold">Math Reasoning</span> <span className="t-out">10/10 ✓</span></div>
              <div><span className="t-dim">[2/5]</span> <span className="t-bold">Proof Verification</span> <span className="t-out"> 7/7 ✓</span></div>
              <div><span className="t-dim">[3/5]</span> <span className="t-bold">Conjecture Gen</span> <span className="t-out">  5/5 ✓</span></div>
              <div><span className="t-dim">[4/5]</span> <span className="t-bold">Knowledge Quality</span> <span className="t-warn"> 3/5 ~</span></div>
              <div><span className="t-dim">[5/5]</span> <span className="t-bold">Research Planning</span> <span className="t-out"> 5/5 ✓</span></div>
              <div className="t-dim">──────────────────────────────────────</div>
              <div><span className="t-dim">Composite Score:</span> <span className="t-val">0.8010</span> <span className="t-out">▲ +8%</span></div>
              <div><span className="t-dim">Weakest Gap:</span> <span className="t-warn">Counterexample Search</span></div>
              <div><span className="t-dim">Prize Readiness:</span> <span className="t-val">Riemann 76→78</span></div>
              <div><span className="t-out">✓ No regressions detected · run saved</span></div>
            </div>
          </div>

          <div className="mini-cards">
            <div className="mini-card">
              <div className="mini-card-label">Composite Score</div>
              <div className="mini-card-value">0.80</div>
              <div className="mini-card-trend">↑ +8% this sprint</div>
            </div>
            <div className="mini-card">
              <div className="mini-card-label">Prize Readiness</div>
              <div className="mini-card-value">6/6</div>
              <div className="mini-card-sub">problems scored</div>
            </div>
            <div className="mini-card">
              <div className="mini-card-label">Benchmarks</div>
              <div className="mini-card-value">30/32</div>
              <div className="mini-card-trend">↑ passing</div>
            </div>
            <div className="mini-card">
              <div className="mini-card-label">Regressions</div>
              <div className="mini-card-value" style={{color: 'var(--emerald)'}}>0</div>
              <div className="mini-card-sub">detected this run</div>
            </div>
          </div>
        </div>
      </section>

      <div className="divider" />

      {/* ── Metrics Strip ──────────────────────────────────────── */}
      <div className="container" style={{padding: '0 clamp(20px,5vw,48px)', maxWidth: 'var(--max-w)', margin: '0 auto'}}>
        <div className="metrics-strip" role="list" aria-label="AXIOM platform metrics">
          {metrics.map(m => (
            <div className="metric-item" key={m.label} role="listitem">
              <div className="metric-value">{m.value}</div>
              <div className="metric-label">{m.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── 3 Parallel Tracks ──────────────────────────────────── */}
      <div className="section-full" id="platform">
        <section className="section" aria-labelledby="tracks-title">
          <div className="section-header">
            <p className="section-label">How We Build</p>
            <h2 className="section-title" id="tracks-title">
              Three parallel tracks,<br />
              <span className="gradient-text">progressing together.</span>
            </h2>
            <p className="section-subtitle">
              AXIOM doesn't wait until the research is done to build the product.
              Research, product, and company advance in parallel — each
              strengthening the others.
            </p>
          </div>

          <div className="track-grid">
            {tracks.map(t => (
              <article className="track-card" key={t.letter}>
                <div className={`track-icon ${t.iconClass}`} aria-hidden="true">
                  {t.icon}
                </div>
                <p className="track-letter">{t.letter}</p>
                <h3 className="track-name">{t.name}</h3>
                <p className="track-desc">{t.desc}</p>
                <div className="track-milestones" role="list">
                  {t.milestones.map(m => (
                    <div className="track-milestone" key={m} role="listitem">{m}</div>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>

      {/* ── Features ───────────────────────────────────────────── */}
      <section className="section" aria-labelledby="features-title">
        <div className="section-header">
          <p className="section-label">The Platform</p>
          <h2 className="section-title" id="features-title">
            Built for researchers who<br />
            <span className="gradient-text">demand exactness.</span>
          </h2>
          <p className="section-subtitle">
            Every AXIOM capability is designed to make reasoning explicit,
            verification visible, and scientific progress measurable.
          </p>
        </div>
        <div className="feature-grid">
          {features.map(f => (
            <article className="feature-card" key={f.num}>
              <p className="feature-num">{f.num}</p>
              <h3 className="feature-title">{f.title}</h3>
              <p className="feature-desc">{f.desc}</p>
            </article>
          ))}
        </div>
      </section>

      <div className="divider" />

      {/* ── Roadmap ────────────────────────────────────────────── */}
      <section className="section" id="roadmap" aria-labelledby="roadmap-title">
        <div className="section-header">
          <p className="section-label">Roadmap</p>
          <h2 className="section-title" id="roadmap-title">
            Where AXIOM is going.
          </h2>
          <p className="section-subtitle">
            Concrete milestones, not speculative timelines.
            Every milestone is verified against the SCEP benchmark suite.
          </p>
        </div>
        <div className="milestone-list">
          {milestones.map(m => (
            <div className="milestone-item" key={m.title}>
              <div className="milestone-time">{m.time}</div>
              <div className={`milestone-dot ${m.active ? 'active' : ''}`} aria-hidden="true" />
              <div className="milestone-body">
                <h3 className="milestone-title">{m.title}</h3>
                <div className="milestone-items">
                  {m.items.map(item => (
                    <span className="milestone-tag" key={item}>{item}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="divider" />

      {/* ── Mission ────────────────────────────────────────────── */}
      <div className="section-full" id="mission">
        <section className="section" aria-labelledby="mission-title">
          <div className="section-header centered">
            <p className="section-label">Mission</p>
            <h2 className="section-title" id="mission-title">
              We're not building a chatbot.<br />
              <span className="gradient-text">We're building a scientist.</span>
            </h2>
            <p className="section-subtitle">
              AXIOM optimizes for scientific capability, research quality, and
              verified discoveries — not features, users, or revenue. We believe
              the only honest measure of an AI research platform is whether it
              demonstrably brings humanity closer to solving difficult problems.
            </p>
          </div>
          <div className="track-grid">
            {[
              { icon: "📐", title: "Evaluation-First", desc: "Every sprint begins with benchmarks. Every epic ends with a Capability Delta Report. We only ship when we can prove we've improved." },
              { icon: "🔍", title: "Chief Skeptic Built-In", desc: "An independent audit layer challenges every score and rejects optimistic assumptions. Estimated capabilities are flagged. Verified ones are celebrated." },
              { icon: "🏆", title: "Prize-Backed Targets", desc: "The Clay Millennium Problems are our long-horizon capability tests, not product promises. Prize readiness scores guide every engineering decision." },
            ].map(p => (
              <article className="track-card" key={p.title}>
                <div className="track-icon indigo" style={{fontSize: '24px'}} aria-hidden="true">{p.icon}</div>
                <h3 className="track-name">{p.title}</h3>
                <p className="track-desc">{p.desc}</p>
              </article>
            ))}
          </div>
        </section>
      </div>

      {/* ── CTA ────────────────────────────────────────────────── */}
      <section className="cta-section" aria-labelledby="cta-title">
        <div className="cta-card">
          <p className="section-label" style={{marginBottom: '16px'}}>GET STARTED</p>
          <h2 id="cta-title">
            Join researchers building with AXIOM.
          </h2>
          <p>
            Get access to the research workspace, benchmark results,
            and our technical progress reports.
          </p>
          <div className="cta-actions mt-6">
            {isAuthenticated ? (
              <Link className="btn btn-primary" href="/workspace">
                Go to Workspace →
              </Link>
            ) : (
              <button className="btn btn-primary" onClick={() => { setAuthMode("register"); setShowAuthModal(true); }}>
                Create Account →
              </button>
            )}
            <a className="btn btn-ghost" href="https://github.com" rel="noopener" target="_blank">
              View on GitHub
            </a>
          </div>
        </div>
      </section>

      {/* ── Footer ─────────────────────────────────────────────── */}
      <footer>
        <div className="site-footer">
          <Link className="wordmark" href="/" aria-label="AXIOM home">
            <span className="wordmark-mark" aria-hidden="true">A</span>
            <span>AXIOM</span>
          </Link>
          <nav className="footer-links" aria-label="Footer navigation">
            <a href="/workspace">Workspace</a>
            <a href="#platform">Platform</a>
            <a href="#roadmap">Roadmap</a>
          </nav>
          <p className="footer-copy">© {new Date().getFullYear()} AXIOM Labs</p>
        </div>
      </footer>
    </main>
  );
}
