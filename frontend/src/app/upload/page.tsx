import DocumentUploader from '../../components/DocumentUploader';

export default function UploadPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-6">Upload Documents</h1>
      <p className="mb-4 text-gray-600">Upload your legal documents (PDF, DOCX, etc.) for extraction, drafting, or review. You can add more files as the agent proceeds with the work.</p>
      <DocumentUploader />
    </main>
  );
}