/**
 * TypeScript Type Definitions for STEM Service API
 *
 * Copy this file to your project and import the types you need:
 * import { MathSolveRequest, MathSolveResponse } from './types';
 */

// ============================================================================
// REQUEST TYPES
// ============================================================================

/**
 * Request payload for solving math problems
 */
export interface MathSolveRequest {
  /** The mathematical problem to solve */
  query: string;

  /** Include step-by-step solution (default: true) */
  show_steps?: boolean;

  /** Student education level */
  student_level?: 'high_school' | 'undergraduate' | 'graduate';

  /** Include educational content and practice problems (default: true) */
  include_educational?: boolean;

  /** Output format for mathematical expressions */
  format?: 'plaintext' | 'latex' | 'mathml' | 'image';
}

/**
 * FormData fields for image-based problem solving
 */
export interface ImageSolveFormData {
  /** Image file containing the math problem */
  file: File;

  /** Include step-by-step solution */
  show_steps?: boolean | string;

  /** Student education level */
  student_level?: string;

  /** Include educational content */
  include_educational?: boolean | string;

  /** Output format */
  format?: string;
}

/**
 * Request payload for creating plots
 */
export interface PlotRequest {
  /** Mathematical expression to plot */
  expression: string;

  /** Variable name (default: 'x') */
  variable?: string;

  /** Minimum range value (default: -10) */
  range_min?: number;

  /** Maximum range value (default: 10) */
  range_max?: number;

  /** Type of plot (default: 'Plot') */
  plot_type?: string;
}

// ============================================================================
// RESPONSE TYPES
// ============================================================================

/**
 * A single step in a solution
 */
export interface SolutionStep {
  /** Step number (1-indexed) */
  step_number: number;

  /** Human-readable description of the step */
  description: string;

  /** Mathematical expression for this step */
  math: string;
}

/**
 * Image data for visualizations
 */
export interface ImageData {
  /** Image source URL */
  src: string;

  /** Alt text for accessibility */
  alt?: string;

  /** Image width */
  width?: string;

  /** Image height */
  height?: string;
}

/**
 * Visualization containing a plot or diagram
 */
export interface Visualization {
  /** Title of the visualization */
  title: string;

  /** Image data */
  image: ImageData;
}

/**
 * Flashcard for studying
 */
export interface Flashcard {
  /** Question on the flashcard */
  question: string;

  /** Answer to the question */
  answer: string;
}

/**
 * Educational content related to the problem
 */
export interface EducationalContent {
  /** Key mathematical concepts covered */
  key_concepts?: string[];

  /** Related practice problems */
  practice_problems?: string[];

  /** Study flashcards */
  flashcards?: Flashcard[];

  /** Additional learning resources */
  resources?: string[];
}

/**
 * Result data from Wolfram API
 */
export interface MathResult {
  /** Original query sent to Wolfram */
  original_query: string;

  /** Whether the computation was successful */
  success: boolean;

  /** Final answer to the problem */
  final_answer: string | null;

  /** Step-by-step solution (may be in result or top-level) */
  steps?: SolutionStep[];

  /** Visualizations (may be in result or top-level) */
  visualizations?: Visualization[];

  /** Error message if computation failed */
  error?: string | null;
}

/**
 * Complete response from math solve endpoint
 */
export interface MathSolveResponse {
  /** Whether the request was successful */
  success: boolean;

  /** Original query from the request */
  query: string;

  /** Computed result from Wolfram API */
  result: MathResult;

  /** GPT-enhanced explanation */
  explanation?: string | null;

  /** Step-by-step solution (top-level, may also be in result) */
  steps?: SolutionStep[] | null;

  /** Educational content and learning resources */
  educational_content?: EducationalContent | null;

  /** Plots and diagrams (top-level, may also be in result) */
  visualizations?: Visualization[] | null;

  /** Error message if request failed */
  error?: string | null;
}

/**
 * Response from plot endpoint
 */
export interface PlotResponse {
  /** Whether the plot was created successfully */
  success: boolean;

  /** Expression that was plotted */
  expression: string;

  /** URL to the plot image */
  plot: string | null;

  /** Error message if plot creation failed */
  error: string | null;
}

/**
 * Health check response
 */
export interface HealthResponse {
  /** Service health status */
  status: string;

  /** Service name */
  service: string;

  /** Timestamp of health check */
  timestamp: string;
}

// ============================================================================
// ERROR TYPES
// ============================================================================

/**
 * Standard API error response
 */
export interface ApiError {
  /** Error message */
  error: string;

  /** HTTP status code */
  status?: number;

  /** Additional error details */
  details?: any;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * API response wrapper
 */
export type ApiResponse<T> =
  | { success: true; data: T }
  | { success: false; error: ApiError };

/**
 * Format options for mathematical expressions
 */
export type MathFormat = 'plaintext' | 'latex' | 'mathml' | 'image';

/**
 * Student education levels
 */
export type StudentLevel = 'high_school' | 'undergraduate' | 'graduate';

/**
 * API endpoints
 */
export enum ApiEndpoint {
  HEALTH = '/health',
  SOLVE = '/api/v1/math/solve',
  SOLVE_IMAGE = '/api/v1/math/solve-image',
  PLOT = '/api/v1/math/plot',
}

// ============================================================================
// TYPE GUARDS
// ============================================================================

/**
 * Type guard to check if response is successful
 */
export function isSuccessResponse(
  response: MathSolveResponse
): response is MathSolveResponse & { success: true } {
  return response.success === true;
}

/**
 * Type guard to check if response has steps
 */
export function hasSteps(
  response: MathSolveResponse
): response is MathSolveResponse & { steps: SolutionStep[] } {
  return Array.isArray(response.steps) && response.steps.length > 0;
}

/**
 * Type guard to check if response has visualizations
 */
export function hasVisualizations(
  response: MathSolveResponse
): response is MathSolveResponse & { visualizations: Visualization[] } {
  return Array.isArray(response.visualizations) && response.visualizations.length > 0;
}
