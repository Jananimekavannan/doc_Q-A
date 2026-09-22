import React from "react";
import { MessageSquareText, ChevronRight, Sparkles } from "lucide-react";

export default function EmptyChatState({ onSelectSuggestion, file, uploaded }) {
  const suggestions = [
    "Summarize this document",
    "What are the key points?",
    "What is the main topic?"
  ];

  return (
    <div className="chat-empty-state">
      <div className="orb-container">
        <MessageSquareText size={32} strokeWidth={1.8} />
      </div>

      <h3>Start a conversation with your document</h3>
      <p>
        Ask a question about the content you uploaded. DocuMind will retrieve relevant chunks and generate answers grounded in your document.
      </p>

      <div className="suggestions-wrap">
        <span className="suggestions-label">Suggested Questions</span>
        <div className="suggestion-chips">
          {suggestions.map((s) => (
            <button
              key={s}
              className="suggestion-chip"
              onClick={() => onSelectSuggestion(s)}
            >
              <span>{s}</span>
              <ChevronRight size={14} />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
