/**
 * Next.js Math Solver Component (Client Component)
 * Location: app/components/MathSolver.tsx
 *
 * Usage:
 * import MathSolver from '@/components/MathSolver';
 *
 * export default function Page() {
 *   return <MathSolver />;
 * }
 */

'use client';

import { useState, FormEvent } from 'react';
import type {
  MathSolveRequest,
  MathSolveResponse,
  MathFormat,
  StudentLevel,
} from '@/types/stem-api';

export default function MathSolver() {
  // Form state
  const [query, setQuery] = useState('');
  const [format, setFormat] = useState<MathFormat>('latex');
  const [studentLevel, setStudentLevel] = useState<StudentLevel>('undergraduate');
  const [showSteps, setShowSteps] = useState(true);
  const [includeEducational, setIncludeEducational] = useState(true);

  // Response state
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MathSolveResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const requestBody: MathSolveRequest = {
        query,
        format,
        student_level: studentLevel,
        show_steps: showSteps,
        include_educational: includeEducational,
      };

      const response = await fetch('/api/math/solve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: MathSolveResponse = await response.json();
      setResult(data);

      if (!data.success) {
        setError(data.error || 'Failed to solve problem');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Error solving problem:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setQuery('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Math Problem Solver
        </h1>
        <p className="text-gray-600">
          Powered by Wolfram Alpha & GPT-5
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Query Input */}
        <div>
          <label
            htmlFor="query"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Math Problem
          </label>
          <input
            id="query"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., What is the derivative of x^3 + 2x^2?"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
            disabled={loading}
          />
        </div>

        {/* Settings Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Format Selection */}
          <div>
            <label
              htmlFor="format"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Output Format
            </label>
            <select
              id="format"
              value={format}
              onChange={(e) => setFormat(e.target.value as MathFormat)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            >
              <option value="plaintext">Plain Text</option>
              <option value="latex">LaTeX</option>
              <option value="mathml">MathML</option>
              <option value="image">Image</option>
            </select>
          </div>

          {/* Student Level */}
          <div>
            <label
              htmlFor="studentLevel"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Student Level
            </label>
            <select
              id="studentLevel"
              value={studentLevel}
              onChange={(e) => setStudentLevel(e.target.value as StudentLevel)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            >
              <option value="high_school">High School</option>
              <option value="undergraduate">Undergraduate</option>
              <option value="graduate">Graduate</option>
            </select>
          </div>

          {/* Options */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Options
            </label>
            <div className="space-y-1">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={showSteps}
                  onChange={(e) => setShowSteps(e.target.checked)}
                  className="mr-2 rounded"
                  disabled={loading}
                />
                <span className="text-sm text-gray-700">Show steps</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeEducational}
                  onChange={(e) => setIncludeEducational(e.target.checked)}
                  className="mr-2 rounded"
                  disabled={loading}
                />
                <span className="text-sm text-gray-700">Educational content</span>
              </label>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Solving...
              </span>
            ) : (
              'Solve Problem'
            )}
          </button>

          {result && (
            <button
              type="button"
              onClick={handleReset}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 focus:ring-4 focus:ring-gray-200 transition-colors"
            >
              Reset
            </button>
          )}
        </div>
      </form>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results Display */}
      {result && result.success && (
        <div className="space-y-6 p-6 bg-gray-50 border border-gray-200 rounded-lg">
          <h2 className="text-2xl font-semibold text-gray-900">Solution</h2>

          {/* Final Answer */}
          {result.result.final_answer && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-3">Answer</h3>
              <div className="p-4 bg-white border border-gray-200 rounded-lg">
                <code className="text-lg text-blue-600 font-mono">
                  {result.result.final_answer}
                </code>
              </div>
            </div>
          )}

          {/* Explanation */}
          {result.explanation && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-3">Explanation</h3>
              <div className="p-4 bg-white border border-gray-200 rounded-lg">
                <p className="text-gray-700 leading-relaxed">{result.explanation}</p>
              </div>
            </div>
          )}

          {/* Steps */}
          {result.steps && result.steps.length > 0 && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-3">
                Step-by-Step Solution
              </h3>
              <div className="space-y-3">
                {result.steps.map((step, index) => (
                  <div
                    key={index}
                    className="p-4 bg-white border border-gray-200 rounded-lg"
                  >
                    <div className="flex items-start">
                      <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold text-sm">
                        {step.step_number}
                      </div>
                      <div className="ml-4 flex-1">
                        <p className="text-gray-700 mb-2">{step.description}</p>
                        <code className="block p-3 bg-gray-50 rounded border border-gray-200 text-sm font-mono">
                          {step.math}
                        </code>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Visualizations */}
          {result.visualizations && result.visualizations.length > 0 && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-3">
                Visualizations
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {result.visualizations.map((viz, index) => (
                  <div
                    key={index}
                    className="p-4 bg-white border border-gray-200 rounded-lg"
                  >
                    <h4 className="font-medium text-gray-900 mb-2">{viz.title}</h4>
                    {viz.image && viz.image.src && (
                      <img
                        src={viz.image.src}
                        alt={viz.image.alt || viz.title}
                        className="w-full rounded"
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Educational Content */}
          {result.educational_content && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-3">
                Learn More
              </h3>
              <div className="p-4 bg-white border border-gray-200 rounded-lg space-y-4">
                {result.educational_content.key_concepts && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Key Concepts</h4>
                    <ul className="list-disc list-inside space-y-1">
                      {result.educational_content.key_concepts.map((concept, index) => (
                        <li key={index} className="text-gray-700">{concept}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.educational_content.practice_problems && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Practice Problems</h4>
                    <ul className="list-decimal list-inside space-y-1">
                      {result.educational_content.practice_problems.map((problem, index) => (
                        <li key={index} className="text-gray-700">{problem}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
