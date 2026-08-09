import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AXIOM — AI Research Platform (Early Access)",
  description:
    "AXIOM is an AI research platform in active development. Start with the research workspace — projects, PDFs, notes, search, and Q&A. Honest capability disclosure.",
  keywords: ["AI research", "research workspace", "scientific discovery", "evidence", "reproducibility"],
  openGraph: {
    title: "AXIOM — AI Research Platform",
    description: "An honest workspace for scientific research. Early access — see what actually works today.",
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

