import React from "react";
import { Sparkles } from "lucide-react";

export default function TypingIndicator() {
  return (
    <div className="message-row assistant">
      <div className="message-avatar assistant">
        <Sparkles size={16} strokeWidth={2.2} />
      </div>
      <div className="message-bubble typing-box">
        <div className="typing-dots">
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
        </div>
        <span className="typing-label">Retrieving context & generating answer…</span>
      </div>
    </div>
  );
}
