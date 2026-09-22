import React from "react";
import { Send, ShieldCheck, AlertCircle } from "lucide-react";

export default function ChatComposer({
  question,
  setQuestion,
  onSend,
  loading,
  hasFile,
  isIndexed
}) {
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (hasFile && question.trim() && !loading) {
        onSend();
      }
    }
  };

  const isInputDisabled = !hasFile || loading;
  const isSendDisabled = !hasFile || !question.trim() || loading;

  let placeholderText = "Ask anything about your document…";
  if (!hasFile) {
    placeholderText = "Upload a document on the left to start asking questions…";
  } else if (!isIndexed) {
    placeholderText = "Index your document or ask a question…";
  }

  return (
    <div className="composer-section">
      {!hasFile && (
        <div className="composer-banner">
          <AlertCircle size={14} />
          <span>Upload a document to unlock natural language Q&A</span>
        </div>
      )}

      <div className={`composer-input-box ${isInputDisabled ? "disabled" : ""}`}>
        <input
          type="text"
          className="composer-input"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholderText}
          disabled={isInputDisabled}
        />

        <button
          className="composer-send-btn"
          onClick={() => onSend()}
          disabled={isSendDisabled}
          title="Send question (Enter)"
          aria-label="Send question"
        >
          <Send size={16} strokeWidth={2.2} />
        </button>
      </div>

      <div className="composer-footer">
        <div className="composer-grounded-note">
          <ShieldCheck size={14} strokeWidth={2.2} />
          <span>Answers grounded in retrieved context</span>
        </div>
        <span>Press <kbd style={{ fontFamily: "var(--font-mono)", background: "rgba(255,255,255,0.06)", padding: "1px 5px", borderRadius: "4px" }}>Enter ↵</kbd> to send</span>
      </div>
    </div>
  );
}
