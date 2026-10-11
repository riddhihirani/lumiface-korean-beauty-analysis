/**
 * LumiFace API Client Helper
 * 
 * Centralizes the backend API base URL so the application seamlessly operates
 * both in local development (defaulting to http://127.0.0.1:8000) and in cloud
 * deployment (configured via NEXT_PUBLIC_API_URL).
 */

export const API_BASE_URL: string = (
  process.env.NEXT_PUBLIC_API_URL?.trim().replace(/\/$/, '') || 'http://127.0.0.1:8000'
);

export function getApiUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
}
