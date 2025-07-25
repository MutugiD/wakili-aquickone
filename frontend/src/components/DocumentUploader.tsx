'use client';
import React, { useRef, useState } from 'react';

interface UploadedFile {
  file: File;
  previewUrl: string;
  status: 'pending' | 'accepted' | 'denied' | 'uploading' | 'uploaded' | 'error' | 'extracting' | 'extracted';
  serverPath?: string;
  error?: string;
  extractionResult?: unknown;
  extractionStatus?: 'idle' | 'extracting' | 'extracted' | 'error';
  extractionError?: string;
  extractionAccepted?: boolean;
}

function getFileTypeIcon(file: File) {
  if (file.type === 'application/pdf') return '📄';
  if (file.name.endsWith('.doc') || file.name.endsWith('.docx')) return '📝';
  if (file.type.startsWith('image/')) return null;
  return '📁';
}

export default function DocumentUploader() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList) return;
    const newFiles: UploadedFile[] = Array.from(fileList).map((file) => ({
      file,
      previewUrl: file.type.startsWith('image/') ? URL.createObjectURL(file) : '',
      status: 'pending',
      extractionStatus: 'idle',
      extractionAccepted: false,
    }));
    setFiles((prev) => [...prev, ...newFiles]);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    handleFiles(e.dataTransfer.files);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  };

  const handleAccept = (idx: number) => {
    setFiles((prev) => prev.map((f, i) => (i === idx ? { ...f, status: 'accepted' } : f)));
  };

  const handleDeny = (idx: number) => {
    setFiles((prev) => prev.map((f, i) => (i === idx ? { ...f, status: 'denied' } : f)));
  };

  const handleRemove = (idx: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  const uploadFiles = async () => {
    setUploading(true);
    const updatedFiles = await Promise.all(
      files.map(async (f) => {
        if (f.status !== 'accepted') return f;
        const formData = new FormData();
        formData.append('file', f.file);
        try {
          const res = await fetch('/documents/upload', {
            method: 'POST',
            body: formData,
          });
          if (!res.ok) throw new Error('Upload failed');
          const data = await res.json();
          return { ...f, status: 'uploaded' as UploadedFile['status'], serverPath: data.path };
        } catch (err: unknown) {
          let errorMsg = 'Unknown error';
          if (err instanceof Error) errorMsg = err.message;
          return { ...f, status: 'error' as UploadedFile['status'], error: errorMsg };
        }
      })
    );
    setFiles(updatedFiles as UploadedFile[]);
    setUploading(false);
  };

  const triggerExtraction = async (idx: number) => {
    setFiles((prev) => prev.map((f, i) => (i === idx ? { ...f, extractionStatus: 'extracting', extractionError: undefined } : f)));
    const file = files[idx];
    if (!file.serverPath) {
      setFiles((prev) => prev.map((f, i) => (i === idx ? { ...f, extractionStatus: 'error', extractionError: 'No server path for file.' } : f)));
      return;
    }
    try {
      const res = await fetch('/documents/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: file.file.name }),
      });
      if (!res.ok) throw new Error('Extraction failed');
      const data = await res.json();
      setFiles((prev) => prev.map((f, i) => (i === idx ? { ...f, extractionResult: data, extractionStatus: 'extracted' } : f)));
    } catch (err: unknown) {
      let errorMsg = 'Unknown error';
      if (err instanceof Error) errorMsg = err.message;
      setFiles((prev) => prev.map((f, i) => (i === idx ? { ...f, extractionStatus: 'error', extractionError: errorMsg } : f)));
    }
  };

  const handleExtractionAccept = (idx: number) => {
    setFiles((prev) => prev.map((f, i) => (i === idx ? { ...f, extractionAccepted: true } : f)));
  };

  const handleExtractionDeny = (idx: number) => {
    setFiles((prev) => prev.map((f, i) => (i === idx ? { ...f, extractionAccepted: false } : f)));
  };

  return (
    <div className="w-full max-w-xl">
      <div
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 flex flex-col items-center justify-center bg-white cursor-pointer hover:border-blue-400 transition mb-6"
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          multiple
          className="hidden"
          ref={fileInputRef}
          onChange={handleFileChange}
        />
        <span className="text-gray-500">Drag and drop files here, or <span className="text-blue-600 underline">browse</span></span>
      </div>
      {files.length > 0 && (
        <div className="space-y-4">
          {files.map((f, idx) => (
            <div key={idx} className="flex flex-col gap-2 bg-gray-100 rounded p-3 mb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {getFileTypeIcon(f.file) && <span className="text-2xl">{getFileTypeIcon(f.file)}</span>}
                  <span className="font-medium text-gray-700">{f.file.name}</span>
                  <span className="text-xs text-gray-400">({Math.round(f.file.size / 1024)} KB)</span>
                  {f.file.type.startsWith('image/') && (
                    <img src={f.previewUrl} alt="preview" className="w-10 h-10 object-cover rounded" />
                  )}
                  {f.file.type === 'application/pdf' && (
                    <span className="text-xs text-blue-700">PDF preview not available</span>
                  )}
                  {(f.file.name.endsWith('.doc') || f.file.name.endsWith('.docx')) && (
                    <span className="text-xs text-green-700">DOCX</span>
                  )}
                  <span className={`ml-2 text-xs px-2 py-1 rounded ${f.status === 'accepted' ? 'bg-green-100 text-green-700' : f.status === 'denied' ? 'bg-red-100 text-red-700' : f.status === 'uploaded' ? 'bg-blue-100 text-blue-700' : f.status === 'uploading' ? 'bg-yellow-100 text-yellow-700' : f.status === 'error' ? 'bg-red-200 text-red-800' : 'bg-yellow-100 text-yellow-700'}`}>{f.status}</span>
                  {f.error && <span className="text-xs text-red-500 ml-2">{f.error}</span>}
                </div>
                <div className="flex gap-2">
                  <button
                    className="px-2 py-1 bg-green-500 text-white rounded hover:bg-green-600 text-xs"
                    onClick={() => handleAccept(idx)}
                    disabled={f.status === 'accepted' || f.status === 'uploaded' || f.status === 'uploading'}
                  >
                    Accept
                  </button>
                  <button
                    className="px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-xs"
                    onClick={() => handleDeny(idx)}
                    disabled={f.status === 'denied' || f.status === 'uploaded' || f.status === 'uploading'}
                  >
                    Deny
                  </button>
                  <button
                    className="px-2 py-1 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 text-xs"
                    onClick={() => handleRemove(idx)}
                    disabled={f.status === 'uploading'}
                  >
                    Remove
                  </button>
                </div>
              </div>
              {f.status === 'uploaded' && (
                <div className="flex gap-2 mt-2">
                  <button
                    className="px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-xs"
                    onClick={() => triggerExtraction(idx)}
                    disabled={f.extractionStatus === 'extracting'}
                  >
                    {f.extractionStatus === 'extracting' ? 'Extracting...' : 'Extract Document'}
                  </button>
                  {f.extractionStatus === 'extracted' && (
                    <>
                      <button
                        className={`px-2 py-1 rounded text-xs ${f.extractionAccepted ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'}`}
                        onClick={() => handleExtractionAccept(idx)}
                      >
                        Accept Extraction
                      </button>
                      <button
                        className={`px-2 py-1 rounded text-xs ${!f.extractionAccepted ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-700'}`}
                        onClick={() => handleExtractionDeny(idx)}
                      >
                        Deny Extraction
                      </button>
                    </>
                  )}
                </div>
              )}
              {f.extractionStatus === 'extracting' && <div className="text-xs text-blue-500 mt-1">Extracting...</div>}
              {f.extractionStatus === 'error' && <div className="text-xs text-red-500 mt-1">Extraction error: {f.extractionError}</div>}
              {f.extractionStatus === 'extracted' && (
                <div className="bg-white rounded p-3 mt-2 border border-gray-200">
                  <h4 className="font-semibold mb-1 text-sm">Extraction Result</h4>
                  <pre className="text-xs whitespace-pre-wrap break-all">
                    {(() => {
                      try {
                        if (typeof f.extractionResult === 'string') return f.extractionResult;
                        if (typeof f.extractionResult === 'object' && f.extractionResult !== null) return JSON.stringify(f.extractionResult, null, 2);
                        return String(f.extractionResult ?? '');
                      } catch {
                        return '';
                      }
                    })()}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      <div className="flex gap-4 mt-6">
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          Add More Files
        </button>
        <button
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          onClick={uploadFiles}
          disabled={uploading || files.filter(f => f.status === 'accepted').length === 0}
        >
          {uploading ? 'Uploading...' : 'Upload Accepted Files'}
        </button>
      </div>
    </div>
  );
}