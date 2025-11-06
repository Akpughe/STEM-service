/**
 * React Hook for STEM Math Solver
 * Location: hooks/useMathSolver.ts
 *
 * Usage:
 * import { useMathSolver } from '@/hooks/useMathSolver';
 *
 * function MyComponent() {
 *   const { solve, loading, result, error } = useMathSolver();
 *
 *   const handleSolve = async () => {
 *     await solve({ query: 'x^2 + 2x + 1', format: 'latex' });
 *   };
 *
 *   return ...;
 * }
 */

import { useState, useCallback, useRef } from 'react';
import type { MathSolveRequest, MathSolveResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_STEM_API_URL || 'http://localhost:8000';

interface UseMathSolverOptions {
  /**
   * Base URL for the API
   * @default process.env.REACT_APP_STEM_API_URL || 'http://localhost:8000'
   */
  baseUrl?: string;

  /**
   * Request timeout in milliseconds
   * @default 60000 (60 seconds)
   */
  timeout?: number;

  /**
   * Callback fired when solve succeeds
   */
  onSuccess?: (result: MathSolveResponse) => void;

  /**
   * Callback fired when solve fails
   */
  onError?: (error: Error) => void;
}

interface UseMathSolverReturn {
  /** Solve a math problem */
  solve: (request: MathSolveRequest) => Promise<MathSolveResponse>;

  /** Whether a request is currently in progress */
  loading: boolean;

  /** The most recent successful result */
  result: MathSolveResponse | null;

  /** The most recent error */
  error: Error | null;

  /** Reset state to initial values */
  reset: () => void;

  /** Cancel the current request */
  cancel: () => void;
}

export function useMathSolver(options: UseMathSolverOptions = {}): UseMathSolverReturn {
  const {
    baseUrl = API_BASE_URL,
    timeout = 60000,
    onSuccess,
    onError,
  } = options;

  // State
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MathSolveResponse | null>(null);
  const [error, setError] = useState<Error | null>(null);

  // Ref for abort controller
  const abortControllerRef = useRef<AbortController | null>(null);

  // Solve function
  const solve = useCallback(
    async (request: MathSolveRequest): Promise<MathSolveResponse> => {
      // Cancel any pending request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Create new abort controller
      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      // Reset state
      setLoading(true);
      setError(null);

      try {
        // Create timeout promise
        const timeoutPromise = new Promise<never>((_, reject) => {
          setTimeout(() => {
            abortController.abort();
            reject(new Error('Request timeout'));
          }, timeout);
        });

        // Create fetch promise
        const fetchPromise = fetch(`${baseUrl}/api/v1/math/solve`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(request),
          signal: abortController.signal,
        });

        // Race timeout vs fetch
        const response = await Promise.race([fetchPromise, timeoutPromise]);

        // Check response
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        // Parse response
        const data: MathSolveResponse = await response.json();

        // Update state
        setResult(data);
        setLoading(false);

        // Call success callback
        if (onSuccess) {
          onSuccess(data);
        }

        return data;
      } catch (err) {
        // Handle abort
        if (err instanceof Error && err.name === 'AbortError') {
          const abortError = new Error('Request was cancelled');
          setError(abortError);
          setLoading(false);
          throw abortError;
        }

        // Handle other errors
        const error = err instanceof Error ? err : new Error('Unknown error');
        setError(error);
        setLoading(false);

        // Call error callback
        if (onError) {
          onError(error);
        }

        throw error;
      } finally {
        abortControllerRef.current = null;
      }
    },
    [baseUrl, timeout, onSuccess, onError]
  );

  // Reset function
  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setLoading(false);
  }, []);

  // Cancel function
  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setLoading(false);
  }, []);

  return {
    solve,
    loading,
    result,
    error,
    reset,
    cancel,
  };
}

// ============================================================================
// Additional Hooks
// ============================================================================

/**
 * Hook for solving problems from images
 */
export function useImageSolver(options: UseMathSolverOptions = {}) {
  const { baseUrl = API_BASE_URL, timeout = 60000, onSuccess, onError } = options;

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MathSolveResponse | null>(null);
  const [error, setError] = useState<Error | null>(null);

  const solveFromImage = useCallback(
    async (file: File, options: Omit<MathSolveRequest, 'query'> = {}) => {
      setLoading(true);
      setError(null);

      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('show_steps', String(options.show_steps ?? true));
        formData.append('student_level', options.student_level ?? 'undergraduate');
        formData.append('include_educational', String(options.include_educational ?? true));
        formData.append('format', options.format ?? 'latex');

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(`${baseUrl}/api/v1/math/solve-image`, {
          method: 'POST',
          body: formData,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data: MathSolveResponse = await response.json();
        setResult(data);

        if (onSuccess) {
          onSuccess(data);
        }

        return data;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Unknown error');
        setError(error);

        if (onError) {
          onError(error);
        }

        throw error;
      } finally {
        setLoading(false);
      }
    },
    [baseUrl, timeout, onSuccess, onError]
  );

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return {
    solveFromImage,
    loading,
    result,
    error,
    reset,
  };
}

/**
 * Hook for batch solving multiple problems
 */
export function useBatchSolver(options: UseMathSolverOptions = {}) {
  const { baseUrl = API_BASE_URL, timeout = 60000 } = options;

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<MathSolveResponse[]>([]);
  const [errors, setErrors] = useState<Error[]>([]);

  const solveBatch = useCallback(
    async (requests: MathSolveRequest[]) => {
      setLoading(true);
      setResults([]);
      setErrors([]);

      const promises = requests.map(async (request) => {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), timeout);

          const response = await fetch(`${baseUrl}/api/v1/math/solve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
            signal: controller.signal,
          });

          clearTimeout(timeoutId);

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
          }

          return await response.json();
        } catch (err) {
          return { success: false, error: err instanceof Error ? err.message : 'Unknown error' };
        }
      });

      const settled = await Promise.allSettled(promises);

      const successResults: MathSolveResponse[] = [];
      const failureErrors: Error[] = [];

      settled.forEach((result) => {
        if (result.status === 'fulfilled') {
          successResults.push(result.value);
        } else {
          failureErrors.push(result.reason);
        }
      });

      setResults(successResults);
      setErrors(failureErrors);
      setLoading(false);

      return { results: successResults, errors: failureErrors };
    },
    [baseUrl, timeout]
  );

  return {
    solveBatch,
    loading,
    results,
    errors,
  };
}
