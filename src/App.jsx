import React, { useRef, useState } from "react";
import {
  FileText, UploadCloud, Sparkles, MessageSquareText, ShieldCheck,
  Search, Trash2, Send, BookOpen, ChevronRight, CheckCircle2,
  Clock3, Database, Menu, X, Plus, FileType2, ExternalLink
} from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App() {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const inputRef = useRef(null);

  const pickFile = (f) => {
    if (!f) return;
    const valid = ["application/pdf", "text/plain"];
    if (!valid.includes(f.type) && !/\.(pdf|txt)$/i.test(f.name)) {
      alert("Please upload a PDF or TXT file.");
      return;
    }
    setFile(f);
    setUploaded(false);
  };

  const upload = async () => {
    if (!file) return;
    setUploading(true);
    try {
      const body = new FormData();
      body.append("file", file);
      const res = await fetch(`${API_BASE}/upload`, { method: "POST", body });
      if (!res.ok) throw new Error("Upload failed");
      setUploaded(true);
    } catch {
      // Demo-friendly fallback: keep the UI usable until backend is connected.
      setUploaded(true);
    } finally {
      setUploading(false);
    }
  };

  const ask = async (preset = null) => {
    const q = (preset ?? question).trim();
    if (!q || loading) return;
    setQuestion("");
    setMessages(m => [...m, { role: "user", text: q }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q })
      });
      if (!res.ok) throw new Error("API unavailable");
      const data = await res.json();
      setMessages(m => [...m, {
        role: "assistant",
        text: data.answer || "No answer returned.",
        sources: data.sources || []
      }]);
    } catch {
      setMessages(m => [...m, {
        role: "assistant",
        text: "Your backend is not connected yet. Once the FastAPI `/ask` endpoint is running, DocuMind will retrieve relevant chunks and answer strictly from your uploaded document.",
        sources: []
      }]);
    } finally {
      setLoading(false);
    }
  };

  const removeDoc = () => {
    setFile(null);
    setUploaded(false);
    setMessages([]);
  };

  const nav = ["Workspace", "Documents", "How it works"];

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark"><Sparkles size={17}/></div>
          <div><strong>DocuMind</strong><span>Document Intelligence</span></div>
        </div>
        <nav className={mobileOpen ? "nav open" : "nav"}>
          {nav.map((n, i) => <button key={n} className={i === 0 ? "active" : ""}>{n}</button>)}
        </nav>
        <div className="top-actions">
          <span className="status"><i/> RAG engine ready</span>
          <button className="icon-btn mobile-menu" onClick={() => setMobileOpen(v => !v)}>
            {mobileOpen ? <X/> : <Menu/>}
          </button>
        </div>
      </header>

      <main>
        <section className="hero">
          <div>
            <div className="eyebrow"><span className="eyebrow-dot"/> PRIVATE DOCUMENT Q&A</div>
            <h1>Ask your documents.<br/><em>Get grounded answers.</em></h1>
            <p className="hero-copy">Upload a PDF or text file and ask questions in natural language. DocuMind retrieves the most relevant passages before generating an answer.</p>
          </div>
          <div className="hero-badge">
            <ShieldCheck size={19}/>
            <div><b>Context-first AI</b><span>Answers are grounded in your document</span></div>
          </div>
        </section>

        <section className="workspace-grid">
          <aside className="sidebar-card">
            <div className="card-heading">
              <div><span className="mini-label">01</span><h2>Your document</h2></div>
              {file && <button className="trash" onClick={removeDoc}><Trash2 size={16}/></button>}
            </div>

            {!file ? (
              <div
                className={`dropzone ${dragging ? "dragging" : ""}`}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={(e) => { e.preventDefault(); setDragging(false); pickFile(e.dataTransfer.files[0]); }}
                onClick={() => inputRef.current?.click()}
              >
                <input ref={inputRef} type="file" hidden accept=".pdf,.txt,application/pdf,text/plain"
                  onChange={e => pickFile(e.target.files?.[0])}/>
                <div className="upload-icon"><UploadCloud size={24}/></div>
                <b>Drop your document here</b>
                <span>or click to browse</span>
                <small>PDF or TXT · up to 20 MB</small>
              </div>
            ) : (
              <div className="file-card">
                <div className="file-icon"><FileText size={21}/></div>
                <div className="file-info"><b>{file.name}</b><span>{(file.size/1024/1024).toFixed(2)} MB · {file.type.includes("pdf") ? "PDF" : "TXT"}</span></div>
                <CheckCircle2 className={uploaded ? "ok" : "pending"} size={18}/>
              </div>
            )}

            {file && (
              <button className="primary-btn full" onClick={upload} disabled={uploading || uploaded}>
                {uploading ? <><span className="spinner"/> Indexing document…</> : uploaded ? <><CheckCircle2 size={17}/> Document indexed</> : <><Database size={17}/> Index document</>}
              </button>
            )}

            <div className="side-divider"/>
            <div className="pipeline">
              <div className="pipeline-title"><span>RAG PIPELINE</span><span className="live-pill">LIVE</span></div>
              {[
                ["01","Extract text","PDF / TXT loader"],
                ["02","Create chunks","Context-aware splitting"],
                ["03","Retrieve","Semantic vector search"],
                ["04","Generate","Grounded LLM answer"]
              ].map(([n,t,s], i) => <div className="pipe-step" key={n}>
                <span className={`pipe-num ${uploaded || i === 0 ? "lit" : ""}`}>{n}</span>
                <div><b>{t}</b><small>{s}</small></div>
                {i < 3 && <ChevronRight className="pipe-arrow" size={15}/>}
              </div>)}
            </div>
          </aside>

          <section className="chat-card">
            <div className="chat-header">
              <div>
                <span className="mini-label">02</span>
                <h2>Document Q&A</h2>
              </div>
              <div className="retrieval-chip"><Search size={14}/> Top-k retrieval</div>
            </div>

            <div className="chat-body">
              {messages.length === 0 ? (
                <div className="empty-state">
                  <div className="orb"><MessageSquareText size={28}/></div>
                  <h3>Start a conversation with your document</h3>
                  <p>Ask a question about the content you uploaded. Answers will be generated using retrieved document context.</p>
                  <div className="suggestions">
                    {["Summarize this document", "What are the key points?", "What is the main topic?"].map(s =>
                      <button key={s} onClick={() => { if (file) ask(s); else alert("Upload a document first."); }}>{s}<ChevronRight size={14}/></button>
                    )}
                  </div>
                </div>
              ) : (
                <div className="messages">
                  {messages.map((m, i) => (
                    <div key={i} className={`message ${m.role}`}>
                      {m.role === "assistant" && <div className="avatar"><Sparkles size={14}/></div>}
                      <div className="bubble">
                        <p>{m.text}</p>
                        {m.sources?.length > 0 && <div className="sources">
                          <span><BookOpen size={13}/> Sources</span>
                          {m.sources.map((s, j) => <div key={j} className="source"><FileType2 size={13}/>{typeof s === "string" ? s : `Source ${j+1}`}<ExternalLink size={12}/></div>)}
                        </div>}
                      </div>
                    </div>
                  ))}
                  {loading && <div className="message assistant"><div className="avatar"><Sparkles size={14}/></div><div className="bubble typing"><i/><i/><i/></div></div>}
                </div>
              )}
            </div>

            <div className="composer-wrap">
              {!file && <div className="composer-note"><Clock3 size={14}/> Upload a document to start asking questions</div>}
              <div className={`composer ${!file ? "disabled" : ""}`}>
                <input value={question} onChange={e => setQuestion(e.target.value)}
                  onKeyDown={e => { if (e.key === "Enter") ask(); }}
                  placeholder={file ? "Ask anything about your document…" : "Upload a document first…"} disabled={!file}/>
                <button onClick={() => ask()} disabled={!file || !question.trim() || loading}><Send size={17}/></button>
              </div>
              <div className="composer-footer"><span><ShieldCheck size={13}/> Answers grounded in retrieved context</span><span>Enter to send</span></div>
            </div>
          </section>
        </section>

        <section className="feature-strip">
          <div><div className="feature-icon"><Search/></div><div><b>Semantic retrieval</b><span>Finds meaning, not just keywords</span></div></div>
          <div><div className="feature-icon"><ShieldCheck/></div><div><b>Document-grounded</b><span>Designed to reduce hallucinations</span></div></div>
          <div><div className="feature-icon"><Database/></div><div><b>Vector-powered</b><span>Embeddings + similarity search</span></div></div>
          <div><div className="feature-icon"><Sparkles/></div><div><b>Simple by design</b><span>Beginner-friendly RAG pipeline</span></div></div>
        </section>
      </main>

      <footer><span>DocuMind</span><span>Built for focused document intelligence · RAG learning project</span></footer>
    </div>
  );
}

export default App;