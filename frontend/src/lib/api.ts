/**
 * API client configuration for Nexus API.
 *
 * Provides base URL configuration and fetch wrapper for API calls.
 * Uses environment variable VITE_API_URL for the API base URL.
 *
 * Docs: https://tanstack.com/query/latest/docs/framework/react/overview
 */

/** Base URL for API requests, defaults to localhost in development */
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/** Default headers for API requests */
const defaultHeaders: HeadersInit = {
  'Content-Type': 'application/json',
};

/**
 * Generic API error class for handling HTTP errors.
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    message?: string
  ) {
    super(message || `API Error: ${status} ${statusText}`);
    this.name = 'ApiError';
  }
}

/**
 * Fetch wrapper that handles common API response patterns.
 *
 * @param endpoint - API endpoint (relative to API_BASE_URL)
 * @param options - Fetch options
 * @returns Parsed JSON response
 * @throws ApiError on non-2xx responses
 */
export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new ApiError(
      response.status,
      response.statusText,
      errorBody || undefined
    );
  }

  return response.json() as Promise<T>;
}

/**
 * GET request helper.
 *
 * @param endpoint - API endpoint
 * @returns Parsed JSON response
 */
export async function apiGet<T>(endpoint: string): Promise<T> {
  return apiFetch<T>(endpoint, { method: 'GET' });
}

/**
 * POST request helper.
 *
 * @param endpoint - API endpoint
 * @param body - Request body (will be JSON stringified)
 * @returns Parsed JSON response
 */
export async function apiPost<T, B = unknown>(
  endpoint: string,
  body: B
): Promise<T> {
  return apiFetch<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}
