'use client';

import { useState, useEffect, useCallback, Suspense } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AuthGuard from '@/components/AuthGuard';
import { useSearchParams } from 'next/navigation';
import {
  Play,
  Pause,
  CheckCircle,
  Clock,
  AlertCircle,
  Edit,
  Download,
  RefreshCw,
  FileText,
  Search,
  PenTool,
  Shield,
  Brain,
  Target
} from 'lucide-react';

interface WorkflowStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'error' | 'paused';
  progress: number; // 0-100
  startTime?: Date;
  endTime?: Date;
  duration?: number; // in seconds
  result?: Record<string, unknown>;
  error?: string;
  canModify: boolean;
  canApprove: boolean;
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  status: 'idle' | 'running' | 'paused' | 'completed' | 'error';
  currentStep: number;
  totalSteps: number;
  steps: WorkflowStep[];
  createdAt: Date;
  updatedAt: Date;
  estimatedDuration: number; // in minutes
}

interface WorkflowResult {
  type: 'research' | 'extraction' | 'draft' | 'validation';
  content: Record<string, unknown>;
  metadata: {
    sources?: string[];
    confidence?: number;
    timestamp: Date;
  };
}

function WorkflowContent() {
  const { session } = useAuth();
  const searchParams = useSearchParams();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [currentWorkflow, setCurrentWorkflow] = useState<Workflow | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedResult, setSelectedResult] = useState<WorkflowResult | null>(null);

  // Load user's workflows
  const loadWorkflows = useCallback(async () => {
    if (!session?.access_token) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/workflows`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setWorkflows(data.workflows || []);
      }
    } catch (error) {
      console.error('Error loading workflows:', error);
      setError('Failed to load workflows');
    }
  }, [session?.access_token]);



  // Control workflow
  const controlWorkflow = useCallback(async (action: 'start' | 'pause' | 'resume' | 'stop') => {
    if (!currentWorkflow || !session?.access_token) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/workflows/${currentWorkflow.id}/control`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action }),
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentWorkflow(data.workflow);
      }
    } catch (error) {
      console.error('Error controlling workflow:', error);
      setError('Failed to control workflow');
    }
  }, [currentWorkflow, session?.access_token]);

  // Approve step
  const approveStep = useCallback(async (stepId: string) => {
    if (!currentWorkflow || !session?.access_token) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/workflows/${currentWorkflow.id}/steps/${stepId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentWorkflow(data.workflow);
      }
    } catch (error) {
      console.error('Error approving step:', error);
      setError('Failed to approve step');
    }
  }, [currentWorkflow, session?.access_token]);

  // Modify step
  const modifyStep = useCallback(async (stepId: string, modifications: Record<string, unknown>) => {
    if (!currentWorkflow || !session?.access_token) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/workflows/${currentWorkflow.id}/steps/${stepId}/modify`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ modifications }),
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentWorkflow(data.workflow);
      }
    } catch (error) {
      console.error('Error modifying step:', error);
      setError('Failed to modify step');
    }
  }, [currentWorkflow, session?.access_token]);

  // Export workflow results
  const exportWorkflow = useCallback(async (format: 'pdf' | 'docx' | 'json') => {
    if (!currentWorkflow || !session?.access_token) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/workflows/${currentWorkflow.id}/export`, {
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
        a.download = `workflow-${currentWorkflow.id}.${format}`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Error exporting workflow:', error);
      setError('Failed to export workflow');
    }
  }, [currentWorkflow, session?.access_token]);

  // Get step icon
  const getStepIcon = (stepName: string) => {
    const icons: Record<string, React.ReactNode> = {
      'research': <Search className="w-5 h-5" />,
      'extraction': <FileText className="w-5 h-5" />,
      'drafting': <PenTool className="w-5 h-5" />,
      'validation': <Shield className="w-5 h-5" />,
      'analysis': <Brain className="w-5 h-5" />,
      'review': <Target className="w-5 h-5" />,
    };
    return icons[stepName.toLowerCase()] || <FileText className="w-5 h-5" />;
  };

  // Get step status color
  const getStepStatusColor = (status: WorkflowStep['status']) => {
    const colors = {
      pending: 'text-gray-400',
      running: 'text-blue-500',
      completed: 'text-green-500',
      error: 'text-red-500',
      paused: 'text-yellow-500',
    };
    return colors[status];
  };

  // Get step status icon
  const getStepStatusIcon = (status: WorkflowStep['status']) => {
    const icons = {
      pending: <Clock className="w-4 h-4" />,
      running: <RefreshCw className="w-4 h-4 animate-spin" />,
      completed: <CheckCircle className="w-4 h-4" />,
      error: <AlertCircle className="w-4 h-4" />,
      paused: <Pause className="w-4 h-4" />,
    };
    return icons[status];
  };

  // Calculate workflow progress
  const getWorkflowProgress = (workflow: Workflow) => {
    const completedSteps = workflow.steps.filter(step => step.status === 'completed').length;
    return Math.round((completedSteps / workflow.totalSteps) * 100);
  };

  // Format duration
  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  // Load specific workflow if workflow_id is provided in URL
  const loadSpecificWorkflow = useCallback(async (workflowId: string) => {
    if (!session?.access_token) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/workflows/${workflowId}`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentWorkflow(data.workflow);
      } else {
        setError('Failed to load workflow');
      }
    } catch (error) {
      console.error('Error loading specific workflow:', error);
      setError('Failed to load workflow');
    }
  }, [session?.access_token]);

  useEffect(() => {
    loadWorkflows();

    // Check if workflow_id is provided in URL
    const workflowId = searchParams.get('workflow_id');
    if (workflowId) {
      loadSpecificWorkflow(workflowId);
    }
  }, [loadWorkflows, loadSpecificWorkflow, searchParams]);

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Workflow Dashboard</h1>
              <p className="text-gray-600">Monitor and control sequential agent workflows</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => window.history.back()}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                ← Back
              </button>
              <button
                onClick={() => loadWorkflows()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <AlertCircle className="w-5 h-5 text-red-400 mr-3" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {!currentWorkflow ? (
          /* Workflow List View */
          <div>
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Workflows</h2>
              {workflows.length === 0 && (
                <div className="text-center py-12">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No workflows yet</h3>
                  <p className="text-gray-600 mb-4">Start a workflow from your chat to see it here</p>
                  <button
                    onClick={() => window.location.href = '/chat'}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Go to Chat
                  </button>
                </div>
              )}
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {workflows.map((workflow) => (
                <div
                  key={workflow.id}
                  className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => setCurrentWorkflow(workflow)}
                >
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">{workflow.name}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      workflow.status === 'completed' ? 'bg-green-100 text-green-800' :
                      workflow.status === 'running' ? 'bg-blue-100 text-blue-800' :
                      workflow.status === 'error' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {workflow.status}
                    </span>
                  </div>

                  <p className="text-gray-600 text-sm mb-4">{workflow.description}</p>

                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Progress</span>
                      <span>{getWorkflowProgress(workflow)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${getWorkflowProgress(workflow)}%` }}
                      />
                    </div>
                  </div>

                  <div className="flex justify-between text-sm text-gray-500">
                    <span>{workflow.currentStep} / {workflow.totalSteps} steps</span>
                    <span>{formatDuration(workflow.estimatedDuration * 60)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          /* Workflow Detail View */
          <div>
            {/* Workflow Header */}
            <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{currentWorkflow.name}</h2>
                  <p className="text-gray-600">{currentWorkflow.description}</p>
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={() => setCurrentWorkflow(null)}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800"
                  >
                    ← Back to List
                  </button>
                  {currentWorkflow.status === 'completed' && (
                    <button
                      onClick={() => exportWorkflow('pdf')}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Export
                    </button>
                  )}
                </div>
              </div>

              {/* Overall Progress */}
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Overall Progress</span>
                  <span>{getWorkflowProgress(currentWorkflow)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${getWorkflowProgress(currentWorkflow)}%` }}
                  />
                </div>
              </div>

              {/* Workflow Controls */}
              <div className="flex space-x-3">
                {currentWorkflow.status === 'idle' && (
                  <button
                    onClick={() => controlWorkflow('start')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Start Workflow
                  </button>
                )}
                {currentWorkflow.status === 'running' && (
                  <>
                    <button
                      onClick={() => controlWorkflow('pause')}
                      className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
                    >
                      <Pause className="w-4 h-4 mr-2" />
                      Pause
                    </button>
                    <button
                      onClick={() => controlWorkflow('stop')}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    >
                      Stop
                    </button>
                  </>
                )}
                {currentWorkflow.status === 'paused' && (
                  <button
                    onClick={() => controlWorkflow('resume')}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Resume
                  </button>
                )}
              </div>
            </div>

            {/* Workflow Steps */}
            <div className="grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Workflow Steps</h3>
                                     <div className="space-y-4">
                     {currentWorkflow.steps.map((step) => (
                      <div
                        key={step.id}
                        className={`border rounded-lg p-4 ${
                          step.status === 'running' ? 'border-blue-300 bg-blue-50' :
                          step.status === 'completed' ? 'border-green-300 bg-green-50' :
                          step.status === 'error' ? 'border-red-300 bg-red-50' :
                          'border-gray-200'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <div className={`p-2 rounded-lg ${
                              step.status === 'running' ? 'bg-blue-100' :
                              step.status === 'completed' ? 'bg-green-100' :
                              step.status === 'error' ? 'bg-red-100' :
                              'bg-gray-100'
                            }`}>
                              {getStepIcon(step.name)}
                            </div>
                            <div>
                              <h4 className="font-medium text-gray-900">{step.name}</h4>
                              <p className="text-sm text-gray-600">{step.description}</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className={getStepStatusColor(step.status)}>
                              {getStepStatusIcon(step.status)}
                            </div>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              step.status === 'completed' ? 'bg-green-100 text-green-800' :
                              step.status === 'running' ? 'bg-blue-100 text-blue-800' :
                              step.status === 'error' ? 'bg-red-100 text-red-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {step.status}
                            </span>
                          </div>
                        </div>

                        {/* Step Progress */}
                        {step.status === 'running' && (
                          <div className="mb-3">
                            <div className="flex justify-between text-sm text-gray-600 mb-1">
                              <span>Progress</span>
                              <span>{step.progress}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${step.progress}%` }}
                              />
                            </div>
                          </div>
                        )}

                        {/* Step Duration */}
                        {step.duration && (
                          <div className="text-sm text-gray-500 mb-3">
                            Duration: {formatDuration(step.duration)}
                          </div>
                        )}

                        {/* Step Error */}
                        {step.error && (
                          <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                            <p className="text-sm text-red-800">{step.error}</p>
                          </div>
                        )}

                        {/* Step Actions */}
                        <div className="flex space-x-2">
                          {step.canModify && step.status === 'completed' && (
                            <button
                              onClick={() => modifyStep(step.id, {})}
                              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                            >
                              <Edit className="w-3 h-3 mr-1" />
                              Modify
                            </button>
                          )}
                          {step.canApprove && step.status === 'completed' && (
                            <button
                              onClick={() => approveStep(step.id)}
                              className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200"
                            >
                              <CheckCircle className="w-3 h-3 mr-1" />
                              Approve
                            </button>
                          )}
                                                     {step.result && (
                             <button
                               onClick={() => setSelectedResult({
                                 type: 'research',
                                 content: step.result || {},
                                 metadata: {
                                   confidence: 85,
                                   timestamp: new Date()
                                 }
                               })}
                               className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                             >
                               View Result
                             </button>
                           )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Results Panel */}
              <div className="lg:col-span-1">
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Results</h3>
                  {selectedResult ? (
                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-medium text-gray-900 capitalize">{selectedResult.type}</h4>
                        <button
                          onClick={() => setSelectedResult(null)}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          ×
                        </button>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3 mb-3">
                        <pre className="text-sm text-gray-800 whitespace-pre-wrap">
                          {JSON.stringify(selectedResult.content, null, 2)}
                        </pre>
                      </div>
                      <div className="text-xs text-gray-500">
                        Confidence: {selectedResult.metadata.confidence}%<br />
                        Sources: {selectedResult.metadata.sources?.length || 0}<br />
                        Generated: {new Date(selectedResult.metadata.timestamp).toLocaleString()}
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <FileText className="w-8 h-8 mx-auto mb-2" />
                      <p>Select a step to view its results</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
                 )}
       </div>
     </div>
     </AuthGuard>
   );
 }

// Default export component that wraps WorkflowContent with Suspense
export default function WorkflowPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading workflow dashboard...</p>
        </div>
      </div>
    }>
      <WorkflowContent />
    </Suspense>
  );
}