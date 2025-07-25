# Planner: Modular Lawyer-Facing Legal Automation System

## Overview

This planner outlines a modular, decoupled architecture for Kenyan legal workflows, designed for a lawyer endpoint. The system is extensible, with each agent/module in its own folder under `src/agent/`, services in `src/services/`, utilities in `src/utils/`, and API endpoints in `src/api/`. The orchestrator uses a Task Interpreter for intent detection and dynamic routing.

---

## High-Level Task Flow

1. **Client Request**: Lawyer submits a request via API/UI.
2. **API Layer**: Receives the request and passes it to the orchestrator.
3. **Orchestrator (Task Interpreter)**: Classifies intent (e.g., research, draft, review) and selects the agent pipeline.
4. **Agent Pipeline**: Orchestrator routes to the appropriate agent(s):
   - Research Agent (for legal research)
   - Evidence Agent (for evidence review)
   - Drafting Agent (for document generation)
   - Validation Agent (for compliance checks, optional)
5. **Output**: Results are returned to the lawyer for review or delivery to the client.

---

## Agent/Module Responsibilities

### 1. API Layer (`src/api/`)

- Exposes endpoints for each agent and workflow.
- Receives requests from lawyer-facing UI or integrations.

### 2. Orchestrator & Task Interpreter (`src/agent/orchestrator.py`)

- Receives all requests from API.
- Uses Task Interpreter (LLM prompt/classifier) to detect intent.
- Routes request to the appropriate agent pipeline.
- Manages state, context, and agent chaining.

### 3. Research Agent (`src/agent/research_agent/`)

- Handles legal research queries (case law, statutes, etc.).
- Returns citations and summaries for use in evidence or drafting.

### 4. Evidence Agent (`src/agent/evidence_agent/`)

- Extracts structured facts, parties, dates, and key details from client input or uploaded documents.
- Flags missing evidence and provides legal rationale.

### 5. Drafting Agent (`src/agent/drafting_agent/`)

- Generates legal documents using templates and context (facts, extracted data, case law if provided).
- Supports multiple document types (demand letter, plaint, brief, etc.).

### 6. Validation Agent (`src/agent/validation_agent/`, optional)

- Reviews generated documents for compliance with Kenyan legal SOP, formatting, and citation standards.
- Can be added or removed from the workflow as needed.

### 7. Services (`src/services/`)

- DocLing backend for document ingestion and OCR.
- Vector store and metadata services for retrieval.

### 8. Utilities (`src/utils/`)

- Schema, text, and helper utilities for all agents.

---

## Extensibility Notes

- Add new agents by creating a new folder/module in `src/agent/` and registering with the orchestrator and API.
- Add new services or utilities in `src/services/` or `src/utils/`.
- Add new endpoints in `src/api/endpoints/`.
- Update the orchestrator to support new intent types and agent pipelines.

---

## Example: Lawyer Workflow

- Lawyer: “I want to see recent Kenyan cases on deposit refunds.”
  - Intent Interpreter: “legal research”
  - Research Agent: returns case law
- Lawyer: “Draft a plaint for my client based on these facts.”
  - Intent Interpreter: “draft plaint”
  - Drafting Agent: uses facts, research, templates to generate draft
- Lawyer: “Review this lease and flag missing evidence.”
  - Intent Interpreter: “evidence review”
  - Evidence Agent: analyzes document, flags gaps

---

## Summary

This planner provides a flexible, extensible, and lawyer-centric foundation for Kenyan legal automation, supporting easy integration of new agent modules and document types while minimizing unnecessary steps.
