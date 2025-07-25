# Frontend Testing Guide: Document Upload & Extraction

This guide explains how to test the document upload and extraction features in the Wakili Quick1 frontend (Next.js + Tailwind CSS).

---

## Prerequisites
- Backend API must be running and accessible at `http://localhost:8000` or `http://127.0.0.1:8000`.
- Frontend dev server must be running (`npm run dev` in the `frontend/` folder).
- Sample documents (PDF/DOCX) are available in `docs/samples/`.

---

## 1. Start the Backend API

Open a terminal in the project root and run:
```bash
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```
Or, if using Python module:
```bash
python -m backend.api.main
```

---

## 2. Start the Frontend Dev Server

Open a new terminal and run:
```bash
cd frontend
npm install  # if not already done
npm run dev
```

Visit [http://localhost:3000/upload](http://localhost:3000/upload) in your browser.

---

## 3. Test Document Upload

1. **Open the Upload Page:**
   - Go to `/upload` in your browser.

2. **Add Files:**
   - Drag and drop PDF/DOCX files into the drop area, or click "browse" to select files.
   - Each file appears in the list with its name, size, and status (`pending`).

3. **Accept/Deny/Remove:**
   - Click **Accept** to mark a file for upload.
   - Click **Deny** to mark a file as denied (won't be uploaded).
   - Click **Remove** to delete a file from the list.

4. **Upload Files:**
   - Click **Upload Accepted Files**.
   - Accepted files are uploaded to the backend. Status changes to `uploading`, then `uploaded` on success, or `error` on failure.
   - Errors are shown inline (e.g., if the backend is down).

5. **Add More Files:**
   - Click **Add More Files** to select and add more documents at any time.

---

## 4. Test Extraction Flow

1. **After Upload:**
   - For each file with status `uploaded`, an **Extract Document** button appears.

2. **Trigger Extraction:**
   - Click **Extract Document** to call the backend extraction API for that file.
   - Status changes to `extracting`, then `extracted` on success, or `error` on failure.
   - Extraction results are shown inline as formatted JSON.

3. **Accept/Deny Extraction:**
   - After extraction, click **Accept Extraction** to mark the result as accepted, or **Deny Extraction** to reject it.
   - You can preview the extraction result before accepting/denying.

---

## 5. UI/UX Checks

- **File Previews:**
  - Images show a thumbnail preview.
  - PDFs/DOCX show an icon and filename (no in-browser preview yet).
- **Status Badges:**
  - Each file shows its current status (pending, accepted, denied, uploading, uploaded, extracting, extracted, error).
- **Error Handling:**
  - Upload or extraction errors are shown inline in red.
  - If the backend is down, uploading will fail with an error.
- **Responsiveness:**
  - The UI is responsive and works on desktop and mobile.

---

## 6. Troubleshooting

- **Upload Fails:**
  - Ensure the backend is running and accessible at the correct port.
  - Check the browser console and network tab for error details.
- **Extraction Fails:**
  - Ensure the backend `/documents/extract` endpoint is implemented and working.
  - Check backend logs for errors (e.g., missing dependencies, file not found).
- **UI Not Updating:**
  - Refresh the page and retry.
  - Check for errors in the browser console.

---

## 7. Extending the Flow

- After extraction is accepted, the UI can be extended to:
  - Trigger drafting, agent chat, or other downstream actions.
  - Allow users to preview, accept, or deny each step as the agent proceeds.

---

## 8. Example Test Cases

- Upload a valid PDF and DOCX, accept and upload, extract, and accept extraction.
- Upload a file, deny it, and verify it is not uploaded.
- Upload multiple files, remove one before upload, and verify only the others are processed.
- Simulate backend down and verify error handling.

---

**For any issues, check backend logs, browser console, and network tab for details.**