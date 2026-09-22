import React from "react";
import { Trash2, Database, CheckCircle2, Sparkles } from "lucide-react";
import UploadZone from "./UploadZone";
import FileCard from "./FileCard";
import RagPipeline from "./RagPipeline";

export default function DocumentPanel({
  file,
  dragging,
  setDragging,
  pickFile,
  upload,
  uploading,
  uploaded,
  removeDoc,
  inputRef,
  isQuerying
}) {
  return (
    <aside className="panel-card sidebar-panel">
      <div className="panel-header">
        <div className="panel-title-wrap">
          <span className="step-chip">01</span>
          <h2>Your document</h2>
        </div>

        {file && (
          <button
            className="icon-action-btn"
            onClick={removeDoc}
            title="Remove document and reset chat"
            aria-label="Remove document"
          >
            <Trash2 size={16} />
          </button>
        )}
      </div>

      <div className="doc-panel-body">
        {!file ? (
          <UploadZone
            dragging={dragging}
            setDragging={setDragging}
            pickFile={pickFile}
            inputRef={inputRef}
          />
        ) : (
          <>
            <FileCard file={file} uploaded={uploaded} />

            <button
              className={`primary-btn ${uploaded ? "indexed" : ""}`}
              onClick={upload}
              disabled={uploading || uploaded}
            >
              {uploading ? (
                <>
                  <span className="spinner" />
                  <span>Indexing document…</span>
                </>
              ) : uploaded ? (
                <>
                  <CheckCircle2 size={18} strokeWidth={2.2} />
                  <span>Document indexed</span>
                </>
              ) : (
                <>
                  <Database size={18} />
                  <span>Index document</span>
                </>
              )}
            </button>
          </>
        )}

        <div className="pipeline-divider" />

        <RagPipeline uploaded={uploaded} isQuerying={isQuerying} />
      </div>
    </aside>
  );
}
