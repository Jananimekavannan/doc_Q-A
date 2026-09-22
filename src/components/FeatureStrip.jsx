import React from "react";
import { Search, ShieldCheck, Database, Sparkles } from "lucide-react";

export default function FeatureStrip() {
  const features = [
    {
      icon: <Search size={18} strokeWidth={2.2} />,
      title: "Semantic Retrieval",
      desc: "Finds meaning, not just keywords"
    },
    {
      icon: <ShieldCheck size={18} strokeWidth={2.2} />,
      title: "Document Grounded",
      desc: "Answers use retrieved context"
    },
    {
      icon: <Database size={18} strokeWidth={2.2} />,
      title: "Vector Powered",
      desc: "Embeddings + similarity search"
    },
    {
      icon: <Sparkles size={18} strokeWidth={2.2} />,
      title: "Simple by Design",
      desc: "Beginner-friendly RAG pipeline"
    }
  ];

  return (
    <section className="feature-strip">
      {features.map((f, idx) => (
        <div key={idx} className="feature-item">
          <div className="feature-icon-box">
            {f.icon}
          </div>
          <div className="feature-text">
            <b>{f.title}</b>
            <span>{f.desc}</span>
          </div>
        </div>
      ))}
    </section>
  );
}
