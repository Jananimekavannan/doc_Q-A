# DocuMind Frontend

A polished React/Vite frontend for a beginner-friendly document Q&A (RAG) project.

## Run

```bash
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

## Backend contract

Set `VITE_API_BASE_URL` if your FastAPI backend is not on `http://localhost:8000`.

Expected endpoints:

### POST `/upload`
Multipart form-data:
- `file`: PDF or TXT

### POST `/ask`
JSON:
```json
{ "question": "What is this document about?" }
```

Expected response:
```json
{
  "answer": "....",
  "sources": ["Page 2", "Page 4"]
}
```

### Notes
The UI remains usable before the backend is connected, so your team can build and review the frontend independently. The fallback message is only for local UI development; connect the FastAPI endpoints for the real RAG behavior.
