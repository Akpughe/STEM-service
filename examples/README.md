# STEM API Integration Examples

This directory contains ready-to-use code examples for integrating the STEM Service API into your Next.js or React applications.

## 📁 Directory Structure

```
examples/
├── types.ts                              # TypeScript type definitions
├── nextjs/
│   ├── api-route-app-router.ts          # Next.js 13+ App Router API route
│   └── MathSolverComponent.tsx          # Full-featured client component
└── react/
    ├── useMathSolver.ts                 # React hook for API integration
    └── SimpleMathSolver.tsx             # Simple component example
```

## 🚀 Quick Start

### 1. Copy Type Definitions

Copy `types.ts` to your project:

```bash
# For Next.js
cp examples/types.ts your-nextjs-app/types/stem-api.ts

# For React
cp examples/types.ts your-react-app/src/types/stem-api.ts
```

### 2. Set Environment Variables

Create `.env.local` (Next.js) or `.env` (React):

```bash
# Next.js
STEM_API_URL=http://localhost:8000

# React
REACT_APP_STEM_API_URL=http://localhost:8000
```

### 3. Choose Your Integration Method

Pick the example that fits your needs:

- **Next.js App Router** → Use `nextjs/api-route-app-router.ts` + `nextjs/MathSolverComponent.tsx`
- **React with Hooks** → Use `react/useMathSolver.ts` + `react/SimpleMathSolver.tsx`

## 📦 Next.js Integration

### App Router (Next.js 13+)

#### Step 1: Create API Route

```bash
mkdir -p app/api/math/solve
cp examples/nextjs/api-route-app-router.ts app/api/math/solve/route.ts
```

#### Step 2: Add Component

```bash
mkdir -p app/components
cp examples/nextjs/MathSolverComponent.tsx app/components/MathSolver.tsx
```

#### Step 3: Use in Page

```typescript
// app/page.tsx
import MathSolver from './components/MathSolver';

export default function Home() {
  return (
    <main className="container mx-auto py-8">
      <MathSolver />
    </main>
  );
}
```

### Pages Router (Next.js 12 and below)

Create `pages/api/math/solve.ts`:

```typescript
import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.STEM_API_URL || 'http://localhost:8000';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const response = await fetch(`${API_URL}/api/v1/math/solve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req.body),
  });

  const data = await response.json();
  res.status(200).json(data);
}
```

## ⚛️ React Integration

### Step 1: Copy Hook

```bash
mkdir -p src/hooks
cp examples/react/useMathSolver.ts src/hooks/useMathSolver.ts
```

### Step 2: Copy Component

```bash
mkdir -p src/components
cp examples/react/SimpleMathSolver.tsx src/components/MathSolver.tsx
```

### Step 3: Use in App

```typescript
// App.tsx
import MathSolver from './components/MathSolver';

function App() {
  return (
    <div className="App">
      <MathSolver />
    </div>
  );
}

export default App;
```

## 🎯 Usage Examples

### Basic Solve

```typescript
import { useMathSolver } from '@/hooks/useMathSolver';

function MyComponent() {
  const { solve, loading, result } = useMathSolver();

  const handleSolve = async () => {
    await solve({
      query: 'What is the derivative of x^3?',
      format: 'latex',
      show_steps: true,
    });
  };

  return (
    <div>
      <button onClick={handleSolve} disabled={loading}>
        {loading ? 'Solving...' : 'Solve'}
      </button>
      {result && <div>{result.result.final_answer}</div>}
    </div>
  );
}
```

### With TypeScript

```typescript
import type { MathSolveRequest, MathSolveResponse } from '@/types/stem-api';

const request: MathSolveRequest = {
  query: 'Integrate x^2 dx',
  format: 'latex',
  show_steps: true,
  student_level: 'undergraduate',
  include_educational: true,
};

const response: MathSolveResponse = await solve(request);
```

### Image Upload

```typescript
import { useImageSolver } from '@/hooks/useMathSolver';

function ImageSolver() {
  const { solveFromImage, loading, result } = useImageSolver();

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      await solveFromImage(file, { format: 'latex' });
    }
  };

  return (
    <div>
      <input type="file" accept="image/*" onChange={handleFileUpload} />
      {loading && <p>Processing image...</p>}
      {result && <div>{result.result.final_answer}</div>}
    </div>
  );
}
```

### Batch Solving

```typescript
import { useBatchSolver } from '@/hooks/useMathSolver';

function BatchSolver() {
  const { solveBatch, loading, results } = useBatchSolver();

  const handleBatch = async () => {
    const problems = [
      { query: 'derivative of x^2', format: 'latex' as const },
      { query: 'integral of sin(x)', format: 'latex' as const },
      { query: 'solve x^2 - 4 = 0', format: 'latex' as const },
    ];

    await solveBatch(problems);
  };

  return (
    <div>
      <button onClick={handleBatch} disabled={loading}>
        Solve All
      </button>
      {results.map((result, i) => (
        <div key={i}>{result.result.final_answer}</div>
      ))}
    </div>
  );
}
```

## 🔧 Customization

### Custom Hook Options

```typescript
const { solve } = useMathSolver({
  baseUrl: 'https://api.yourapp.com',
  timeout: 30000, // 30 seconds
  onSuccess: (result) => {
    console.log('Success:', result);
    // Track analytics, show notification, etc.
  },
  onError: (error) => {
    console.error('Error:', error);
    // Log to error service, show user message, etc.
  },
});
```

### Request Caching

```typescript
import { useMemo } from 'react';

function MathSolver() {
  const cache = useMemo(() => new Map(), []);

  const solveWithCache = async (query: string) => {
    if (cache.has(query)) {
      return cache.get(query);
    }

    const result = await solve({ query, format: 'latex' });
    cache.set(query, result);
    return result;
  };

  // ...
}
```

### Debounced Input

```typescript
import { useEffect, useState } from 'react';
import { debounce } from 'lodash';

function MathInput() {
  const [query, setQuery] = useState('');
  const { solve } = useMathSolver();

  useEffect(() => {
    const debouncedSolve = debounce(async (q: string) => {
      if (q.length > 3) {
        await solve({ query: q, format: 'latex' });
      }
    }, 500);

    debouncedSolve(query);
  }, [query]);

  return <input value={query} onChange={(e) => setQuery(e.target.value)} />;
}
```

## 🎨 Styling

### Tailwind CSS

The Next.js component example uses Tailwind CSS classes. Make sure Tailwind is installed:

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Custom CSS

For custom styling, replace className props with your CSS classes or styled-components.

### CSS Modules

```typescript
import styles from './MathSolver.module.css';

<div className={styles.container}>
  <input className={styles.input} />
</div>
```

## 📱 Mobile Support

All components are mobile-responsive. For better mobile experience:

```typescript
<div className="w-full max-w-4xl mx-auto px-4 md:px-6">
  {/* Mobile-first design */}
</div>
```

## 🧪 Testing

### Unit Tests

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { useMathSolver } from './useMathSolver';

test('solves math problem', async () => {
  const { result } = renderHook(() => useMathSolver());

  await waitFor(async () => {
    await result.current.solve({ query: 'x^2', format: 'latex' });
  });

  expect(result.current.result?.success).toBe(true);
});
```

### Integration Tests

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MathSolver from './MathSolver';

test('renders and solves problem', async () => {
  render(<MathSolver />);

  const input = screen.getByPlaceholderText(/enter your math problem/i);
  fireEvent.change(input, { target: { value: 'x^2 + 2x' } });

  const button = screen.getByText(/solve/i);
  fireEvent.click(button);

  await waitFor(() => {
    expect(screen.getByText(/solution/i)).toBeInTheDocument();
  });
});
```

## 🔒 Security

### API Key Authentication

If you add authentication to your API:

```typescript
const response = await fetch(`${API_URL}/api/v1/math/solve`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.STEM_API_KEY}`,
  },
  body: JSON.stringify(request),
});
```

### Rate Limiting

Implement client-side rate limiting:

```typescript
import { useRateLimit } from '@/hooks/useRateLimit';

const { canMakeRequest, recordRequest } = useRateLimit(10, 60000); // 10 requests per minute

const handleSolve = async () => {
  if (!canMakeRequest()) {
    alert('Too many requests. Please wait.');
    return;
  }

  recordRequest();
  await solve({ query, format: 'latex' });
};
```

## 🐛 Troubleshooting

### CORS Errors

If you see CORS errors, make sure your API allows requests from your frontend domain:

```python
# In your FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Timeout Errors

Increase timeout for complex problems:

```typescript
const { solve } = useMathSolver({ timeout: 120000 }); // 2 minutes
```

### Type Errors

Make sure TypeScript is configured correctly:

```json
{
  "compilerOptions": {
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
```

## 📚 Additional Resources

- [Main API Documentation](../API_DOCUMENTATION.md)
- [Testing Guide](../TESTING_GUIDE.md)
- [Test Examples](../TEST_README.md)

## 💡 Tips

1. **Always handle errors** - Network requests can fail
2. **Show loading states** - Improve UX while solving
3. **Cache results** - Avoid duplicate API calls
4. **Validate input** - Check query before sending
5. **Use TypeScript** - Catch errors at compile time
6. **Test thoroughly** - Write tests for critical paths

## 🤝 Contributing

Found a bug or want to improve the examples? Feel free to submit a PR!

## 📄 License

These examples are provided as-is for use with the STEM Service API.
