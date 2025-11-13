/**
 * Next.js App Router API Route Example
 * Location: app/api/math/solve/route.ts
 *
 * This creates a proxy endpoint to the STEM API
 */

import { NextRequest, NextResponse } from 'next/server';
import type { MathSolveRequest, MathSolveResponse } from '@/types/stem-api';

const STEM_API_URL = process.env.STEM_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    // Parse request body
    const body: MathSolveRequest = await request.json();

    // Validate required fields
    if (!body.query) {
      return NextResponse.json(
        { success: false, error: 'Query is required' },
        { status: 400 }
      );
    }

    // Forward request to STEM API
    const response = await fetch(`${STEM_API_URL}/api/v1/math/solve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      // Add timeout
      signal: AbortSignal.timeout(60000), // 60 second timeout
    });

    // Check if request was successful
    if (!response.ok) {
      throw new Error(`STEM API returned ${response.status}`);
    }

    // Parse and return response
    const data: MathSolveResponse = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Error calling STEM API:', error);

    // Handle different error types
    if (error instanceof TypeError && error.message.includes('timeout')) {
      return NextResponse.json(
        { success: false, error: 'Request timeout' },
        { status: 504 }
      );
    }

    return NextResponse.json(
      { success: false, error: 'Failed to solve problem' },
      { status: 500 }
    );
  }
}

// Optional: Add GET method for health check
export async function GET() {
  try {
    const response = await fetch(`${STEM_API_URL}/health`);
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { status: 'unhealthy', error: 'Cannot reach STEM API' },
      { status: 503 }
    );
  }
}
