import React from "react";
import { BookOpen, FileText, ExternalLink, Bookmark } from "lucide-react";

export default function SourceCard({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="sources-container">
      <div className="sources-header">
        <BookOpen size={14} strokeWidth={2.2} />
        <span>Retrieved Sources ({sources.length})</span>
      </div>

      <div className="sources-list">
        {sources.map((src, idx) => {
          let pageLabel = `Source ${idx + 1}`;
          let passageText = "";

          if (typeof src === "string") {
            // Check if string contains "Page X" or similar
            const pageMatch = src.match(/page\s*(\d+)/i);
            if (pageMatch) {
              pageLabel = `Page ${pageMatch[1]}`;
            }
            passageText = src;
          } else if (typeof src === "object" && src !== null) {
            if (src.page) {
              pageLabel = `Page ${src.page}`;
            } else if (src.source) {
              pageLabel = String(src.source);
            }
            passageText = src.content || src.text || src.passage || JSON.stringify(src);
          }

          return (
            <div key={idx} className="source-item">
              <div className="source-meta-row">
                <span className="source-tag">
                  <FileText size={13} />
                  <span>{pageLabel}</span>
                </span>
                <Bookmark size={13} opacity={0.6} />
              </div>
              {passageText && (
                <p className="source-snippet">
                  "{passageText.length > 220 ? passageText.slice(0, 220) + "…" : passageText}"
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
