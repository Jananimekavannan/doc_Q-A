import React from "react";
import { ChevronRight } from "lucide-react";

export default function RagPipeline({ uploaded, isQuerying }) {
  const steps = [
    { num: "01", title: "Extract text", subtitle: "PDF / TXT loader", litWhen: true },
    { num: "02", title: "Create chunks", subtitle: "Context-aware splitting", litWhen: uploaded },
    { num: "03", title: "Retrieve", subtitle: "Semantic vector search", litWhen: uploaded || isQuerying },
    { num: "04", title: "Generate", subtitle: "Grounded LLM answer", litWhen: isQuerying || uploaded }
  ];

  return (
    <div className="pipeline-card">
      <div className="pipeline-top">
        <span className="pipeline-title">RAG PIPELINE</span>
        <span className="live-pill">LIVE</span>
      </div>

      <div className="pipeline-steps">
        {steps.map((s) => (
          <div key={s.num} className={`pipe-step-item ${s.litWhen ? "active" : ""}`}>
            <div className="pipe-step-num">{s.num}</div>
            <div className="pipe-step-info">
              <b>{s.title}</b>
              <span>{s.subtitle}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
