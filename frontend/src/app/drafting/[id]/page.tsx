'use client';

import React, { useState, useCallback, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import {
  ArrowLeft,
  RefreshCw,
  Download,
  Plus,
  CheckCircle,
  XCircle,
  Edit,
  RotateCcw,
  Edit3,
  FileText
} from 'lucide-react';
import InteractiveDocumentEditor from '@/components/InteractiveDocumentEditor';

interface DraftVersion {
  id: string;
  content: string | DocumentContent;
  status: 'pending' | 'approved' | 'rejected';
  createdAt: string;
  feedback?: string;
}

interface DocumentContent {
  document_type?: string;
  content?: string | object;
  sections?: Array<{
    title?: string;
    content?: string | object;
  }>;
  metadata?: object;
  [key: string]: string | object | undefined;
}

interface DocumentDraft {
  id: string;
  title: string;
  description?: string;
  documentType: string;
  status: string;
  currentVersion: number;
  versions: DraftVersion[];
  createdAt: string;
  updatedAt: string;
  settings: {
    auto_approve?: boolean;
    require_user_approval?: boolean;
    max_versions?: number;
  };
}

// Helper function to convert structured content to displayable text
const convertContentToText = (content: string | DocumentContent | null | undefined): string => {
  if (!content) {
    return 'No content available';
  }

  // If content is already a string, return it
  if (typeof content === 'string') {
    return content;
  }

  // If content is an object, convert it to text
  if (typeof content === 'object') {
    const contentObj = content as DocumentContent;
    const textParts: string[] = [];

    // Handle sections if they exist
    if (contentObj.sections && Array.isArray(contentObj.sections)) {
      for (const section of contentObj.sections) {
        if (typeof section === 'object') {
          if (section.title) {
            textParts.push(`\n${section.title}\n`);
          }
          if (section.content) {
            textParts.push(String(section.content));
          }
        }
      }
    }

    // Handle main content
    if (contentObj.content) {
      if (typeof contentObj.content === 'string') {
        textParts.push(contentObj.content);
      } else if (typeof contentObj.content === 'object') {
        textParts.push(JSON.stringify(contentObj.content, null, 2));
      }
    }

    // Handle document type
    if (contentObj.document_type) {
      textParts.unshift(`Document Type: ${contentObj.document_type}\n`);
    }

    // Add any other string fields
    for (const [key, value] of Object.entries(contentObj)) {
      if (key !== 'sections' && key !== 'content' && key !== 'document_type' && typeof value === 'string') {
        textParts.push(`${key}: ${value}`);
      }
    }

    const result = textParts.join('\n');
    return result.trim() || 'Content exported successfully';
  }

  // Fallback
  return String(content);
};

export default function DraftReviewPage() {
  const { session } = useAuth();
  const [draft, setDraft] = useState<DocumentDraft | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<DraftVersion | null>(null);
  const [editedContent, setEditedContent] = useState<string>('');
  const [feedback, setFeedback] = useState<string>('');
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [isInteractiveEditing, setIsInteractiveEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load draft details
  const loadDraft = useCallback(async () => {
    if (!session?.access_token) return;

    try {
      const draftId = window.location.pathname.split('/').pop();
      if (!draftId) return;

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/drafting/${draftId}`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDraft(data.draft);

        // Set the current version as selected
        if (data.draft.versions && data.draft.versions.length > 0) {
          const currentVersion = data.draft.versions[data.draft.currentVersion - 1];
          setSelectedVersion(currentVersion);
          setEditedContent(convertContentToText(currentVersion.content));
        }
      } else {
        setError('Failed to load draft');
      }
    } catch (error) {
      console.error('Error loading draft:', error);
      setError('Failed to load draft');
    } finally {
      setLoading(false);
    }
  }, [session?.access_token]);

  // Handle interactive editor save
  const handleInteractiveSave = (sections: Array<{ content: string }>) => {
    const updatedContent = sections.map(section => section.content).join('\n\n');
    setEditedContent(updatedContent);
    setIsInteractiveEditing(false);
    // You can also save this to the backend here
  };

  // Handle interactive editor cancel
  const handleInteractiveCancel = () => {
    setIsInteractiveEditing(false);
  };

  useEffect(() => {
    loadDraft();
  }, [loadDraft]);

  // Generate draft version
  const generateDraftVersion = useCallback(async () => {
    if (!session?.access_token || !draft) return;

    setActionLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/drafting/${draft.id}/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ context: {} }),
      });

      if (response.ok) {
        const data = await response.json();
        setDraft(data.draft);

        // Check if there are any versions before accessing them
        if (data.draft.versions && data.draft.versions.length > 0) {
          const currentVersion = data.draft.versions[data.draft.currentVersion - 1];
          if (currentVersion) {
            setSelectedVersion(currentVersion);
            setEditedContent(convertContentToText(currentVersion.content));
          }
        }
      } else {
        setError('Failed to generate draft');
      }
    } catch (error) {
      console.error('Error generating draft:', error);
      setError('Failed to generate draft');
    } finally {
      setActionLoading(false);
    }
  }, [session?.access_token, draft]);

  // Approve draft version
  const approveDraftVersion = useCallback(async () => {
    if (!session?.access_token || !draft || !selectedVersion) return;

    setActionLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/drafting/${draft.id}/versions/${selectedVersion.id}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ feedback: '' }),
      });

      if (response.ok) {
        const data = await response.json();
        setDraft(data.draft);

        // Check if there are any versions before accessing them
        if (data.draft.versions && data.draft.versions.length > 0) {
          const currentVersion = data.draft.versions[data.draft.currentVersion - 1];
          if (currentVersion) {
            setSelectedVersion(currentVersion);
            setEditedContent(convertContentToText(currentVersion.content));
          }
        }
      } else {
        setError('Failed to approve draft');
      }
    } catch (error) {
      console.error('Error approving draft:', error);
      setError('Failed to approve draft');
    } finally {
      setActionLoading(false);
    }
  }, [session?.access_token, draft, selectedVersion]);

  // Reject draft version
  const rejectDraftVersion = useCallback(async () => {
    if (!session?.access_token || !draft || !selectedVersion) return;

    setActionLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/drafting/${draft.id}/versions/${selectedVersion.id}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ feedback }),
      });

      if (response.ok) {
        const data = await response.json();
        setDraft(data.draft);

        // Check if there are any versions before accessing them
        if (data.draft.versions && data.draft.versions.length > 0) {
          const currentVersion = data.draft.versions[data.draft.currentVersion - 1];
          if (currentVersion) {
            setSelectedVersion(currentVersion);
            setEditedContent(convertContentToText(currentVersion.content));
          }
        }
        setFeedback('');
        setShowFeedbackModal(false);
      } else {
        setError('Failed to reject draft');
      }
    } catch (error) {
      console.error('Error rejecting draft:', error);
      setError('Failed to reject draft');
    } finally {
      setActionLoading(false);
    }
  }, [session?.access_token, draft, selectedVersion, feedback]);

  // Regenerate draft version
  const regenerateDraftVersion = useCallback(async () => {
    if (!session?.access_token || !draft || !selectedVersion) return;

    setActionLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/drafting/${draft.id}/versions/${selectedVersion.id}/regenerate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ feedback }),
      });

      if (response.ok) {
        const data = await response.json();
        setDraft(data.draft);

        // Check if there are any versions before accessing them
        if (data.draft.versions && data.draft.versions.length > 0) {
          const currentVersion = data.draft.versions[data.draft.currentVersion - 1];
          if (currentVersion) {
            setSelectedVersion(currentVersion);
            setEditedContent(convertContentToText(currentVersion.content));
          }
        }
        setFeedback('');
        setShowFeedbackModal(false);
      } else {
        setError('Failed to regenerate draft');
      }
    } catch (error) {
      console.error('Error regenerating draft:', error);
      setError('Failed to regenerate draft');
    } finally {
      setActionLoading(false);
    }
  }, [session?.access_token, draft, selectedVersion, feedback]);

  // Export draft
  const exportDraft = useCallback(async (format: 'pdf' | 'docx') => {
    if (!session?.access_token || !draft) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/drafting/${draft.id}/export`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ format }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `draft-${draft.id}.${format}`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Error exporting draft:', error);
      setError('Failed to export draft');
    }
  }, [session?.access_token, draft]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <Link
                href="/drafting"
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Drafts</span>
              </Link>
              <div className="h-6 w-px bg-gray-300"></div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">{draft?.title}</h1>
                <p className="text-sm text-gray-500">Version {draft?.currentVersion}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => loadDraft()}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span className="text-sm">Refresh</span>
              </button>
              <div className="flex space-x-2">
                <button
                  onClick={() => exportDraft('pdf')}
                  className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                >
                  <Download className="w-3 h-3 inline mr-1" />
                  PDF
                </button>
                <button
                  onClick={() => exportDraft('docx')}
                  className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                >
                  <Download className="w-3 h-3 inline mr-1" />
                  DOCX
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800">{error}</p>
              </div>
            )}

            {loading ? (
              <div className="bg-white rounded-lg shadow p-8">
                <div className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
            ) : draft ? (
              <div className="bg-white rounded-lg shadow">
                {/* Draft Header */}
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900">{draft.title}</h2>
                      <div className="flex items-center space-x-4 mt-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          draft.status === 'approved' ? 'bg-green-100 text-green-800' :
                          draft.status === 'rejected' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {draft.status}
                        </span>
                        <span className="text-sm text-gray-500">Created: {new Date(draft.createdAt).toLocaleDateString()}</span>
                        <span className="text-sm text-gray-500">Updated: {new Date(draft.updatedAt).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      Document Type: {draft.documentType}
                    </div>
                  </div>
                </div>

                {/* Document Content */}
                <div className="p-6">
                  {isInteractiveEditing ? (
                    <InteractiveDocumentEditor
                      documentContent={editedContent || convertContentToText(selectedVersion?.content) || ''}
                      onSave={handleInteractiveSave}
                      onCancel={handleInteractiveCancel}
                      isEditing={true}
                      onToggleEdit={() => setIsInteractiveEditing(false)}
                    />
                  ) : (
                    <div className="space-y-4">
                      {/* Interactive Editor Toggle */}
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-gray-900">Document Content</h3>
                        <button
                          onClick={() => setIsInteractiveEditing(true)}
                          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                          <Edit3 className="w-4 h-4" />
                          <span>Interactive Editor</span>
                        </button>
                      </div>

                      {/* Simple Content Display */}
                      <div className="bg-gray-50 rounded-lg p-4">
                        <div className="whitespace-pre-wrap text-gray-900">
                          {editedContent || convertContentToText(selectedVersion?.content) || 'No content available'}
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                {!isInteractiveEditing && (
                  <div className="p-6 border-t border-gray-200 bg-gray-50">
                    <div className="flex space-x-3">
                      {!selectedVersion ? (
                        <button
                          onClick={generateDraftVersion}
                          disabled={actionLoading}
                          className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50"
                        >
                          <Plus className="w-4 h-4 inline mr-2" />
                          Generate Draft
                        </button>
                      ) : selectedVersion.status === 'pending' ? (
                        <>
                          <button
                            onClick={approveDraftVersion}
                            disabled={actionLoading}
                            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                          >
                            <CheckCircle className="w-4 h-4 inline mr-2" />
                            Approve
                          </button>
                          <button
                            onClick={() => setShowFeedbackModal(true)}
                            disabled={actionLoading}
                            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                          >
                            <XCircle className="w-4 h-4 inline mr-2" />
                            Reject
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            onClick={() => setIsInteractiveEditing(true)}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                          >
                            <Edit className="w-4 h-4 inline mr-2" />
                            Edit
                          </button>
                          <button
                            onClick={() => setShowFeedbackModal(true)}
                            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                          >
                            <RotateCcw className="w-4 h-4 inline mr-2" />
                            Regenerate
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-8 text-center">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Draft not found</h3>
                <p className="text-gray-600 mb-4">The draft you&apos;re looking for doesn&apos;t exist or has been deleted.</p>
                <Link
                  href="/drafting"
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
                >
                  Back to Drafts
                </Link>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Version History */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Version History</h3>
              <div className="space-y-2">
                {draft?.versions?.map((version, index) => (
                  <div
                    key={version.id}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedVersion?.id === version.id
                        ? 'bg-emerald-50 border border-emerald-200'
                        : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                    onClick={() => {
                      setSelectedVersion(version);
                      setEditedContent(convertContentToText(version.content));
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">Version {index + 1}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(version.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        version.status === 'approved' ? 'bg-green-100 text-green-800' :
                        version.status === 'rejected' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {version.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Draft Settings */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Draft Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Auto Approve</label>
                  <p className="text-sm text-gray-500 mt-1">
                    {draft?.settings?.auto_approve ? 'Enabled' : 'Disabled'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Require Feedback</label>
                  <p className="text-sm text-gray-500 mt-1">
                    {draft?.settings?.require_user_approval ? 'Required' : 'Optional'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Max Versions</label>
                  <p className="text-sm text-gray-500 mt-1">
                    {draft?.settings?.max_versions || 'Unlimited'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Provide Feedback</h3>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Enter your feedback or suggestions for improvement..."
              className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 mb-4"
            />
            <div className="flex space-x-3">
              <button
                onClick={rejectDraftVersion}
                disabled={actionLoading || !feedback.trim()}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                Reject with Feedback
              </button>
              <button
                onClick={regenerateDraftVersion}
                disabled={actionLoading || !feedback.trim()}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
              >
                Regenerate
              </button>
              <button
                onClick={() => {
                  setShowFeedbackModal(false);
                  setFeedback('');
                }}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}