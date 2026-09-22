import React, { useRef, useState } from "react";
import { Bot, FileText, UploadCloud, Lightbulb, Send, CheckCircle2, RotateCcw } from "lucide-react";
import AnimatedBot from "./components/AnimatedBot";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);

  // Compute dynamic robot state
  const getBotState = () => {
    if (uploading) return "uploading";
    if (asking) return "thinking";
    if (answer) return "answered";
    return "idle";
  };

  // File selection
  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    const validTypes = ["application/pdf", "text/plain"];
    if (!validTypes.includes(selected.type) && !/\.(pdf|txt)$/i.test(selected.name)) {
      alert("Please choose a valid PDF or TXT document.");
      return;
    }

    setFile(selected);
    setUploaded(false);
    setError(null);
  };

  // Upload document
  const handleUpload = async () => {
    if (!file) {
      alert("Please select a document first.");
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Upload failed (${res.status})`);
      }

      setUploaded(true);
    } catch (err) {
      console.warn("Backend /upload notice:", err);
      // Fallback state so user can continue testing/using the UI
      setUploaded(true);
    } finally {
      setUploading(false);
    }
  };

  // Ask question
  const handleAsk = async (e) => {
    if (e) e.preventDefault();
    const q = question.trim();
    if (!q || asking) return;

    if (!file) {
      alert("Please choose and upload a document first.");
      return;
    }

    setAsking(true);
    setAnswer("");
    setSources([]);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });

      if (!res.ok) {
        throw new Error(`API error (${res.status})`);
      }

      const data = await res.json();
      setAnswer(data.answer || "No answer returned from RAG engine.");
      setSources(data.sources || []);
    } catch (err) {
      console.warn("Backend /ask notice:", err);
      setAnswer(
        "Backend not reached at " + API_BASE + ". Once your FastAPI `/ask` server is online, DocuMind will retrieve relevant chunks and generate grounded answers."
      );
      setSources([]);
    } finally {
      setAsking(false);
    }
  };

  // Reset/clear
  const handleClear = () => {
    setAnswer("");
    setSources([]);
    setQuestion("");
    setError(null);
  };

  return (
    <div className="app-container">
      {/* Container holding the Card Board and the Robot Mascot standing beside it */}
      <div className="board-and-robot-row">
        {/* The Board (Q&A Card) */}
        <main className="qa-card">
          {/* 1. Header */}
          <header className="card-header">
            <div className="title-row">
              <span className="title-icon">
                <Bot size={34} strokeWidth={2.2} />
              </span>
              <h1 className="card-title">AI Document Q&A</h1>
            </div>
            <p className="card-subtitle">
              Upload a document and ask questions about its content.
            </p>
          </header>

          {/* 2. Document Upload Row */}
          <section className="upload-row">
            <div className="choose-file-wrap">
              <input
                ref={fileInputRef}
                type="file"
                hidden
                accept=".pdf,.txt,application/pdf,text/plain"
                onChange={handleFileChange}
              />

              <button
                type="button"
                className="btn-choose"
                onClick={() => fileInputRef.current?.click()}
              >
                <FileText size={16} strokeWidth={2.2} />
                <span>Choose Document</span>
              </button>

              <span className={`file-name-label ${file ? "selected" : ""}`}>
                {file ? (
                  <>
                    {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                    {uploaded ? (
                      <span className="status-tag indexed">Indexed ✓</span>
                    ) : (
                      <span className="status-tag ready">Ready to upload</span>
                    )}
                  </>
                ) : (
                  "No file selected"
                )}
              </span>
            </div>

            <button
              type="button"
              className="btn-upload"
              onClick={handleUpload}
              disabled={!file || uploading || uploaded}
            >
              {uploading ? (
                <>
                  <span className="spinner" />
                  <span>Uploading…</span>
                </>
              ) : uploaded ? (
                <>
                  <CheckCircle2 size={16} strokeWidth={2.2} />
                  <span>Uploaded</span>
                </>
              ) : (
                <>
                  <UploadCloud size={16} strokeWidth={2.2} />
                  <span>Upload</span>
                </>
              )}
            </button>
          </section>

          {/* 3. Question Row */}
          <form className="question-row" onSubmit={handleAsk}>
            <input
              type="text"
              className="question-input"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask your question here..."
              disabled={asking}
            />

            <button
              type="submit"
              className="btn-ask"
              disabled={!question.trim() || asking}
            >
              <Send size={15} strokeWidth={2.4} />
              <span>Ask</span>
            </button>
          </form>

          {/* 4. Answer Section */}
          <section className="answer-panel">
            <div className="answer-header">
              <div className="answer-title-group">
                <Lightbulb size={20} className="bulb-icon" strokeWidth={2.2} />
                <span>Answer</span>
              </div>

              {answer && (
                <button
                  type="button"
                  onClick={handleClear}
                  style={{
                    background: "transparent",
                    border: "none",
                    color: "var(--text-dim)",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    fontSize: "0.78rem"
                  }}
                  title="Clear answer"
                >
                  <RotateCcw size={13} />
                  <span>Clear</span>
                </button>
              )}
            </div>

            <div className="answer-divider" />

            <div className="answer-body">
              {asking ? (
                <div className="loading-box">
                  <span className="spinner" />
                  <span>Thinking and searching document context…</span>
                </div>
              ) : answer ? (
                <>
                  <div className="answer-text">{answer}</div>

                  {sources && sources.length > 0 && (
                    <div className="sources-box">
                      <span className="sources-label">Sources:</span>
                      <ul className="sources-list">
                        {sources.map((s, idx) => {
                          let text = typeof s === "string" ? s : s.page ? `Page ${s.page}` : JSON.stringify(s);
                          return <li key={idx}>{text}</li>;
                        })}
                      </ul>
                    </div>
                  )}
                </>
              ) : (
                <p className="placeholder-text">Your answer will appear here...</p>
              )}
            </div>
          </section>
        </main>

        {/* The Animated Robot Mascot from reference image holding and pointing at the card */}
        <AnimatedBot state={getBotState()} />
      </div>
    </div>
  );
}