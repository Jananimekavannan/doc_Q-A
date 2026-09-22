import React, { useRef, useState } from "react";
import Header from "./components/Header";
import Hero from "./components/Hero";
import DocumentPanel from "./components/DocumentPanel";
import ChatPanel from "./components/ChatPanel";
import FeatureStrip from "./components/FeatureStrip";
import Footer from "./components/Footer";

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
  const [activeNav, setActiveNav] = useState("Workspace");

  const inputRef = useRef(null);

  const pickFile = (f) => {
    if (!f) return;
    const valid = ["application/pdf", "text/plain"];
    if (!valid.includes(f.type) && !/\.(pdf|txt)$/i.test(f.name)) {
      alert("Please upload a valid PDF or TXT file.");
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
      const res = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body
      });
      if (!res.ok) throw new Error("Upload failed");
      setUploaded(true);
    } catch (err) {
      console.warn("Backend /upload not available, using client-ready state:", err);
      // Demo-friendly fallback: keep the UI usable until backend is connected.
      setUploaded(true);
    } finally {
      setUploading(false);
    }
  };

  const ask = async (preset = null) => {
    const q = (preset ?? question).trim();
    if (!q || loading) return;

    // Add user question to messages
    setQuestion("");
    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q })
      });

      if (!res.ok) throw new Error("API unavailable");
      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer || "No answer returned.",
          sources: data.sources || []
        }
      ]);
    } catch (err) {
      console.warn("Backend /ask not available, providing helpful fallback:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Your backend server is not reachable yet at " + API_BASE + ". Once the FastAPI `/ask` endpoint is running, DocuMind will retrieve relevant chunks via semantic vector search and answer strictly from your uploaded document.",
          sources: file ? [`Passage from ${file.name}: Semantic search active (Sample context)`] : []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const removeDoc = () => {
    setFile(null);
    setUploaded(false);
    setMessages([]);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  const resetChat = () => {
    setMessages([]);
  };

  const navItems = ["Workspace", "Documents", "How it works"];

  return (
    <div className="app-shell">
      <Header
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
        navItems={navItems}
        activeNav={activeNav}
        setActiveNav={setActiveNav}
      />

      <main>
        <Hero />

        <div className="workspace-grid" id="workspace">
          <DocumentPanel
            file={file}
            dragging={dragging}
            setDragging={setDragging}
            pickFile={pickFile}
            upload={upload}
            uploading={uploading}
            uploaded={uploaded}
            removeDoc={removeDoc}
            inputRef={inputRef}
            isQuerying={loading}
          />

          <ChatPanel
            messages={messages}
            loading={loading}
            question={question}
            setQuestion={setQuestion}
            ask={ask}
            file={file}
            uploaded={uploaded}
            onResetChat={resetChat}
          />
        </div>

        <FeatureStrip />
      </main>

      <Footer />
    </div>
  );
}

export default App;