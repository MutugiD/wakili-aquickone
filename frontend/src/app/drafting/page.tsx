'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  FileText,
  MessageSquare,
  Download,
  Plus,
  AlertCircle,
  RefreshCw,
  Eye
} from 'lucide-react';

interface DraftVersion {
  id: string;
  content: string;
  status: 'pending' | 'approved' | 'rejected' | 'modified';
  feedback?: string;
  createdAt: string;
  modifiedAt?: string;
}

interface DocumentDraft {
  id: string;
  title: string;
  description: string;
  status: 'active' | 'archived' | 'deleted';
  currentVersion: number;
  versions: DraftVersion[];
  chatId?: string;
  workflowId?: string;
  createdAt: string;
  updatedAt: string;
  settings: {
    autoApprove: boolean;
    requireFeedback: boolean;
    maxVersions: number;
  };
}

export default function DraftingDashboard() {
  const { session } = useAuth();
  const router = useRouter();
  const [drafts, setDrafts] = useState<DocumentDraft[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // const [selectedDraft, setSelectedDraft] = useState<DocumentDraft | null>(null); // TODO: Implement draft selection
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Load user's drafts
  const loadDrafts = useCallback(async () => {
    if (!session?.access_token) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/drafting/`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDrafts(data.drafts || []);
      } else {
        setError('Failed to load drafts');
      }
    } catch (error) {
      console.error('Error loading drafts:', error);
      setError('Failed to load drafts');
    } finally {
      setLoading(false);
    }
  }, [session?.access_token]);

  // Create draft from chat ID or content
  const createDraftFromChatOrContent = useCallback(async (chatId: string, chatContent: string, documentType: string) => {
    if (!session?.access_token) return;

    try {
      const payload: {
        chat_id?: string;
        chat_content?: string;
        document_type?: string;
      } = {};

      if (chatId.trim()) {
        payload.chat_id = chatId;
      }

      if (chatContent.trim()) {
        payload.chat_content = chatContent;
      }

      if (documentType.trim()) {
        payload.document_type = documentType;
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/drafting/create-from-chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        setDrafts(prev => [data.draft, ...prev]);
        setShowCreateModal(false);
        router.push(`/drafting/${data.draft.id}`);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create draft');
      }
    } catch (error) {
      console.error('Error creating draft:', error);
      setError('Failed to create draft');
    }
  }, [session?.access_token, router]);

  // Approve draft version - TODO: Implement in UI
  // const approveDraftVersion = useCallback(async (draftId: string, versionId: string) => {
  //   if (!session?.access_token) return;

  //   try {
  //     const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/drafting/${draftId}/versions/${versionId}/approve`, {
  //       method: 'POST',
  //       headers: {
  //         'Authorization': `Bearer ${session.access_token}`,
  //         'Content-Type': 'application/json',
  //       },
  //     });

  //     if (response.ok) {
  //       const data = await response.json();
  //       setDrafts(prev => prev.map(draft =>
  //         draft.id === draftId ? data.draft : draft
  //       ));
  //       if (selectedDraft?.id === draftId) {
  //         setSelectedDraft(data.draft);
  //       }
  //     }
  //   } catch (error) {
  //     console.error('Error approving draft:', error);
  //     setError('Failed to approve draft');
  //   }
  // }, [session?.access_token, selectedDraft]);

  // Reject draft version - TODO: Implement in UI
  // const rejectDraftVersion = useCallback(async (draftId: string, versionId: string, feedback: string) => {
  //   if (!session?.access_token) return;

  //   try {
  //     const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/drafting/${draftId}/versions/${versionId}/reject`, {
  //       method: 'POST',
  //       headers: {
  //         'Authorization': `Bearer ${session.access_token}`,
  //         'Content-Type': 'application/json',
  //       },
  //       body: JSON.stringify({ feedback }),
  //     });

  //     if (response.ok) {
  //       const data = await response.json();
  //       setDrafts(prev => prev.map(draft =>
  //         draft.id === draftId ? data.draft : draft
  //       ));
  //       if (selectedDraft?.id === draftId) {
  //         setSelectedDraft(data.draft);
  //       }
  //     }
  //   } catch (error) {
  //     console.error('Error rejecting draft:', error);
  //     setError('Failed to reject draft');
  //   }
  // }, [session?.access_token, selectedDraft]);

  // Export draft
  const exportDraft = useCallback(async (draftId: string, format: 'pdf' | 'docx' | 'json' | 'txt') => {
    if (!session?.access_token) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/drafting/${draftId}/export`, {
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
        a.download = `draft-${draftId}.${format}`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Error exporting draft:', error);
      setError('Failed to export draft');
    }
  }, [session?.access_token]);

  useEffect(() => {
    loadDrafts();
  }, [loadDrafts]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'text-green-600 bg-green-100';
      case 'rejected': return 'text-red-600 bg-red-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      case 'modified': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  // Status icon helper - TODO: Implement in UI
  // const getStatusIcon = (status: string) => {
  //   switch (status) {
  //     case 'approved': return <CheckCircle className="w-4 h-4" />;
  //     case 'rejected': return <XCircle className="w-4 h-4" />;
  //     case 'pending': return <Clock className="w-4 h-4" />;
  //     case 'modified': return <Edit className="w-4 h-4" />;
  //     default: return <AlertCircle className="w-4 h-4" />;
  //   }
  // };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Link href="/dashboard" className="text-2xl font-bold text-gray-900 hover:text-emerald-600">
                Wakili Quick1
              </Link>
              <span className="ml-2 text-sm text-gray-500">Document Drafting</span>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => loadDrafts()}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span className="text-sm">Refresh</span>
              </button>
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center space-x-2 bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>New Draft</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <AlertCircle className="w-5 h-5 text-red-400 mr-3" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Welcome Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Document Drafting</h1>
              <p className="text-gray-600">
                Review, approve, and manage AI-generated legal documents from your conversations.
              </p>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <FileText className="w-4 h-4" />
              <span>{drafts.length} drafts</span>
            </div>
          </div>
        </div>

        {/* Drafts Grid */}
        {drafts.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No drafts yet</h3>
            <p className="text-gray-600 mb-4">
              Start a conversation in chat to generate your first document draft.
            </p>
            <div className="flex justify-center space-x-4">
              <Link
                href="/chat"
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
              >
                <MessageSquare className="w-4 h-4 inline mr-2" />
                Go to Chat
              </Link>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Plus className="w-4 h-4 inline mr-2" />
                Create from Chat
              </button>
            </div>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {drafts.map((draft) => {
              const currentVersion = draft.versions[draft.currentVersion - 1];
              return (
                <div
                  key={draft.id}
                  className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => router.push(`/drafting/${draft.id}`)}
                >
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 truncate">{draft.title}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(currentVersion?.status || 'pending')}`}>
                      {currentVersion?.status || 'pending'}
                    </span>
                  </div>

                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">{draft.description}</p>

                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <span>Version {draft.currentVersion}</span>
                    <span>{new Date(draft.updatedAt).toLocaleDateString()}</span>
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/drafting/${draft.id}`);
                      }}
                      className="flex-1 px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                    >
                      <Eye className="w-3 h-3 inline mr-1" />
                      Review
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        exportDraft(draft.id, 'pdf');
                      }}
                      className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                    >
                      <Download className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create Draft Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Create Draft from Chat</h3>
            <p className="text-gray-600 mb-4">
              You can either enter a chat ID or paste chat content directly below.
            </p>

            <div className="space-y-4">
              {/* Chat ID Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Chat ID (Optional)</label>
                <input
                  type="text"
                  placeholder="Enter chat ID to load existing conversation"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  id="chatId"
                />
              </div>

              {/* Chat Content Textarea */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Chat Content</label>
                <textarea
                  placeholder="Paste your chat conversation here...&#10;&#10;Example:&#10;User: I need to create an employment contract&#10;Assistant: I'll help you create an employment contract. What are the details?&#10;User: The employee is John Doe, position is Software Engineer, salary is $80,000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 min-h-[200px] resize-y"
                  id="chatContent"
                />
              </div>

              {/* Document Type Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Document Type (Optional)</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  id="documentType"
                >
                  <option value="">Auto-detect from content</option>
                  <option value="employment_contract">Employment Contract</option>
                  <option value="offer_letter">Offer Letter</option>
                  <option value="demand_letter">Demand Letter</option>
                  <option value="contract">General Contract</option>
                  <option value="plaint">Plaint</option>
                  <option value="affidavit">Affidavit</option>
                  <option value="brief">Legal Brief</option>
                </select>
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    const chatId = (document.getElementById('chatId') as HTMLInputElement).value;
                    const chatContent = (document.getElementById('chatContent') as HTMLTextAreaElement).value;
                    const documentType = (document.getElementById('documentType') as HTMLSelectElement).value;

                    if (chatId || chatContent.trim()) {
                      createDraftFromChatOrContent(chatId, chatContent, documentType);
                    }
                  }}
                  className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
                >
                  Create Draft
                </button>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}