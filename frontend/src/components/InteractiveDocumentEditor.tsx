'use client';

import React, { useState, useEffect } from 'react';
import {
  Edit3,
  Trash2,
  Plus,
  Save,
  Eye,
  EyeOff,
  ChevronUp,
  ChevronDown,
  FileText
} from 'lucide-react';

interface DocumentSection {
  id: string;
  type: 'heading' | 'paragraph' | 'list' | 'signature' | 'clause';
  content: string;
  level?: number;
  isEditable?: boolean;
  isHighlighted?: boolean;
}

interface InteractiveDocumentEditorProps {
  documentContent: string;
  onSave: (sections: DocumentSection[]) => void;
  onCancel: () => void;
  isEditing: boolean;
  onToggleEdit: () => void;
}

const InteractiveDocumentEditor: React.FC<InteractiveDocumentEditorProps> = ({
  documentContent,
  onSave,
  isEditing,
  onToggleEdit
}) => {
  const [sections, setSections] = useState<DocumentSection[]>([]);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [dragSource, setDragSource] = useState<string | null>(null);
  const [showPreview, setShowPreview] = useState(true);
  const [editMode, setEditMode] = useState<'view' | 'edit' | 'highlight'>('view');

  // Parse document content into sections
  useEffect(() => {
    if (documentContent) {
      const parsedSections = parseDocumentIntoSections(documentContent);
      setSections(parsedSections);
    }
  }, [documentContent]);

  const parseDocumentIntoSections = (content: string): DocumentSection[] => {
    const lines = content.split('\n').filter(line => line.trim());
    const sections: DocumentSection[] = [];
    let currentSection: DocumentSection | null = null;

    lines.forEach((line, index) => {
      const trimmedLine = line.trim();

      // Detect headings (all caps, numbered, or bold patterns)
      if (trimmedLine.match(/^[A-Z\s]+$/) ||
          trimmedLine.match(/^\d+\.\s/) ||
          trimmedLine.match(/^\*\*.*\*\*$/) ||
          trimmedLine.includes('AGREEMENT') ||
          trimmedLine.includes('CONTRACT') ||
          trimmedLine.includes('WHEREAS') ||
          trimmedLine.includes('NOW, THEREFORE')) {

        if (currentSection) {
          sections.push(currentSection);
        }

        currentSection = {
          id: `section-${index}`,
          type: 'heading',
          content: trimmedLine,
          level: trimmedLine.match(/^\d+\.\s/) ? 2 : 1,
          isEditable: true,
          isHighlighted: false
        };
      }
      // Detect signature sections
      else if (trimmedLine.includes('Signature') ||
               trimmedLine.includes('WITNESS') ||
               trimmedLine.includes('Date') ||
               trimmedLine.match(/^_+$/)) {

        if (currentSection) {
          sections.push(currentSection);
        }

        currentSection = {
          id: `section-${index}`,
          type: 'signature',
          content: trimmedLine,
          isEditable: true,
          isHighlighted: false
        };
      }
      // Detect list items
      else if (trimmedLine.match(/^[•\-\*]\s/) || trimmedLine.match(/^\d+\.\s/)) {
        if (currentSection && currentSection.type === 'list') {
          currentSection.content += '\n' + trimmedLine;
        } else {
          if (currentSection) {
            sections.push(currentSection);
          }
          currentSection = {
            id: `section-${index}`,
            type: 'list',
            content: trimmedLine,
            isEditable: true,
            isHighlighted: false
          };
        }
      }
      // Regular paragraphs
      else {
        if (currentSection && currentSection.type === 'paragraph') {
          currentSection.content += '\n' + trimmedLine;
        } else {
          if (currentSection) {
            sections.push(currentSection);
          }
          currentSection = {
            id: `section-${index}`,
            type: 'paragraph',
            content: trimmedLine,
            isEditable: true,
            isHighlighted: false
          };
        }
      }
    });

    if (currentSection) {
      sections.push(currentSection);
    }

    return sections;
  };

  const handleSectionEdit = (id: string, newContent: string) => {
    setSections(prev => prev.map(section =>
      section.id === id ? { ...section, content: newContent } : section
    ));
  };

  const handleSectionDelete = (id: string) => {
    setSections(prev => prev.filter(section => section.id !== id));
  };

  const handleSectionMove = (id: string, direction: 'up' | 'down') => {
    setSections(prev => {
      const index = prev.findIndex(section => section.id === id);
      if (index === -1) return prev;

      const newSections = [...prev];
      if (direction === 'up' && index > 0) {
        [newSections[index], newSections[index - 1]] = [newSections[index - 1], newSections[index]];
      } else if (direction === 'down' && index < newSections.length - 1) {
        [newSections[index], newSections[index + 1]] = [newSections[index + 1], newSections[index]];
      }
      return newSections;
    });
  };

  const handleSectionAdd = (afterId?: string) => {
    const newSection: DocumentSection = {
      id: `section-${Date.now()}`,
      type: 'paragraph',
      content: 'New paragraph content...',
      isEditable: true,
      isHighlighted: false
    };

    if (afterId) {
      setSections(prev => {
        const index = prev.findIndex(section => section.id === afterId);
        const newSections = [...prev];
        newSections.splice(index + 1, 0, newSection);
        return newSections;
      });
    } else {
      setSections(prev => [...prev, newSection]);
    }
  };

  const handleSectionHighlight = (id: string) => {
    setSections(prev => prev.map(section =>
      section.id === id ? { ...section, isHighlighted: !section.isHighlighted } : section
    ));
  };

  const handleDragStart = (e: React.DragEvent, id: string) => {
    setDragSource(id);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e: React.DragEvent, targetId: string) => {
    e.preventDefault();
    if (dragSource && dragSource !== targetId) {
      setSections(prev => {
        const sourceIndex = prev.findIndex(section => section.id === dragSource);
        const targetIndex = prev.findIndex(section => section.id === targetId);

        if (sourceIndex === -1 || targetIndex === -1) return prev;

        const newSections = [...prev];
        const [movedSection] = newSections.splice(sourceIndex, 1);
        newSections.splice(targetIndex, 0, movedSection);
        return newSections;
      });
    }
    setDragSource(null);
  };

  const renderSection = (section: DocumentSection) => {
    const isSelected = selectedSection === section.id;
    const isDragging = dragSource === section.id;

    return (
      <div
        key={section.id}
        className={`relative group border-l-4 transition-all duration-200 ${
          isSelected ? 'border-blue-500 bg-blue-50' :
          section.isHighlighted ? 'border-yellow-500 bg-yellow-50' :
          'border-transparent hover:border-gray-300'
        } ${isDragging ? 'opacity-50' : ''}`}
        draggable={isEditing}
        onDragStart={(e) => handleDragStart(e, section.id)}
        onDragOver={handleDragOver}
        onDrop={(e) => handleDrop(e, section.id)}
        onClick={() => setSelectedSection(section.id)}
      >
        <div className="p-4">
          {/* Section Header */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <span className={`text-xs px-2 py-1 rounded ${
                section.type === 'heading' ? 'bg-blue-100 text-blue-800' :
                section.type === 'signature' ? 'bg-green-100 text-green-800' :
                section.type === 'list' ? 'bg-purple-100 text-purple-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {section.type}
              </span>
              {section.level && (
                <span className="text-xs text-gray-500">Level {section.level}</span>
              )}
            </div>

            {isEditing && (
              <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => handleSectionHighlight(section.id)}
                  className={`p-1 rounded ${section.isHighlighted ? 'bg-yellow-200 text-yellow-800' : 'bg-gray-100 text-gray-600'}`}
                  title="Highlight section"
                >
                  <Eye className="w-3 h-3" />
                </button>
                <button
                  onClick={() => handleSectionMove(section.id, 'up')}
                  className="p-1 rounded bg-gray-100 text-gray-600 hover:bg-gray-200"
                  title="Move up"
                >
                  <ChevronUp className="w-3 h-3" />
                </button>
                <button
                  onClick={() => handleSectionMove(section.id, 'down')}
                  className="p-1 rounded bg-gray-100 text-gray-600 hover:bg-gray-200"
                  title="Move down"
                >
                  <ChevronDown className="w-3 h-3" />
                </button>
                <button
                  onClick={() => handleSectionAdd(section.id)}
                  className="p-1 rounded bg-green-100 text-green-600 hover:bg-green-200"
                  title="Add section after"
                >
                  <Plus className="w-3 h-3" />
                </button>
                <button
                  onClick={() => handleSectionDelete(section.id)}
                  className="p-1 rounded bg-red-100 text-red-600 hover:bg-red-200"
                  title="Delete section"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            )}
          </div>

          {/* Section Content */}
          <div className="relative">
            {isEditing ? (
              <textarea
                value={section.content}
                onChange={(e) => handleSectionEdit(section.id, e.target.value)}
                className={`w-full p-2 border rounded resize-none ${
                  isSelected ? 'border-blue-300 focus:border-blue-500' : 'border-gray-200'
                }`}
                rows={Math.max(2, section.content.split('\n').length)}
                placeholder={`Enter ${section.type} content...`}
              />
            ) : (
              <div className={`whitespace-pre-wrap ${
                section.type === 'heading' ? 'font-bold text-lg' :
                section.type === 'signature' ? 'font-mono text-sm' :
                'text-base'
              }`}>
                {section.content}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/* Editor Toolbar */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h3 className="text-lg font-semibold text-gray-900">Document Editor</h3>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setEditMode('view')}
                className={`px-3 py-1 rounded text-sm ${
                  editMode === 'view' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'
                }`}
              >
                <Eye className="w-4 h-4 inline mr-1" />
                View
              </button>
              <button
                onClick={() => setEditMode('edit')}
                className={`px-3 py-1 rounded text-sm ${
                  editMode === 'edit' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                }`}
              >
                <Edit3 className="w-4 h-4 inline mr-1" />
                Edit
              </button>
              <button
                onClick={() => setEditMode('highlight')}
                className={`px-3 py-1 rounded text-sm ${
                  editMode === 'highlight' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-600'
                }`}
              >
                <FileText className="w-4 h-4 inline mr-1" />
                Highlight
              </button>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowPreview(!showPreview)}
              className="px-3 py-1 rounded bg-gray-100 text-gray-600 hover:bg-gray-200"
            >
              {showPreview ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
            {isEditing && (
              <>
                <button
                  onClick={() => handleSectionAdd()}
                  className="px-3 py-1 rounded bg-green-100 text-green-600 hover:bg-green-200"
                >
                  <Plus className="w-4 h-4 inline mr-1" />
                  Add Section
                </button>
                <button
                  onClick={() => onSave(sections)}
                  className="px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700"
                >
                  <Save className="w-4 h-4 inline mr-1" />
                  Save Changes
                </button>
              </>
            )}
            <button
              onClick={onToggleEdit}
              className={`px-3 py-1 rounded ${
                isEditing ? 'bg-red-100 text-red-600 hover:bg-red-200' : 'bg-blue-100 text-blue-600 hover:bg-blue-200'
              }`}
            >
              {isEditing ? 'Cancel Edit' : 'Enable Edit'}
            </button>
          </div>
        </div>
      </div>

      {/* Document Content */}
      <div className="max-h-96 overflow-y-auto">
        {showPreview && (
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Document Preview</h4>
            <div className="text-sm text-gray-600 whitespace-pre-wrap max-h-32 overflow-y-auto">
              {sections.map(section => section.content).join('\n\n')}
            </div>
          </div>
        )}

        <div className="divide-y divide-gray-100">
          {sections.map(renderSection)}
        </div>

        {sections.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No document sections found. Add content to get started.</p>
          </div>
        )}
      </div>

      {/* Statistics */}
      <div className="border-t border-gray-200 p-4 bg-gray-50">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-4">
            <span>Total Sections: {sections.length}</span>
            <span>Highlighted: {sections.filter(s => s.isHighlighted).length}</span>
            <span>Characters: {sections.reduce((acc, s) => acc + s.content.length, 0)}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs">
              {editMode === 'view' ? 'View Mode' :
               editMode === 'edit' ? 'Edit Mode' : 'Highlight Mode'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InteractiveDocumentEditor;