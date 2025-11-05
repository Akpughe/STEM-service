/**
 * Simple React Math Solver Component
 * Location: components/SimpleMathSolver.tsx
 *
 * A minimal example showing basic usage of the useMathSolver hook
 */

import React, { useState } from 'react';
import { useMathSolver } from '../hooks/useMathSolver';

export default function SimpleMathSolver() {
  const [query, setQuery] = useState('');
  const { solve, loading, result, error, reset } = useMathSolver({
    onSuccess: (data) => {
      console.log('Problem solved successfully:', data);
    },
    onError: (err) => {
      console.error('Failed to solve:', err);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await solve({
        query,
        format: 'latex',
        show_steps: true,
        include_educational: true,
      });
    } catch (err) {
      // Error is already handled by the hook
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h1>Math Problem Solver</h1>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '16px' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your math problem"
            style={{
              width: '100%',
              padding: '12px',
              fontSize: '16px',
              border: '1px solid #ccc',
              borderRadius: '4px',
            }}
            required
          />
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            style={{
              padding: '12px 24px',
              fontSize: '16px',
              backgroundColor: loading ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? 'Solving...' : 'Solve'}
          </button>

          {result && (
            <button
              type="button"
              onClick={reset}
              style={{
                padding: '12px 24px',
                fontSize: '16px',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Reset
            </button>
          )}
        </div>
      </form>

      {error && (
        <div
          style={{
            marginTop: '20px',
            padding: '16px',
            backgroundColor: '#f8d7da',
            border: '1px solid #f5c6cb',
            borderRadius: '4px',
            color: '#721c24',
          }}
        >
          <strong>Error:</strong> {error.message}
        </div>
      )}

      {result && result.success && (
        <div
          style={{
            marginTop: '20px',
            padding: '20px',
            backgroundColor: '#f8f9fa',
            border: '1px solid #dee2e6',
            borderRadius: '4px',
          }}
        >
          <h2>Solution</h2>

          {result.result.final_answer && (
            <div style={{ marginBottom: '20px' }}>
              <h3>Answer:</h3>
              <code
                style={{
                  display: 'block',
                  padding: '12px',
                  backgroundColor: 'white',
                  border: '1px solid #dee2e6',
                  borderRadius: '4px',
                  fontSize: '18px',
                  color: '#007bff',
                }}
              >
                {result.result.final_answer}
              </code>
            </div>
          )}

          {result.explanation && (
            <div style={{ marginBottom: '20px' }}>
              <h3>Explanation:</h3>
              <p style={{ lineHeight: '1.6' }}>{result.explanation}</p>
            </div>
          )}

          {result.steps && result.steps.length > 0 && (
            <div>
              <h3>Steps:</h3>
              {result.steps.map((step, index) => (
                <div
                  key={index}
                  style={{
                    marginBottom: '12px',
                    padding: '12px',
                    backgroundColor: 'white',
                    border: '1px solid #dee2e6',
                    borderRadius: '4px',
                  }}
                >
                  <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                    Step {step.step_number}:
                  </div>
                  <div style={{ marginBottom: '8px' }}>{step.description}</div>
                  <code
                    style={{
                      display: 'block',
                      padding: '8px',
                      backgroundColor: '#f8f9fa',
                      borderRadius: '4px',
                      fontSize: '14px',
                    }}
                  >
                    {step.math}
                  </code>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
