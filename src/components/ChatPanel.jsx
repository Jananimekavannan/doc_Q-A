import React, { useRef, useEffect } from "react";
import { Search, RotateCcw } from "lucide-react";
import EmptyChatState from "./EmptyChatState";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import ChatComposer from "./ChatComposer";

export default function ChatPanel({
  messages,
  loading,
  question,
  setQuestion,
  ask,
  file,
  uploaded,
  onResetChat
}) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSelectSuggestion = (suggestion) => {
    if (!file) {
      alert("Please upload a document first.");
      return;
    }
    ask(suggestion);
  };

  return (
    <section className="panel-card chat-panel">
      <div className="panel-header">
        <div className="panel-title-wrap">
          <span className="step-chip">02</span>
          <h2>Document Q&A</h2>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.65rem" }}>
          {messages.length > 0 && (
            <button
              className="icon-action-btn"
              onClick={onResetChat}
              title="Clear chat history"
              aria-label="Clear chat history"
            >
              <RotateCcw size={15} />
            </button>
          )}
          <div className="retrieval-badge">
            <Search size={13} strokeWidth={2.2} />
            <span>Top-k retrieval</span>
          </div>
        </div>
      </div>

      <div className="chat-messages-container">
        {messages.length === 0 ? (
          <EmptyChatState
            onSelectSuggestion={handleSelectSuggestion}
            file={file}
            uploaded={uploaded}
          />
        ) : (
          <>
            {messages.map((m, idx) => (
              <MessageBubble key={idx} message={m} />
            ))}
            {loading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <ChatComposer
        question={question}
        setQuestion={setQuestion}
        onSend={ask}
        loading={loading}
        hasFile={Boolean(file)}
        isIndexed={uploaded}
      />
    </section>
  );
}
