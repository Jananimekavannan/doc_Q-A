import React from "react";
import { UploadCloud, FileUp } from "lucide-react";

export default function UploadZone({ dragging, setDragging, pickFile, inputRef }) {
  return (
    <div
      className={`dropzone ${dragging ? "dragging" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
          pickFile(e.dataTransfer.files[0]);
        }
      }}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        hidden
        accept=".pdf,.txt,application/pdf,text/plain"
        onChange={(e) => {
          if (e.target.files && e.target.files[0]) {
            pickFile(e.target.files[0]);
          }
        }}
      />
      
      <div className="upload-icon-container">
        <UploadCloud size={28} strokeWidth={2} />
      </div>

      <b className="dropzone-title">Drop your document here</b>
      <span className="dropzone-sub">or click to browse your files</span>

      <span className="browse-btn">
        <FileUp size={14} />
        Choose Document
      </span>

      <span className="dropzone-format">PDF or TXT · up to 20 MB</span>
    </div>
  );
}
