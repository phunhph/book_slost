const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export { API_BASE_URL, API_URL };

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function parseApiError(response: Response, fallbackMessage: string): Promise<never> {
  const errorBody = await response.json().catch(() => null);
  const detail = errorBody?.detail;

  if (typeof detail === "string") {
    throw new ApiError(detail, response.status);
  }

  if (Array.isArray(detail) && detail[0]?.msg) {
    throw new ApiError(String(detail[0].msg), response.status);
  }

  throw new ApiError(fallbackMessage, response.status);
}

export function authHeaders(token?: string): HeadersInit {
  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}
