"use client";

import { FormEvent, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Run = {
  run_id: string;
  question: { text: string; model: string; max_experiments: number; allowed_rho: number[] };
  hypothesis?: { statement: string; rationale: string } | null;
  plans: Array<{ rho: number; horizon: number; dts: number[] }>;
  evidence: Array<{
    experiment_id: string;
    evidence_tier: string;
    content_sha256: string;
    provenance: { input_digest_sha256?: string };
    convergence: Array<{ reference_error: number | null }>;
    independent_check: { relative_error: number; finite: boolean };
  }>;
  critiques: Array<{ verdict: string; concerns: string[]; next_actions: string[] }>;
  stage: string;
  transitions: Array<{ stage: string; action: string; detail: string }>;
  conclusion?: string | null;
};

type Benchmark = {
  benchmark: string;
  rho: number;
  experiment_id: string;
  convergence: Array<{ reference_error: number | null }>;
  independent_check: { relative_error: number; finite: boolean };
  provenance: { input_digest_sha256?: string };
  critic: { verdict: string; severity: string; checks: Record<string, boolean>; concerns: string[]; next_actions: string[] };
};

export default function ScientificResearchPage() {
  const [token, setToken] = useState("axiom-dev-token");
  const [question, setQuestion] = useState(
    "Investigate sensitivity and transition toward chaotic behavior in the Lorenz system."
  );
  const [maxExperiments, setMaxExperiments] = useState(3);
  const [run, setRun] = useState<Run | null>(null);
  const [benchmark, setBenchmark] = useState<Benchmark | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function startResearch(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setRun(null);
    try {
      const response = await fetch(`${API_BASE}/api/v1/science/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          question,
          model: "lorenz",
          max_experiments: maxExperiments,
          allowed_rho: [20, 24, 28, 32, 40],
        }),
      });
      if (!response.ok) throw new Error((await response.text()) || `Request failed (${response.status})`);
      setRun(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Research request failed");
    } finally {
      setBusy(false);
    }
  }

  async function runBenchmark() {
    setBusy(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/api/v1/science/benchmark/lorenz`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error((await response.text()) || `Benchmark failed (${response.status})`);
      setBenchmark(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Benchmark request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="science-shell">
      <header className="science-header">
        <div>
          <div className="eyebrow">AXIOM / SCIENTIFIC RUNTIME</div>
          <h1>Scientific Research Workspace</h1>
          <p>Bounded computational research with explicit evidence, critique, and provenance.</p>
        </div>
        <div className="stage-pill">{run?.stage ?? "READY"}</div>
      </header>

      <section className="science-grid">
        <form className="panel launch-panel" onSubmit={startResearch}>
          <div className="panel-heading">
            <div><span className="kicker">01</span><h2>Research question</h2></div>
            <span className="runtime-tag">LORENZ / DETERMINISTIC</span>
          </div>
          <label>
            Question
            <textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows={6} />
          </label>
          <div className="control-row">
            <label>
              Experiment budget
              <select value={maxExperiments} onChange={(e) => setMaxExperiments(Number(e.target.value))}>
                {[1, 2, 3, 4, 5].map((n) => <option key={n} value={n}>{n} experiments</option>)}
              </select>
            </label>
            <div className="bounds"><span>Allowed ρ</span><strong>20 · 24 · 28 · 32 · 40</strong></div>
          </div>
          <button disabled={busy || question.trim().length < 5} type="submit">
            {busy ? "Running scientific runtime…" : "Start bounded investigation"}
          </button>
          <button className="secondary" disabled={busy} type="button" onClick={runBenchmark}>
            Run evidence benchmark
          </button>
          <label className="token-field">
            API token
            <input value={token} onChange={(e) => setToken(e.target.value)} type="password" autoComplete="off" />
          </label>
          {error && <div className="error">{error}</div>}
        </form>

        <section className="panel evidence-panel">
          <div className="panel-heading"><div><span className="kicker">02</span><h2>Research state</h2></div></div>
          {!run ? (
            <div className="empty">Start an investigation to populate hypotheses, experiments, critic decisions, and evidence.</div>
          ) : (
            <>
              <div className="run-id">{run.run_id}</div>
              <div className="hypothesis"><span>HYPOTHESIS</span><p>{run.hypothesis?.statement}</p></div>
              <div className="timeline">
                {run.transitions.map((item, index) => (
                  <div className="timeline-item" key={`${item.action}-${index}`}>
                    <span className="dot" /><div><strong>{item.stage}</strong><span>{item.action}</span><p>{item.detail}</p></div>
                  </div>
                ))}
              </div>
            </>
          )}
        </section>
      </section>

      {run && (
        <section className="panel result-panel">
          <div className="panel-heading"><div><span className="kicker">03</span><h2>Evidence ledger</h2></div><span className="evidence-badge">{run.evidence.length} experiment(s)</span></div>
          <div className="experiment-list">
            {run.evidence.map((evidence, index) => {
              const critique = run.critiques[index];
              const minError = evidence.convergence.reduce<number | null>((best, point) => {
                if (point.reference_error == null) return best;
                return best == null ? point.reference_error : Math.min(best, point.reference_error);
              }, null);
              return (
                <article className="experiment" key={evidence.experiment_id}>
                  <div className="experiment-top"><strong>Experiment {index + 1}</strong><span>{critique?.verdict ?? "UNKNOWN"}</span></div>
                  <div className="metrics">
                    <div><span>ρ</span><strong>{run.plans[index]?.rho}</strong></div>
                    <div><span>Evidence</span><strong>{evidence.evidence_tier}</strong></div>
                    <div><span>Best convergence error</span><strong>{minError == null ? "—" : minError.toExponential(2)}</strong></div>
                    <div><span>Independent relative error</span><strong>{evidence.independent_check.relative_error.toExponential(2)}</strong></div>
                  </div>
                  <div className="hashes"><code>content {evidence.content_sha256}</code><code>provenance {evidence.provenance.input_digest_sha256 ?? "—"}</code></div>
                  {critique?.concerns?.length ? <div className="concerns">{critique.concerns.map((item) => <span key={item}>{item}</span>)}</div> : null}
                </article>
              );
            })}
          </div>
          <div className="conclusion"><span>CONCLUSION</span><p>{run.conclusion}</p></div>
        </section>
      )}

      {benchmark && (
        <section className="panel benchmark-panel">
          <div className="panel-heading"><div><span className="kicker">04</span><h2>Benchmark result</h2></div><span className="evidence-badge">{benchmark.critic.verdict}</span></div>
          <div className="benchmark-result"><strong>{benchmark.critic.verdict === "ACCEPT_NUMERICAL_EVIDENCE" ? "PASS" : "FAIL"}</strong><span>{benchmark.benchmark} · rho={benchmark.rho} · {benchmark.experiment_id}</span></div>
          <div className="hashes"><code>provenance {benchmark.provenance.input_digest_sha256 ?? "—"}</code><code>independent relative error {benchmark.independent_check.relative_error.toExponential(2)}</code></div>
        </section>
      )}

      <style jsx>{`
        .science-shell{min-height:100vh;padding:48px;max-width:1440px;margin:0 auto;color:#111;background:#f7f7f5}
        .science-header{display:flex;justify-content:space-between;gap:32px;align-items:flex-start;margin-bottom:32px}.eyebrow,.kicker{font-size:11px;letter-spacing:.14em;font-weight:700;color:#777}.science-header h1{font-size:42px;letter-spacing:-.04em;margin:8px 0}.science-header p{color:#666;margin:0}.stage-pill,.evidence-badge,.runtime-tag{border:1px solid #d5d5d0;border-radius:999px;padding:8px 12px;font-size:11px;letter-spacing:.08em;font-weight:700;background:#fff}
        .science-grid{display:grid;grid-template-columns:1fr 1.35fr;gap:20px}.panel{background:#fff;border:1px solid #deded8;border-radius:18px;padding:24px;box-shadow:0 8px 30px rgba(0,0,0,.035);margin-bottom:20px}.panel-heading{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:22px}.panel-heading h2{font-size:21px;margin:5px 0 0;letter-spacing:-.02em}.kicker{display:block;color:#aaa}.launch-panel label{display:flex;flex-direction:column;gap:8px;font-size:12px;font-weight:700;color:#555;margin-bottom:18px}.launch-panel textarea,.launch-panel select,.launch-panel input{font:inherit;border:1px solid #d8d8d2;border-radius:10px;padding:12px;background:#fafaf8;color:#111;outline:none}.token-field{margin-top:18px}.control-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}.bounds{border:1px dashed #ccc;padding:12px;border-radius:10px;display:flex;flex-direction:column;justify-content:center;gap:5px;font-size:11px;color:#777}.bounds strong{font-size:13px;color:#222}.launch-panel button{width:100%;border:0;border-radius:10px;padding:13px;margin-top:4px;background:#111;color:#fff;font-weight:700;cursor:pointer}.launch-panel button:disabled{opacity:.45;cursor:wait}.launch-panel .secondary{background:#f0f0eb;color:#222}.error{margin-top:14px;padding:10px;border-radius:9px;background:#fff0f0;color:#a22;font-size:12px}.empty{min-height:300px;display:grid;place-items:center;text-align:center;color:#888;font-size:13px}.run-id{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;color:#777;margin-bottom:18px}.hypothesis{border-left:3px solid #111;padding:2px 0 2px 14px;margin-bottom:24px}.hypothesis span,.conclusion>span{font-size:10px;letter-spacing:.12em;font-weight:800;color:#888}.hypothesis p{margin:7px 0;line-height:1.55}.timeline{display:flex;flex-direction:column}.timeline-item{display:grid;grid-template-columns:18px 1fr;gap:10px;position:relative;padding-bottom:18px}.timeline-item:not(:last-child):before{content:"";position:absolute;left:5px;top:11px;bottom:0;width:1px;background:#ddd}.dot{width:10px;height:10px;border:2px solid #111;border-radius:50%;background:#fff;z-index:1}.timeline-item strong{font-size:11px;margin-right:8px}.timeline-item span{font-size:11px;color:#777}.timeline-item p{font-size:12px;color:#666;margin:5px 0 0;line-height:1.45}.experiment-list{display:flex;flex-direction:column;gap:12px}.experiment{border:1px solid #e2e2dc;border-radius:12px;padding:16px}.experiment-top{display:flex;justify-content:space-between;gap:10px;margin-bottom:14px}.experiment-top span{font-size:10px;font-weight:800;letter-spacing:.08em}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.metrics div{background:#f7f7f4;border-radius:9px;padding:10px}.metrics span{display:block;font-size:10px;color:#888;margin-bottom:5px}.metrics strong{font-size:13px}.hashes{display:grid;gap:4px;margin-top:12px}.hashes code{font-size:9px;color:#777;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.concerns{display:flex;gap:6px;flex-wrap:wrap;margin-top:12px}.concerns span{font-size:10px;padding:5px 7px;background:#f2f2ed;border-radius:999px;color:#666}.conclusion{margin-top:18px;padding-top:18px;border-top:1px solid #e2e2dc}.conclusion p{margin:7px 0 0;line-height:1.55}.benchmark-result{display:flex;align-items:center;gap:16px}.benchmark-result strong{font-size:28px}.benchmark-result span{font-size:12px;color:#666}
        @media(max-width:900px){.science-shell{padding:24px}.science-grid{grid-template-columns:1fr}.metrics{grid-template-columns:1fr 1fr}.science-header{flex-direction:column}.science-header h1{font-size:32px}}
      `}</style>
    </main>
  );
}
