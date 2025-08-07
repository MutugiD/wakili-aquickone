'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface FieldConfig {
  type: 'text' | 'textarea' | 'number' | 'date' | 'select';
  label: string;
  required: boolean;
  priority: 'high' | 'medium' | 'low';
  validation?: {
    min_length?: number;
    max_length?: number;
    min?: number;
    max?: number;
  };
  options?: string[];
  extraction_patterns?: string[];
}

interface FormData {
  document_type: string;
  name: string;
  description: string;
  fields: Record<string, FieldConfig>;
  field_order: string[];
  validation_rules: Record<string, unknown>;
  prefilled_data: Record<string, unknown>;
}

interface DynamicFormProps {
  formData: FormData;
  onFormSubmit: (data: Record<string, unknown>) => void;
  onFormCancel: () => void;
  isLoading?: boolean;
}

export function DynamicForm({ formData, onFormCancel, isLoading = false }: DynamicFormProps) {
  const router = useRouter();
  const [formValues, setFormValues] = useState<Record<string, unknown>>({});
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    // Initialize form with prefilled data
    const initialValues = { ...formData.prefilled_data };
    setFormValues(initialValues);
  }, [formData]);

  const validateField = (fieldName: string, value: unknown): string[] => {
    const field = formData.fields[fieldName];
    const fieldErrors: string[] = [];

    if (!field) return fieldErrors;

    // Required validation
    if (field.required && (!value || value.toString().trim() === '')) {
      fieldErrors.push(`${field.label} is required`);
    }

    if (value && value.toString().trim() !== '') {
      // Type-specific validation
      if (field.type === 'text' || field.type === 'textarea') {
        const strValue = value.toString();
        if (field.validation?.min_length && strValue.length < field.validation.min_length) {
          fieldErrors.push(`${field.label} must be at least ${field.validation.min_length} characters`);
        }
        if (field.validation?.max_length && strValue.length > field.validation.max_length) {
          fieldErrors.push(`${field.label} must be at most ${field.validation.max_length} characters`);
        }
      } else if (field.type === 'number') {
        const numValue = parseFloat(String(value));
        if (isNaN(numValue)) {
          fieldErrors.push(`${field.label} must be a valid number`);
        } else {
          if (field.validation?.min !== undefined && numValue < (field.validation.min as number)) {
            fieldErrors.push(`${field.label} must be at least ${field.validation.min}`);
          }
          if (field.validation?.max !== undefined && numValue > (field.validation.max as number)) {
            fieldErrors.push(`${field.label} must be at most ${field.validation.max}`);
          }
        }
      } else if (field.type === 'date') {
        const dateValue = new Date(String(value));
        if (isNaN(dateValue.getTime())) {
          fieldErrors.push(`${field.label} must be a valid date`);
        }
              } else if (field.type === 'select') {
          if (field.options && !field.options.includes(String(value))) {
            fieldErrors.push(`${field.label} must be one of: ${field.options.join(', ')}`);
          }
        }
    }

    return fieldErrors;
  };

  const handleFieldChange = (fieldName: string, value: unknown) => {
    const newValues = { ...formValues, [fieldName]: value };
    setFormValues(newValues);

    // Validate field
    const fieldErrors = validateField(fieldName, value);
    setErrors(prev => ({
      ...prev,
      [fieldName]: fieldErrors
    }));
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string[]> = {};
    let isValid = true;

    formData.field_order.forEach(fieldName => {
      const fieldErrors = validateField(fieldName, formValues[fieldName]);
      if (fieldErrors.length > 0) {
        newErrors[fieldName] = fieldErrors;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      // Redirect to document creation page with form data
      const formDataParam = encodeURIComponent(JSON.stringify(formData));
      router.push(`/document-creation?formData=${formDataParam}`);
    }
  };

  const renderField = (fieldName: string) => {
    const field = formData.fields[fieldName];
    if (!field) return null;

    const value = (formValues[fieldName] as string) || '';
    const fieldErrors = errors[fieldName] || [];

    return (
      <div key={fieldName} className="space-y-2">
        <label htmlFor={fieldName} className="flex items-center gap-2 text-sm font-medium text-gray-700">
          {field.label}
          {field.required && <span className="text-red-500">*</span>}
        </label>

        {field.type === 'text' && (
          <input
            id={fieldName}
            type="text"
            value={value}
            onChange={(e) => handleFieldChange(fieldName, e.target.value)}
            disabled={!isEditing || isLoading}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              fieldErrors.length > 0 ? 'border-red-500' : 'border-gray-300'
            } ${!isEditing || isLoading ? 'bg-gray-100' : 'bg-white'}`}
            placeholder={`Enter ${field.label.toLowerCase()}`}
          />
        )}

        {field.type === 'textarea' && (
          <textarea
            id={fieldName}
            value={value}
            onChange={(e) => handleFieldChange(fieldName, e.target.value)}
            disabled={!isEditing || isLoading}
            rows={3}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              fieldErrors.length > 0 ? 'border-red-500' : 'border-gray-300'
            } ${!isEditing || isLoading ? 'bg-gray-100' : 'bg-white'}`}
            placeholder={`Enter ${field.label.toLowerCase()}`}
          />
        )}

        {field.type === 'number' && (
          <input
            id={fieldName}
            type="number"
            value={value}
            onChange={(e) => handleFieldChange(fieldName, e.target.value)}
            disabled={!isEditing || isLoading}
            min={field.validation?.min}
            max={field.validation?.max}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              fieldErrors.length > 0 ? 'border-red-500' : 'border-gray-300'
            } ${!isEditing || isLoading ? 'bg-gray-100' : 'bg-white'}`}
            placeholder={`Enter ${field.label.toLowerCase()}`}
          />
        )}

        {field.type === 'date' && (
          <input
            id={fieldName}
            type="date"
            value={value}
            onChange={(e) => handleFieldChange(fieldName, e.target.value)}
            disabled={!isEditing || isLoading}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              fieldErrors.length > 0 ? 'border-red-500' : 'border-gray-300'
            } ${!isEditing || isLoading ? 'bg-gray-100' : 'bg-white'}`}
          />
        )}

        {field.type === 'select' && (
          <select
            id={fieldName}
            value={value}
            onChange={(e) => handleFieldChange(fieldName, e.target.value)}
            disabled={!isEditing || isLoading}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              fieldErrors.length > 0 ? 'border-red-500' : 'border-gray-300'
            } ${!isEditing || isLoading ? 'bg-gray-100' : 'bg-white'}`}
          >
            <option value="">Select {field.label.toLowerCase()}</option>
            {field.options?.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        )}

        {fieldErrors.length > 0 && (
          <div className="text-sm text-red-500 space-y-1">
            {fieldErrors.map((error, index) => (
              <div key={index} className="flex items-center gap-1">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                {error}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const hasErrors = Object.values(errors).some(errorArray => errorArray.length > 0);

  return (
    <div className="w-full max-w-2xl mx-auto bg-white rounded-lg shadow-md border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900">{formData.name}</h3>
          </div>
          <div className="flex items-center gap-2">
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                disabled={isLoading}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Edit
              </button>
            ) : (
              <button
                onClick={() => setIsEditing(false)}
                disabled={isLoading}
                className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
        {formData.description && (
          <p className="text-sm text-gray-600 mt-1">{formData.description}</p>
        )}
      </div>

      <div className="px-6 py-4 space-y-6">
        {formData.prefilled_data && Object.keys(formData.prefilled_data).length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <p className="text-sm text-blue-800">
                I&apos;ve pre-filled some fields based on our conversation. Please review and complete the remaining information.
              </p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {formData.field_order.map(renderField)}
        </div>

        <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
          <button
            onClick={onFormCancel}
            disabled={isLoading}
            className="px-4 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!isEditing || isLoading || hasErrors}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed min-w-[100px]"
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Creating...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                </svg>
                Continue to Document Creation
              </div>
            )}
          </button>
        </div>

        {hasErrors && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <p className="text-sm text-red-800">
                Please fix the errors above before creating the document.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}