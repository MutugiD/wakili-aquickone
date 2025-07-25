# Architecture: Modular Lawyer-Facing Legal Automation System

## Project Structure

```
wakili-quick1/
  src/
    agent/
      research_agent/
      evidence_agent/
      drafting_agent/
      # ...more agents
    services/
      docling_service.py
      vector_store_service.py
      # ...more services
    utils/
      schema_utils.py
      text_utils.py
      # ...more utils
    api/
      main.py
      endpoints/
        research.py
        evidence.py
        drafting.py
        # ...more endpoints
  docs/
    architecture.md
    planner.md
    tasks-tracker.md
  requirements.txt
  ...
```

---

## System Overview
This architecture describes a modular, agent-based system for automating Kenyan legal workflows for lawyers. The system is designed for a lawyer endpoint: the lawyer receives a client request, the orchestrator uses intent detection to route the request to the appropriate agent(s) (research, evidence, drafting, etc.), and all modules are decoupled for easy extension or minimization of steps.

---

## System Diagram

```mermaid
graph TD
    A[Client Request] --> B[API Layer]
    B --> C[Orchestrator (Task Interpreter)]
    C -->|Intent: Research| D[Research Agent]
    C -->|Intent: Evidence Review| E[Evidence Agent]
    C -->|Intent: Drafting| F[Drafting Agent]
    D --> G[Output to Lawyer]
    E --> G
    F --> G
    F --> H[Validation Agent]
    H --> G
```

---

## Key Components

### 1. API Layer (src/api/)
- FastAPI backend exposes endpoints for each agent and workflow.
- Receives requests from lawyer-facing UI or integrations.

### 2. Orchestrator & Task Interpreter (src/agent/orchestrator.py)
- Receives all requests from API.
- Uses Task Interpreter (LLM prompt/classifier) to detect intent (e.g., research, draft, review).
- Routes request to the appropriate agent pipeline.
- Manages state, context, and agent chaining.

### 3. Research Agent (src/agent/research_agent/)
- Handles legal research queries (case law, statutes, etc.).
- Returns citations and summaries for use in evidence or drafting.

### 4. Evidence Agent (src/agent/evidence_agent/)
- Extracts structured facts, parties, dates, and key details from client input or uploaded documents.
- Flags missing evidence and provides legal rationale.

### 5. Drafting Agent (src/agent/drafting_agent/)
- Generates legal documents using templates and context (facts, extracted data, case law if provided).
- Supports multiple document types (demand letter, plaint, brief, etc.).

### 6. Validation Agent (src/agent/validation_agent/, optional)
- Reviews generated documents for compliance with Kenyan legal SOP, formatting, and citation standards.
- Can be added or removed from the workflow as needed.

### 7. Services (src/services/)
- DocLing backend for document ingestion and OCR.
- Vector store and metadata services for retrieval.

### 8. Utilities (src/utils/)
- Schema, text, and helper utilities for all agents.

---

## Example Agent Pipelines

### A. Research Flow
1. Lawyer submits research query via API.
2. Orchestrator detects "research" intent.
3. Research Agent is invoked, returns case law and summaries.
4. Output is returned to the lawyer.

### B. Drafting Flow
1. Lawyer requests document drafting (e.g., "draft plaint").
2. Orchestrator detects "drafting" intent.
3. Drafting Agent is invoked, optionally calls Evidence Agent and/or Research Agent for context.
4. Draft is generated and optionally validated.
5. Output is returned to the lawyer.

### C. Document Review Flow
1. Lawyer uploads a document for review.
2. Orchestrator detects "evidence review" intent.
3. Evidence Agent is invoked to analyze and flag missing or non-compliant evidence.
4. Output is returned to the lawyer.

---

## Extensibility Points
- Add new agents by creating a new folder/module in `src/agent/` and registering with the orchestrator and API.
- Add new services or utilities in `src/services/` or `src/utils/`.
- Add new endpoints in `src/api/endpoints/`.
- Update the orchestrator to support new intent types and agent pipelines.

---

## Summary

This architecture is lawyer-centric, modular, and extensible. The orchestrator and intent detection enable dynamic, context-aware routing to the right agent pipeline, supporting rapid addition of new workflows and agent modules as legal practice evolves.
