import React from "react";
import { FileText, CheckCircle2, Clock, FileType } from "lucide-react";

export default function FileCard({ file, uploaded }) {
  const isPdf = file.type.includes("pdf") || file.name.toLowerCase().endsWith(".pdf");
  const fileSizeMb = (file.size / (1024 * 1024)).toFixed(2);
  const fileSizeKb = (file.size / 1024).toFixed(1);
  const formattedSize = file.size > 1024 * 1024 ? `${fileSizeMb} MB` : `${fileSizeKb} KB`;

  return (
    <div className="file-card">
      <div className={`file-type-icon ${isPdf ? "pdf" : "txt"}`}>
        {isPdf ? <FileText size={22} strokeWidth={2.2} /> : <FileType size={22} strokeWidth={2.2} />}
      </div>

      <div className="file-meta">
        <strong className="file-name" title={file.name}>
          {file.name}
        </strong>
        <div className="file-details">
          <span>{formattedSize}</span>
          <span>•</span>
          <span>{isPdf ? "PDF Document" : "Plain Text"}</span>
          <span>•</span>
          <span style={{ color: uploaded ? "var(--emerald-accent)" : "var(--amber-accent)", fontWeight: 600 }}>
            {uploaded ? "Indexed" : "Ready to index"}
          </span>
        </div>
      </div>

      <div className="file-status-indicator">
        {uploaded ? (
          <CheckCircle2 className="status-icon indexed" size={20} />
        ) : (
          <Clock className="status-icon pending" size={20} />
        )}
      </div>
    </div>
  );
}
