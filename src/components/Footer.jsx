import React from "react";
import { Sparkles } from "lucide-react";

export default function Footer() {
  return (
    <footer>
      <div className="footer-brand">
        <Sparkles size={15} style={{ color: "var(--cyan-accent)" }} />
        <span>DocuMind</span>
      </div>
      <span className="footer-note">
        Built for focused document intelligence · AI RAG Document Q&A
      </span>
    </footer>
  );
}
