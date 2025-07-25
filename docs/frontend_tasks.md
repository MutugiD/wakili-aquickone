# Frontend Task Tracker: Next.js + Tailwind CSS

## Overview

This tracker outlines all planned and in-progress tasks for the Wakili Quick1 frontend, built with Next.js, Tailwind CSS, and React. All code is tracked in the `frontend/` folder.

---

## Project Setup

- [ ] Scaffold Next.js project in `frontend/`
- [ ] Install and configure Tailwind CSS
- [ ] Set up Prettier, ESLint, and basic code quality tools
- [ ] Add global styles and Tailwind config

---

## Core Features & Pages

### 1. Document Upload & Management

- [ ] Create `/upload` page for document upload
- [ ] Implement `DocumentUploader` component (drag-and-drop, file picker)
- [ ] Show upload status, errors, and uploaded file list
- [ ] Integrate with `/documents/upload` and `/documents/list` API endpoints
- [ ] Link to extraction and drafting flows from uploaded files

### 2. Document Extraction

- [ ] Create `/extract` page to select and extract uploaded documents
- [ ] Implement `ExtractionResults` component to display structured extraction output
- [ ] Integrate with `/documents/extract` API endpoint
- [ ] Add download/copy functionality for extraction results

### 3. Drafting

- [ ] Create `/draft` page for document drafting
- [ ] Implement form to select document type and enter context
- [ ] Integrate with `/documents/draft` API endpoint
- [ ] Display and allow download/copy of generated drafts

### 4. Research

- [ ] Create `/research` page for legal research queries
- [ ] Implement search bar and results list
- [ ] Integrate with `/research/query` and `/research/history` endpoints

### 5. Agent Chat & Orchestration

- [ ] Create `/agent` page for agentic Q&A and workflows
- [ ] Implement chat UI with message history and memory display
- [ ] Integrate with `/agent/ask` and `/agent/workflow` endpoints

### 6. Event Log

- [ ] Create `/events` or `/log` page to display document and agent event log
- [ ] Integrate with `/documents/event-log` endpoint

---

## UI/UX & Styling

- [ ] Set up responsive layout and navigation (header/sidebar)
- [ ] Add loading, error, and success feedback for all API calls
- [ ] Polish with Tailwind utility classes and custom CSS as needed

---

## API Integration

- [ ] Create `/lib/api.ts` or similar for API client utilities
- [ ] Add error handling and type safety for all API calls
- [ ] Write example API tests (Jest or similar)

---

## Testing & QA

- [ ] Manual testing of all flows using backend API
- [ ] Add E2E tests (Cypress/Playwright) for critical flows
- [ ] Accessibility and mobile responsiveness checks

---

## Deliverables

- [ ] All code in `frontend/` folder
- [ ] README with setup and usage instructions
- [ ] Deployed demo or local test instructions

---

**Update this tracker as tasks are started, in progress, or completed.**
