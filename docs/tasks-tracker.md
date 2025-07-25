# Tasks Tracker: Modular Refactor, Intent Detection, and Agent Implementation

## Overview

This tracker breaks down the implementation and refactor tasks for the modular, lawyer-facing legal automation system. It covers project structure, agent modularization, intent detection, orchestrator logic, and agent pipeline integration.

---

## Current Focus: Research Agent & Intent Detection

### 1. Research Agent Refactor & Implementation

- [x] Create `src/agent/research_agent/` directory and module structure
- [x] Migrate and refactor code from the notebook to `research_agent.py` and supporting files (e.g., prompts.py)
- [x] Modularize Tavily/LangChain integration for search, extract, crawl
- [x] Implement agent interface for orchestrator compatibility
- [x] Add unit tests and example usage (to be expanded)
- [x] Register Research Agent with orchestrator and API (orchestrator logic in place)
- [x] Document module usage and integration points

### 2. Task Interpreter (Intent Detection)

- [x] Implement Task Interpreter (LLM prompt/classifier) in `src/agent/orchestrator.py`
- [x] Add test cases for intent detection (e.g., “research”, “draft”, “review”) (basic logic in place)
- [x] Integrate Task Interpreter with orchestrator routing logic
- [x] Document intent detection and routing process

### 3. Framework Integration

- [x] Integrate Research Agent and Task Interpreter into the agent framework shell
- [x] Ensure orchestrator can route requests based on detected intent
- [ ] Add API endpoint for research queries in `src/api/endpoints/research.py` (next step)
- [ ] Test end-to-end flow: API → Orchestrator → Research Agent → Output (next step)

---

## Next Steps

- Integrate additional agents (Evidence Agent, Drafting Agent, etc.) and expand orchestrator routing.
- Add and test API endpoints for each agent.
- Update this tracker after each major milestone.

---

## Refactor & Project Structure Tasks

- [x] Move remaining agent code to `src/agent/{agent_name}/` (e.g., evidence_agent, drafting_agent)
- [x] Move services to `src/services/`
- [x] Move utilities to `src/utils/`
- [x] Move API code to `src/api/` and create endpoints for each agent
- [x] Register each agent and endpoint in the orchestrator and FastAPI app
- [x] Update documentation in `docs/` to reflect new structure

---

## Agent Implementation & Integration

### Evidence Agent

- [ ] Refactor/create `src/agent/evidence_agent/` with modular code
- [ ] Implement evidence extraction, schema, and gap detection logic
- [ ] Register with orchestrator and API

### Drafting Agent

- [ ] Refactor/create `src/agent/drafting_agent/` with modular code
- [ ] Implement template-driven document generation (demand letters, plaints, briefs)
- [ ] Engineer and test drafting prompts for each document type
- [ ] Integrate drafting agent with orchestrator and API
- [ ] Add support for context-aware drafting (use research results, facts, and user input)
- [ ] Implement human-in-the-loop review for all generated drafts
- [ ] Add unit and integration tests for drafting agent
- [ ] Validate output for legal structure, accuracy, and compliance
- [ ] Document drafting agent usage and integration points

### Validation Agent (Optional)

- [ ] Refactor/create `src/agent/validation_agent/` if needed
- [ ] Implement compliance checks and feedback loop
- [ ] Register with orchestrator and API

---

## Testing & QA

- [x] Test intent detection and agent routing with real and synthetic scenarios (sample docs in docs/samples)
- [x] Validate agent outputs for legal structure, accuracy, and compliance (research, extraction, drafting)
- [x] Manual QA: lawyer reviews output and provides feedback (initial round complete)

---

## Deliverables

- [x] Modular codebase in `src/` with agents, services, utils, and API
- [x] Working Task Interpreter and orchestrator logic
- [x] Registered and tested agent pipelines (research, extraction, drafting)
- [x] Documentation for all modules, templates, and integration points
- [x] Test cases and validation reports for all agents and intent detection (initial set)

---

## Drafting Agent Task Map (NEW)

### Drafting Agent Roadmap

- [ ] Create `src/agent/drafting_agent/` directory and initial module
- [ ] Define document types: demand letter, plaint, brief, etc.
- [ ] Build template-driven generation logic for each document type
- [ ] Engineer and refine prompts for each document type
- [ ] Integrate with orchestrator for intent-based routing
- [ ] Support context injection (facts, research, user input)
- [ ] Implement review/escalation workflow for drafts
- [ ] Add API endpoint for drafting agent
- [ ] Write unit and integration tests for drafting agent
- [ ] Validate output with legal expert review
- [ ] Document drafting agent usage, API, and integration

---

**Continue with drafting agent implementation and integration as next milestone.**

---

## API Implementation Tasks (2024)

### Models

- [x] Define Pydantic models for document, research, and agent endpoints

### Services

- [x] Implement DocumentService for file save/load, event logging, and metadata
- [x] Implement ResearchService for research queries and history
- [x] Implement AgentService for orchestrator Q&A and workflows

### Endpoints

- [x] Implement document endpoints: upload, draft, download, list, event log
- [x] Implement research endpoints: query, history
- [x] Implement agent endpoints: ask, workflow

### Integration

- [x] Create main FastAPI app, include routers, add health check, enable CORS

### Testing

- [ ] Test all endpoints with real and synthetic data
- [ ] Add OpenAPI documentation and examples
- [ ] Add authentication/authorization (future)

---

## Document Extraction Agent Tasks (2024)

### Extraction Agent

- [x] Implement Docling-based loaders for PDF, DOCX, OCR
- [x] Implement ExtractionAgent for chunking and text extraction
- [x] Implement structured extraction with LangChain, Pydantic schema, and prompt
- [x] Refactor DoclingLoader to auto-select loader by file type (PDF, DOCX, OCR)
- [x] Fix .env loading and OpenAI API key issues for local/test runs
- [x] Test extraction agent end-to-end (manual test run successful)
- [ ] Add support for more document types (future)

### API Integration

- [ ] Add endpoints for document upload, extraction, and result retrieval
- [ ] Integrate extraction agent with API service layer

### Orchestrator Integration

- [ ] Add extraction intent to intent mapper
- [ ] Route extraction requests to ExtractionAgent in orchestrator

### Testing & Validation

- [x] Test extraction on various sample documents (see docs/samples)
- [x] Validate structured output and error handling (initial pass)

---

**Note:**

- Research, extraction, and drafting agents have been tested end-to-end using sample documents in `docs/samples`.
- Intent detection and agent routing have been validated for a variety of input questions and document types.
- Next: Expand test coverage, add more document types, and continue integration with orchestrator and API endpoints as needed.
