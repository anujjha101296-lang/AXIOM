import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AXIOM Labs — AI Workspace for Frontier Mathematical Research",
  description:
    "AXIOM is the AI workspace for frontier mathematical and scientific research. Visualize knowledge graphs, verify proofs, search counterexamples, and track prize problem readiness.",
  keywords: ["AI research", "mathematical reasoning", "proof verification", "scientific discovery", "knowledge graph"],
  openGraph: {
    title: "AXIOM Labs — AI Workspace for Frontier Research",
    description: "The AI workspace for frontier mathematical and scientific research.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
      </head>
      <body>{children}</body>
    </html>
  );
}

