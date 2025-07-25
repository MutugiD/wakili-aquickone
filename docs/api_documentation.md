# API Documentation

This document describes all available API endpoints for the Wakili Quick1 backend, including request/response formats and example usage for testing.

---

## 1. Health Check

**GET /health**

- **Description:** Returns API health status.
- **Response:** `{ "status": "ok" }`
- **Example:**
  ```bash
  curl http://localhost:8000/health
  ```

---

## 2. Document Endpoints

### a. Upload Document

**POST /documents/upload**

- **Description:** Upload a document (PDF, DOCX, etc.) for extraction or drafting.
- **Request:**
  - `file`: File (multipart/form-data)
  - `description`: (optional) String
- **Response:** `{ "filename": "...", "path": "..." }`
- **Example:**
  ```bash
  curl -F "file=@/path/to/file.pdf" -F "description=Sample doc" http://localhost:8000/documents/upload
  ```

### b. List Documents

**GET /documents/list**

- **Description:** List all uploaded documents.
- **Response:** `[ "filename1.pdf", "filename2.docx", ... ]`
- **Example:**
  ```bash
  curl http://localhost:8000/documents/list
  ```

### c. Get Document

**GET /documents/{filename}**

- **Description:** Download a specific document by filename.
- **Response:** File download
- **Example:**
  ```bash
  curl -O http://localhost:8000/documents/sample.pdf
  ```

### d. Event Log

**GET /documents/event-log**

- **Description:** Get the document event log (uploads, drafts, etc.)
- **Response:** `{ "events": [ ... ] }`
- **Example:**
  ```bash
  curl http://localhost:8000/documents/event-log
  ```

---

## 3. Extraction Endpoint

**POST /documents/extract**

- **Description:** Extract structured data from an uploaded document.
- **Request:**
  - `filename`: String (name of uploaded file)
- **Response:**
  ```json
  {
    "parties": ["Party 1", "Party 2"],
    "effective_date": "...",
    "termination_date": "...",
    "clauses": ["Clause 1", "Clause 2", ...]
  }
  ```
- **Example:**
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"filename": "sample.pdf"}' http://localhost:8000/documents/extract
  ```

---

## 4. Drafting Endpoints

**POST /documents/draft**

- **Description:** Draft a legal document (demand letter, plaint, brief, affidavit) using a template and context.
- **Request:**
  - `doc_type`: String ("demand_letter", "plaint", "brief", "affidavit")
  - `context`: Object (fields depend on doc_type)
- **Response:** `{ "draft": "...document text...", "file_path": "..." }`
- **Example:**
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"doc_type": "demand_letter", "context": {"client": "Jane Doe", "recipient": "John Landlord", "facts": "Deposit refund dispute"}}' http://localhost:8000/documents/draft
  ```

---

## 5. Research Endpoints

### a. Research Query

**POST /research/query**

- **Description:** Submit a legal research question.
- **Request:** `{ "question": "What is the law on ...?" }`
- **Response:** `{ "answer": "...", "sources": [ ... ] }`
- **Example:**
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"question": "What is the law on tenant deposit refunds in Kenya?"}' http://localhost:8000/research/query
  ```

### b. Research History

**GET /research/history**

- **Description:** Get previous research queries and answers.
- **Response:** `[ { "question": "...", "answer": "...", "sources": [ ... ] }, ... ]`
- **Example:**
  ```bash
  curl http://localhost:8000/research/history
  ```

---

## 6. Agent Endpoints

### a. Ask Agent

**POST /agent/ask**

- **Description:** Ask the orchestrator agent any legal question or workflow request.
- **Request:** `{ "question": "Draft a demand letter for ..." }`
- **Response:** `{ "response": "...", "memory": { ... } }`
- **Example:**
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"question": "Draft a demand letter for deposit refund"}' http://localhost:8000/agent/ask
  ```

### b. Agent Workflow

**POST /agent/workflow**

- **Description:** Submit a multi-step workflow or scenario for the agent to process.
- **Request:** `{ "scenario": "Client uploads a contract, requests extraction, then asks for a draft demand letter." }`
- **Response:** `{ "steps": [ ... ], "final_output": "..." }`
- **Example:**
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"scenario": "Extract all parties from contract.pdf and draft a demand letter."}' http://localhost:8000/agent/workflow
  ```

---

## Notes

- All endpoints are unauthenticated by default. Add authentication headers if/when required.
- All responses are JSON unless a file download is requested.
- For file uploads, use multipart/form-data.
- For document extraction, upload the file first, then call the extract endpoint with the filename.
- For drafting, provide as much context as possible for best results.

---

## Testing

- Use the provided curl examples or Postman to test each endpoint.
- For integration with the frontend, see the Next.js API integration plan.
