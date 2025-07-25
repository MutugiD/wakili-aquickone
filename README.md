# wakili-aquickone

## Overview
Wakili Quick1 is a modular, agent-based legal automation system designed for Kenyan lawyers. It streamlines legal workflows such as research, evidence review, document drafting, and multi-turn chat-based case management. The system is built with a FastAPI backend and a Next.js + Tailwind CSS frontend.

## Features
- **Intent-based Orchestrator:** Routes lawyer requests to the correct agent (research, drafting, evidence, etc.) using LLM-powered intent detection.
- **Multi-Agent System:** Includes ResearchAgent, DraftingAgent, EvidenceAgent, and more, each handling specialized legal tasks.
- **Document Management:** Upload, extract, draft, and manage legal documents (PDF, DOCX, etc.).
- **Memory & Context:** Tracks multi-turn conversations, corrections, and workflow state for adaptive recommendations.
- **Human-in-the-Loop:** Allows lawyers to intervene, correct, and refine agent suggestions.
- **Frontend:** Modern React/Next.js UI for chat, document upload, extraction, and drafting.

## Architecture
- **Backend:** FastAPI app with modular endpoints for agents, documents, and research. Agents use LangChain, Tavily, and OpenAI for LLM and search capabilities.
- **Frontend:** Next.js app in `frontend/` with pages for chat, document upload, extraction, and drafting. Uses Tailwind CSS for styling.
- **Agents:**
  - `ResearchAgent`: Legal research, case law, statutes, citations.
  - `DraftingAgent`: Generates demand letters, plaints, briefs, affidavits.
  - `EvidenceAgent`: (Planned) Evidence review and extraction.
  - `Orchestrator`: Intent detection and routing.
- **Document Extraction:** Extracts structured data from legal documents using LLMs and custom prompts.
- **Memory:** ConversationBufferMemory tracks chat history and workflow state.

## Installation
1. **Clone the repo:**
   ```bash
   git clone https://github.com/MutugiD/wakili-aquickone.git
   cd wakili-aquickone
   ```
2. **Backend setup:**
   - Python 3.8+
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Add `.env` file with required API keys (e.g., OpenAI, Tavily).
   - Run the backend:
     ```bash
     python backend/main.py
     # or
     uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
     ```
3. **Frontend setup:**
   - Go to `frontend/`:
     ```bash
     cd frontend
     npm install
     npm run dev
     ```
   - Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage
- **Chat-based workflow:** Submit legal queries, correct agent suggestions, and upload documents via the chat UI.
- **Document drafting:** Generate demand letters, plaints, briefs, and affidavits. Drafts are saved in `docs/outputs/` and logged in `draft_events_log.csv`.
- **Document extraction:** Upload and extract structured data from legal documents.
- **API Endpoints:**
  - `/health`: Health check
  - `/documents/upload`: Upload documents
  - `/documents/draft`: Draft legal documents
  - `/documents/outputs`: List drafted documents
  - `/research/query`: Legal research
  - `/agent/chat`: Multi-turn chat with memory and context

## Project Structure
```
wakili-quick1/
  backend/
    main.py
    agent/
      intent_orchestrator.py
      legal_tools.py
      memory.py
      orchestrator.py
      drafting_agent/
      research_agent/
    api/
      endpoints/
      models/
      services/
    document_extraction/
    prompts/
    utils/
  frontend/
    src/
    public/
    ...
  docs/
    outputs/
    samples/
    ...
  test_orchestrator.py
  .env (ignored)
  venv/ (ignored)
  scripts/ (ignored)
```

## Local Testing
- Run `python test_orchestrator.py` for backend agent tests.
- All outputs are saved in `docs/outputs/`.
- See `docs/local_testing.md` for more details.

## Contributing
Pull requests and issues are welcome! See the architecture and planner docs in `docs/` for guidance on extending agents, workflows, or UI features.

## License
MIT
