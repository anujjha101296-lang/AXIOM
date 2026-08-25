import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AXIOM — Autonomous AI Research Operating System",
  description:
    "An autonomous research system for discovering, testing, and verifying new knowledge. AXIOM combines AI agents, scientific literature, computational experiments, knowledge graphs, and formal verification into one unified research environment.",
  keywords: [
    "AXIOM",
    "AI Research OS",
    "Autonomous Research",
    "Mathematical Discovery",
    "Lean 4 Verification",
    "SMT Z3 Solving",
    "Epistemic Knowledge Graph",
    "Formal Verification",
  ],
  openGraph: {
    title: "AXIOM — Autonomous AI Research Operating System",
    description:
      "An autonomous research system for discovering, testing, and verifying new knowledge. Combining AI agents, computational experiments, and formal proof verification.",
    type: "website",
    siteName: "AXIOM Research OS",
  },
  twitter: {
    card: "summary_large_image",
    title: "AXIOM — Autonomous AI Research Operating System",
    description: "An autonomous research system for discovering, testing, and verifying new knowledge.",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body style={{ margin: 0, padding: 0, backgroundColor: "#090d16" }}>{children}</body>
    </html>
  );
}
