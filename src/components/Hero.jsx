import React from "react";
import { ShieldCheck, Sparkles } from "lucide-react";

export default function Hero() {
  return (
    <section className="hero">
      <div className="hero-left">
        <div className="badge-row">
          <div className="eyebrow-pill">
            <span className="eyebrow-dot" />
            <span>PRIVATE DOCUMENT Q&A</span>
          </div>
        </div>

        <h1>
          Ask your documents.<br />
          <span className="gradient-text">Get grounded answers.</span>
        </h1>

        <p className="hero-copy">
          Upload a document, ask questions in natural language, and get answers grounded in the content you provide. DocuMind retrieves the most relevant passages before generating responses.
        </p>
      </div>

      <div className="hero-trust-badge">
        <div className="trust-icon-box">
          <ShieldCheck size={22} strokeWidth={2.2} />
        </div>
        <div className="trust-content">
          <b>Context-first AI</b>
          <span>Answers are grounded strictly in your uploaded document</span>
        </div>
      </div>
    </section>
  );
}
