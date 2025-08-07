'use client';

import React, { useState, useEffect, Suspense, useMemo } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

interface DocumentTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  fields: string[];
}

interface FormData {
  document_type: string;
  schema: Record<string, unknown>;
  form_structure: {
    fields: Record<string, unknown>;
    field_order: string[];
    sections: Array<{
      name: string;
      fields: string[];
    }>;
  };
  validation_rules: Record<string, unknown>;
  interaction_flow: Record<string, unknown>;
  extracted_info: Record<string, unknown>;
  missing_info: string[];
}

function DocumentCreationContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { session } = useAuth();
  const [currentStep, setCurrentStep] = useState<'template' | 'upload' | 'review' | 'generate'>('template');
  const [selectedTemplate, setSelectedTemplate] = useState<DocumentTemplate | null>(null);
  const [formData, setFormData] = useState<FormData | null>(null);
  const [userInput, setUserInput] = useState<Record<string, unknown>>({});
  const [isLoading, setIsLoading] = useState(false);

  const documentTemplates: DocumentTemplate[] = useMemo(() => [
    {
      id: 'employment_contract',
      name: 'Employment Contract',
      description: 'Standard employment agreement between employer and employee',
      category: 'employment',
      fields: ['employer', 'employee', 'position', 'salary', 'start_date', 'duration']
    },
    {
      id: 'lease_agreement',
      name: 'Lease Agreement',
      description: 'Property rental agreement between landlord and tenant',
      category: 'property',
      fields: ['landlord', 'tenant', 'property', 'rent', 'duration', 'utilities']
    },
    {
      id: 'partnership_agreement',
      name: 'Partnership Agreement',
      description: 'Business partnership agreement between partners',
      category: 'business',
      fields: ['partner1', 'partner2', 'business_name', 'capital', 'profit_sharing', 'management']
    },
    {
      id: 'service_agreement',
      name: 'Service Agreement',
      description: 'Service provision agreement between client and service provider',
      category: 'services',
      fields: ['client', 'service_provider', 'scope', 'payment', 'deliverables', 'timeline']
    }
  ], []);

  // Pre-fill form with extracted information
  useEffect(() => {
    if (formData?.extracted_info) {
      setUserInput(formData.extracted_info);
    }
  }, [formData]);

  // Get form data from URL params
  useEffect(() => {
    const formDataParam = searchParams.get('formData');
    if (formDataParam) {
      try {
        const parsed = JSON.parse(decodeURIComponent(formDataParam));
        setFormData(parsed);

        // If we have form data, skip template selection and go directly to review
        if (parsed.document_type) {
          // Find the matching template
          const matchingTemplate = documentTemplates.find(template =>
            template.id === parsed.document_type ||
            template.name.toLowerCase().includes(parsed.document_type.replace('_', ' '))
          );

          if (matchingTemplate) {
            setSelectedTemplate(matchingTemplate);
            setCurrentStep('review'); // Skip template and upload, go directly to review
          }
        }
      } catch (error) {
        console.error('Error parsing form data:', error);
      }
    }
  }, [searchParams, documentTemplates]); // Added documentTemplates to dependency array

  const handleTemplateSelect = (template: DocumentTemplate) => {
    setSelectedTemplate(template);
    setCurrentStep('upload');
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      // Handle file upload logic here
      console.log('Files uploaded:', files);
      setCurrentStep('review');
    }
  };

  const handleInputChange = (fieldName: string, value: unknown) => {
    setUserInput(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  const handleGenerateDocument = async () => {
    setIsLoading(true);
    try {
      // Call backend to generate document
      const response = await fetch('/api/documents/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`
        },
        body: JSON.stringify({
          document_type: selectedTemplate?.id,
          form_data: formData,
          user_input: userInput
        })
      });

      if (response.ok) {
        const result = await response.json();
        // Handle successful document generation
        console.log('Document generated:', result);
        // Redirect to download or show success message
      }
    } catch (error) {
      console.error('Error generating document:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderTemplateSelection = () => (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Document Creation</h1>
        <p className="text-gray-600">Select a document template to get started</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {documentTemplates.map((template) => (
          <div
            key={template.id}
            className="border border-gray-200 rounded-lg p-6 hover:border-blue-500 hover:shadow-lg transition-all cursor-pointer"
            onClick={() => handleTemplateSelect(template)}
          >
            <h3 className="text-xl font-semibold text-gray-900 mb-2">{template.name}</h3>
            <p className="text-gray-600 mb-4">{template.description}</p>
            <div className="flex items-center justify-between">
              <span className="text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded">
                {template.category}
              </span>
              <button className="text-blue-600 hover:text-blue-800 font-medium">
                Select →
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderUploadSection = () => (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {selectedTemplate?.name} - Upload Documents
        </h2>
        <p className="text-gray-600">Upload any relevant documents or continue with form</p>
      </div>

      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        <input
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt"
          onChange={handleFileUpload}
          className="hidden"
          id="file-upload"
        />
        <label htmlFor="file-upload" className="cursor-pointer">
          <div className="space-y-4">
            <div className="text-6xl text-gray-400">📄</div>
            <div>
              <p className="text-lg font-medium text-gray-900">Upload Documents</p>
              <p className="text-gray-500">Drag and drop files here, or click to browse</p>
            </div>
          </div>
        </label>
      </div>

      <div className="mt-6 flex justify-between">
        <button
          onClick={() => setCurrentStep('template')}
          className="px-4 py-2 text-gray-600 hover:text-gray-800"
        >
          ← Back to Templates
        </button>
        <button
          onClick={() => setCurrentStep('review')}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Continue to Review →
        </button>
      </div>
    </div>
  );

    const renderReviewSection = () => (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {selectedTemplate?.name || 'Employment Contract'} - Review and Complete
        </h2>
        <p className="text-gray-600">Please review and complete the required information for your {selectedTemplate?.name?.toLowerCase() || 'employment contract'}</p>
      </div>

      {/* Show extracted information summary */}
      {formData?.extracted_info && Object.keys(formData.extracted_info).length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">Information Extracted from Conversation</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.entries(formData.extracted_info).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="font-medium text-blue-800">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
                <span className="text-blue-700">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Show missing information */}
      {formData?.missing_info && formData.missing_info.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold text-yellow-900 mb-3">Missing Information</h3>
          <p className="text-yellow-800 mb-2">Please provide the following information:</p>
          <ul className="list-disc list-inside text-yellow-700 space-y-1">
            {formData.missing_info.map((info, index) => (
              <li key={index}>{info}</li>
            ))}
          </ul>
        </div>
      )}

      {formData && (
        <div className="space-y-6">
          {formData.form_structure?.sections?.map((section, sectionIndex: number) => (
            <div key={sectionIndex} className="border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">{section.name}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {section.fields.map((fieldName: string) => {
                  const fieldConfig = formData.form_structure.fields[fieldName] as {
                    type: string;
                    label: string;
                    required: boolean;
                    options?: string[];
                  };
                  if (!fieldConfig) return null;

                  return (
                    <div key={fieldName} className="space-y-2">
                      <label className="block text-sm font-medium text-gray-700">
                        {fieldConfig.label}
                        {fieldConfig.required && <span className="text-red-500">*</span>}
                      </label>
                                             {fieldConfig.type === 'text' && (
                         <input
                           type="text"
                           value={(userInput[fieldName] as string) || ''}
                           onChange={(e) => handleInputChange(fieldName, e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder={`Enter ${fieldConfig.label.toLowerCase()}`}
                        />
                      )}
                                             {fieldConfig.type === 'textarea' && (
                         <textarea
                           value={(userInput[fieldName] as string) || ''}
                           onChange={(e) => handleInputChange(fieldName, e.target.value)}
                          rows={3}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder={`Enter ${fieldConfig.label.toLowerCase()}`}
                        />
                      )}
                                             {fieldConfig.type === 'number' && (
                         <input
                           type="number"
                           value={(userInput[fieldName] as string) || ''}
                           onChange={(e) => handleInputChange(fieldName, e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder={`Enter ${fieldConfig.label.toLowerCase()}`}
                        />
                      )}
                                             {fieldConfig.type === 'date' && (
                         <input
                           type="date"
                           value={(userInput[fieldName] as string) || ''}
                           onChange={(e) => handleInputChange(fieldName, e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      )}
                                             {fieldConfig.type === 'select' && (
                         <select
                           value={(userInput[fieldName] as string) || ''}
                           onChange={(e) => handleInputChange(fieldName, e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Select {fieldConfig.label.toLowerCase()}</option>
                          {fieldConfig.options?.map((option: string) => (
                            <option key={option} value={option}>{option}</option>
                          ))}
                        </select>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-8 flex justify-between">
        <button
          onClick={() => setCurrentStep('upload')}
          className="px-4 py-2 text-gray-600 hover:text-gray-800"
        >
          ← Back to Upload
        </button>
        <button
          onClick={() => setCurrentStep('generate')}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Generate Document →
        </button>
      </div>
    </div>
  );

  const renderGenerateSection = () => (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Generate Document</h2>
        <p className="text-gray-600">Review your information and generate the final document</p>
      </div>

      <div className="bg-gray-50 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Document Type</p>
            <p className="font-medium">{selectedTemplate?.name}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Fields Completed</p>
            <p className="font-medium">{Object.keys(userInput).length} / {formData?.form_structure?.field_order?.length || 0}</p>
          </div>
        </div>
      </div>

      <div className="flex justify-between">
        <button
          onClick={() => setCurrentStep('review')}
          className="px-4 py-2 text-gray-600 hover:text-gray-800"
        >
          ← Back to Review
        </button>
        <button
          onClick={handleGenerateDocument}
          disabled={isLoading}
          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
        >
          {isLoading ? 'Generating...' : 'Generate Document'}
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold text-gray-900">Document Creation</h1>
            <button
              onClick={() => router.push('/chat')}
              className="text-gray-600 hover:text-gray-800"
            >
              ← Back to Chat
            </button>
          </div>
        </div>
      </div>

      {currentStep === 'template' && renderTemplateSelection()}
      {currentStep === 'upload' && renderUploadSection()}
      {currentStep === 'review' && renderReviewSection()}
      {currentStep === 'generate' && renderGenerateSection()}
    </div>
  );
}

export default function DocumentCreationPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gray-50 flex items-center justify-center">Loading...</div>}>
      <DocumentCreationContent />
    </Suspense>
  );
}