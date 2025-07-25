'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function ResearchPage() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleResearch = async () => {
    if (!query.trim()) return;
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch('http://localhost:8000/research/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query }),
      });
      const data = await response.json();
      setResult(data.answer || 'No answer returned.');
    } catch {
      setError('Error fetching research result.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleResearch();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Link href="/" className="text-2xl font-bold text-gray-900 hover:text-blue-600">
                Wakili Quick1
              </Link>
              <span className="ml-2 text-sm text-gray-500">Legal Research</span>
            </div>
            <nav className="flex space-x-8">
              <Link href="/upload" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                Document Upload
              </Link>
              <Link href="/chat" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                Legal Chat
              </Link>
              <Link href="/research" className="text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                Legal Research
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Research Form */}
      <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Legal Research</h2>
        <div className="bg-white rounded-lg shadow-md p-8">
          <label htmlFor="research-query" className="block text-gray-700 font-medium mb-2">
            Enter your legal research question:
          </label>
          <textarea
            id="research-query"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            rows={4}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="e.g. What are the legal requirements for forming a company in Kenya?"
            disabled={isLoading}
          />
          <button
            onClick={handleResearch}
            disabled={isLoading || !query.trim()}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Researching...' : 'Submit'}
          </button>

          {error && <div className="text-red-600 mt-4">{error}</div>}
          {result && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Result:</h3>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 whitespace-pre-line text-gray-800">
                {result}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}