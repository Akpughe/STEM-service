# STEM Service API Documentation

## Table of Contents
- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [TypeScript Types](#typescript-types)
- [Next.js Integration](#nextjs-integration)
- [React Integration](#react-integration)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Code Examples](#code-examples)

---

## Overview

The STEM Service API provides advanced mathematical problem-solving capabilities using Wolfram Alpha and GPT-5. It supports various mathematical operations including calculus, algebra, linear algebra, trigonometry, and more.

### Key Features
- 🧮 Solve complex math problems with step-by-step solutions
- 📊 Multiple output formats (plaintext, LaTeX, MathML, image)
- 📚 Educational content and explanations
- 🖼️ Image-based problem solving (upload math images)
- 📈 Visualizations and plots
- 🎓 Student-level customization

---

## Base URL

```
http://localhost:8000
```

For production, replace with your deployed API URL.

---

## Authentication

Currently, the API does not require authentication. For production use, implement your preferred authentication method (API keys, JWT, OAuth, etc.).

---

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "STEM Service",
  "timestamp": "2025-11-04T20:00:00Z"
}
```

### 2. Solve Math Problem

**POST** `/api/v1/math/solve`

Solve a mathematical problem with detailed explanations.

**Request Body:**
```json
{
  "query": "string (required)",
  "show_steps": "boolean (optional, default: true)",
  "student_level": "string (optional, default: 'undergraduate')",
  "include_educational": "boolean (optional, default: true)",
  "format": "string (optional, default: 'plaintext')"
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | The mathematical problem to solve |
| `show_steps` | boolean | No | `true` | Include step-by-step solution |
| `student_level` | string | No | `"undergraduate"` | Education level: `"high_school"`, `"undergraduate"`, `"graduate"` |
| `include_educational` | boolean | No | `true` | Include educational content and practice problems |
| `format` | string | No | `"plaintext"` | Output format: `"plaintext"`, `"latex"`, `"mathml"`, `"image"` |

**Response:**
```json
{
  "success": true,
  "query": "What is the derivative of x^3 + 2x^2 + 5?",
  "result": {
    "original_query": "derivative of x^3 + 2x^2 + 5",
    "final_answer": "3x^2 + 4x",
    "success": true
  },
  "explanation": "The derivative represents the rate of change...",
  "steps": [
    {
      "step_number": 1,
      "description": "Apply the power rule to x^3",
      "math": "d/dx(x^3) = 3x^2"
    }
  ],
  "educational_content": {
    "key_concepts": ["Power Rule", "Derivatives"],
    "practice_problems": ["Find derivative of x^4"]
  },
  "visualizations": [],
  "error": null
}
```

### 3. Solve from Image

**POST** `/api/v1/math/solve-image`

Solve a mathematical problem from an uploaded image.

**Request:** `multipart/form-data`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `file` | File | Yes | - | Image file (JPG, PNG, etc.) |
| `show_steps` | boolean | No | `true` | Include step-by-step solution |
| `student_level` | string | No | `"undergraduate"` | Education level |
| `include_educational` | boolean | No | `true` | Include educational content |
| `format` | string | No | `"plaintext"` | Output format |

**Response:** Same as `/solve` endpoint

### 4. Create Plot

**POST** `/api/v1/math/plot`

Create a mathematical plot or graph.

**Request:** `multipart/form-data`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `expression` | string | Yes | - | Mathematical expression to plot |
| `variable` | string | No | `"x"` | Variable name |
| `range_min` | number | No | `-10` | Minimum range value |
| `range_max` | number | No | `10` | Maximum range value |
| `plot_type` | string | No | `"Plot"` | Type of plot |

**Response:**
```json
{
  "success": true,
  "expression": "x^2",
  "plot": "https://www.wolframalpha.com/...",
  "error": null
}
```

---

## TypeScript Types

### Request Types

```typescript
// Math solve request
interface MathSolveRequest {
  query: string;
  show_steps?: boolean;
  student_level?: 'high_school' | 'undergraduate' | 'graduate';
  include_educational?: boolean;
  format?: 'plaintext' | 'latex' | 'mathml' | 'image';
}

// Image solve request (FormData)
interface ImageSolveFormData {
  file: File;
  show_steps?: boolean;
  student_level?: string;
  include_educational?: boolean;
  format?: string;
}

// Plot request
interface PlotRequest {
  expression: string;
  variable?: string;
  range_min?: number;
  range_max?: number;
  plot_type?: string;
}
```

### Response Types

```typescript
// Step in solution
interface SolutionStep {
  step_number: number;
  description: string;
  math: string;
}

// Visualization
interface Visualization {
  title: string;
  image: {
    src: string;
    alt?: string;
    width?: string;
    height?: string;
  };
}

// Educational content
interface EducationalContent {
  key_concepts?: string[];
  practice_problems?: string[];
  flashcards?: Array<{
    question: string;
    answer: string;
  }>;
}

// Main math response
interface MathSolveResponse {
  success: boolean;
  query: string;
  result: {
    original_query: string;
    final_answer: string | null;
    success: boolean;
    steps?: SolutionStep[];
    visualizations?: Visualization[];
  };
  explanation?: string | null;
  steps?: SolutionStep[] | null;
  educational_content?: EducationalContent | null;
  visualizations?: Visualization[] | null;
  error?: string | null;
}

// Plot response
interface PlotResponse {
  success: boolean;
  expression: string;
  plot: string | null;
  error: string | null;
}

// Health check response
interface HealthResponse {
  status: string;
  service: string;
  timestamp: string;
}
```

---

## Next.js Integration

### App Router (Next.js 13+)

#### API Route Handler

Create `app/api/math/solve/route.ts`:

```typescript
import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.STEM_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const response = await fetch(`${API_BASE_URL}/api/v1/math/solve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to solve problem' },
      { status: 500 }
    );
  }
}
```

#### Client Component

Create `app/components/MathSolver.tsx`:

```typescript
'use client';

import { useState } from 'react';

interface MathSolveRequest {
  query: string;
  show_steps?: boolean;
  student_level?: 'high_school' | 'undergraduate' | 'graduate';
  include_educational?: boolean;
  format?: 'plaintext' | 'latex' | 'mathml' | 'image';
}

interface SolutionStep {
  step_number: number;
  description: string;
  math: string;
}

interface MathSolveResponse {
  success: boolean;
  query: string;
  result: {
    final_answer: string | null;
  };
  steps?: SolutionStep[] | null;
  error?: string | null;
}

export default function MathSolver() {
  const [query, setQuery] = useState('');
  const [format, setFormat] = useState<'plaintext' | 'latex' | 'mathml' | 'image'>('latex');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MathSolveResponse | null>(null);

  const solveProblem = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('/api/math/solve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          show_steps: true,
          include_educational: true,
          format,
        } as MathSolveRequest),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error solving problem:', error);
      setResult({
        success: false,
        query,
        result: { final_answer: null },
        error: 'Failed to solve problem',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Math Problem Solver</h1>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">
          Enter your math problem:
        </label>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., What is the derivative of x^3 + 2x^2?"
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">
          Output Format:
        </label>
        <select
          value={format}
          onChange={(e) => setFormat(e.target.value as any)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="plaintext">Plain Text</option>
          <option value="latex">LaTeX</option>
          <option value="mathml">MathML</option>
          <option value="image">Image</option>
        </select>
      </div>

      <button
        onClick={solveProblem}
        disabled={loading || !query}
        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
      >
        {loading ? 'Solving...' : 'Solve Problem'}
      </button>

      {result && (
        <div className="mt-6 p-6 border rounded-lg bg-gray-50">
          {result.success ? (
            <>
              <h2 className="text-xl font-semibold mb-4">Solution</h2>

              {result.result.final_answer && (
                <div className="mb-4">
                  <h3 className="font-medium mb-2">Answer:</h3>
                  <div className="p-4 bg-white rounded border">
                    <code>{result.result.final_answer}</code>
                  </div>
                </div>
              )}

              {result.steps && result.steps.length > 0 && (
                <div className="mb-4">
                  <h3 className="font-medium mb-2">Steps:</h3>
                  <div className="space-y-3">
                    {result.steps.map((step) => (
                      <div key={step.step_number} className="p-4 bg-white rounded border">
                        <div className="font-medium text-sm text-gray-600 mb-1">
                          Step {step.step_number}
                        </div>
                        <div className="mb-2">{step.description}</div>
                        <code className="text-sm bg-gray-100 p-2 rounded block">
                          {step.math}
                        </code>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-red-600">
              <h3 className="font-semibold mb-2">Error</h3>
              <p>{result.error || 'Failed to solve problem'}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

#### Usage in Page

```typescript
// app/page.tsx
import MathSolver from './components/MathSolver';

export default function Home() {
  return (
    <main>
      <MathSolver />
    </main>
  );
}
```

### Pages Router (Next.js 12 and below)

#### API Route

Create `pages/api/math/solve.ts`:

```typescript
import type { NextApiRequest, NextApiResponse } from 'next';

const API_BASE_URL = process.env.STEM_API_URL || 'http://localhost:8000';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/math/solve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
    });

    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to solve problem' });
  }
}
```

#### Component

```typescript
// components/MathSolver.tsx
import { useState } from 'react';

// ... (same component code as App Router example)
```

---

## React Integration

### Custom Hook

Create `hooks/useMathSolver.ts`:

```typescript
import { useState, useCallback } from 'react';

interface MathSolveRequest {
  query: string;
  show_steps?: boolean;
  student_level?: 'high_school' | 'undergraduate' | 'graduate';
  include_educational?: boolean;
  format?: 'plaintext' | 'latex' | 'mathml' | 'image';
}

interface MathSolveResponse {
  success: boolean;
  query: string;
  result: any;
  steps?: any[];
  error?: string;
}

const API_BASE_URL = process.env.REACT_APP_STEM_API_URL || 'http://localhost:8000';

export function useMathSolver() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MathSolveResponse | null>(null);

  const solve = useCallback(async (request: MathSolveRequest) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/math/solve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return {
    solve,
    reset,
    loading,
    error,
    result,
  };
}
```

### React Component Example

```typescript
// components/MathSolver.tsx
import React, { useState } from 'react';
import { useMathSolver } from '../hooks/useMathSolver';

export default function MathSolver() {
  const [query, setQuery] = useState('');
  const [format, setFormat] = useState<'plaintext' | 'latex'>('latex');
  const { solve, loading, error, result } = useMathSolver();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await solve({
        query,
        show_steps: true,
        include_educational: true,
        format,
      });
    } catch (err) {
      console.error('Failed to solve:', err);
    }
  };

  return (
    <div className="math-solver">
      <h1>Math Problem Solver</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Math Problem:</label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your math problem"
            required
          />
        </div>

        <div>
          <label>Format:</label>
          <select value={format} onChange={(e) => setFormat(e.target.value as any)}>
            <option value="plaintext">Plain Text</option>
            <option value="latex">LaTeX</option>
          </select>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Solving...' : 'Solve'}
        </button>
      </form>

      {error && (
        <div className="error">
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      )}

      {result && result.success && (
        <div className="result">
          <h2>Solution</h2>

          {result.result.final_answer && (
            <div>
              <h3>Answer:</h3>
              <code>{result.result.final_answer}</code>
            </div>
          )}

          {result.steps && result.steps.length > 0 && (
            <div>
              <h3>Steps:</h3>
              {result.steps.map((step, index) => (
                <div key={index} className="step">
                  <strong>Step {step.step_number}:</strong>
                  <p>{step.description}</p>
                  <code>{step.math}</code>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

### Image Upload Component

```typescript
// components/ImageSolver.tsx
import React, { useState } from 'react';

const API_BASE_URL = process.env.REACT_APP_STEM_API_URL || 'http://localhost:8000';

export default function ImageSolver() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('show_steps', 'true');
    formData.append('format', 'latex');

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/math/solve-image`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Solve from Image</h2>

      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          required
        />

        <button type="submit" disabled={loading || !file}>
          {loading ? 'Processing...' : 'Solve'}
        </button>
      </form>

      {result && (
        <div>
          {result.success ? (
            <>
              <h3>Result:</h3>
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </>
          ) : (
            <p>Error: {result.error}</p>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## Error Handling

### Common Errors

```typescript
interface ErrorResponse {
  success: false;
  error: string;
}

// Example error handling
async function solveMath(query: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/math/solve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      if (response.status === 400) {
        throw new Error('Invalid request');
      } else if (response.status === 500) {
        throw new Error('Server error');
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || 'Failed to solve problem');
    }

    return data;
  } catch (error) {
    console.error('Error solving math problem:', error);
    throw error;
  }
}
```

### Error Types

| Status Code | Description |
|------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Invalid endpoint |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Best Practices

### 1. Environment Variables

Create `.env.local`:

```bash
# Next.js
STEM_API_URL=http://localhost:8000

# React
REACT_APP_STEM_API_URL=http://localhost:8000
```

### 2. Request Timeout

```typescript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

try {
  const response = await fetch(`${API_BASE_URL}/api/v1/math/solve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
    signal: controller.signal,
  });

  clearTimeout(timeoutId);
  return await response.json();
} catch (error) {
  if (error.name === 'AbortError') {
    console.error('Request timeout');
  }
  throw error;
}
```

### 3. Debouncing Input

```typescript
import { useState, useEffect } from 'react';
import { debounce } from 'lodash';

function MathInput() {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    const debouncedFetch = debounce(async (value: string) => {
      if (value.length > 3) {
        // Fetch suggestions or validate
      }
    }, 300);

    debouncedFetch(query);
  }, [query]);

  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Enter math problem"
    />
  );
}
```

### 4. Caching Results

```typescript
const cache = new Map<string, any>();

async function solveMath(query: string) {
  // Check cache
  const cacheKey = `${query}-latex`;
  if (cache.has(cacheKey)) {
    return cache.get(cacheKey);
  }

  // Fetch from API
  const result = await fetch(/* ... */);

  // Store in cache
  cache.set(cacheKey, result);

  return result;
}
```

### 5. Loading States

```typescript
function MathSolver() {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  return (
    <div>
      {status === 'loading' && <LoadingSpinner />}
      {status === 'error' && <ErrorMessage />}
      {status === 'success' && <Result />}
    </div>
  );
}
```

---

## Code Examples

### Example 1: Simple Derivative

```typescript
const request = {
  query: "What is the derivative of x^3 + 2x^2 + 5?",
  format: "latex",
  show_steps: true
};

const response = await fetch('http://localhost:8000/api/v1/math/solve', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(request)
});

const result = await response.json();
console.log(result.result.final_answer); // "3x^2 + 4x"
```

### Example 2: Integration with Steps

```typescript
const request = {
  query: "Integrate x^2 * sin(x) dx",
  format: "latex",
  show_steps: true,
  include_educational: true
};

// Result will include:
// - Final answer
// - Step-by-step solution
// - Educational content (key concepts, practice problems)
```

### Example 3: System of Equations

```typescript
const request = {
  query: "Solve the system: 2x + y = 5, x - y = 1",
  format: "latex",
  show_steps: true,
  student_level: "undergraduate"
};
```

### Example 4: Batch Processing

```typescript
async function solveBatch(queries: string[]) {
  const results = await Promise.all(
    queries.map(query =>
      fetch('http://localhost:8000/api/v1/math/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, format: 'latex' })
      }).then(res => res.json())
    )
  );

  return results;
}

const problems = [
  "derivative of x^2",
  "integral of sin(x)",
  "solve x^2 - 4 = 0"
];

const solutions = await solveBatch(problems);
```

---

## Additional Resources

- [API Health Check](http://localhost:8000/health)
- [Interactive API Docs](http://localhost:8000/docs)
- [Alternative API Docs](http://localhost:8000/redoc)

---

## Support

For issues or questions:
- Check the [TESTING_GUIDE.md](./TESTING_GUIDE.md) for troubleshooting
- Review the [TEST_README.md](./TEST_README.md) for examples
- Open an issue on GitHub

---

**Last Updated:** 2025-11-04
**API Version:** 1.0.0
