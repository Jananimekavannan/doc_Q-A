import React from "react";
import { Sparkles, User } from "lucide-react";
import SourceCard from "./SourceCard";

export default function MessageBubble({ message }) {
  const isAssistant = message.role === "assistant";

  return (
    <div className={`message-row ${message.role}`}>
      {isAssistant && (
        <div className="message-avatar assistant">
          <Sparkles size={16} strokeWidth={2.2} />
        </div>
      )}

      <div className="message-bubble">
        <div className="message-text">
          {message.text}
        </div>

        {isAssistant && message.sources && message.sources.length > 0 && (
          <SourceCard sources={message.sources} />
        )}
      </div>

      {!isAssistant && (
        <div className="message-avatar user">
          <User size={16} strokeWidth={2.2} />
        </div>
      )}
    </div>
  );
}
