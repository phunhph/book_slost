function inferApiBaseUrl() {
  const configured = import.meta.env.VITE_API_BASE_URL?.trim();
  if (configured) return configured;

  if (typeof window === "undefined") return "http://localhost:8000";

  const { protocol, hostname } = window.location;
  if (hostname === "localhost" || hostname === "127.0.0.1") {
    return "http://localhost:8000";
  }

  const parts = hostname.split(".");
  if (parts.length >= 3 && ["admin", "client", "kol"].includes(parts[0])) {
    return `${protocol}//api.${parts.slice(1).join(".")}`;
  }

  if (hostname.startsWith("api.")) {
    return `${protocol}//${hostname}`;
  }

  return `${protocol}//${hostname}`;
}

function inferApiUrl() {
  const configured = import.meta.env.VITE_API_URL?.trim();
  if (configured) return configured;
  return `${inferApiBaseUrl().replace(/\/$/, "")}/api`;
}

const API_URL = inferApiUrl();
const API_BASE_URL = inferApiBaseUrl();

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

  if (response.status === 401) {
    throw new ApiError("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.", response.status);
  }
  if (response.status === 403) {
    throw new ApiError("Bạn không có quyền thực hiện thao tác này.", response.status);
  }
  if (response.status === 404) {
    throw new ApiError("Không tìm thấy dữ liệu yêu cầu.", response.status);
  }
  if (response.status >= 500) {
    throw new ApiError("Máy chủ đang gặp sự cố. Vui lòng thử lại sau.", response.status);
  }

  throw new ApiError(fallbackMessage, response.status);
}

export async function apiFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(input, init);
  } catch (error) {
    const message =
      error instanceof TypeError
        ? `Không kết nối được máy chủ. Frontend hiện đang gọi API tại ${API_URL}.`
        : error instanceof Error
          ? error.message
          : "Không kết nối được máy chủ.";
    throw new ApiError(message, 0);
  }
}

export function authHeaders(token?: string): HeadersInit {
  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}
