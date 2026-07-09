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

export const API_BASE_URL = inferApiBaseUrl();
const API_URL = inferApiUrl();

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function parseError(response: Response) {
  const body = await response.json().catch(() => null);
  const detail = body?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return String(detail[0].msg);
  if (response.status === 401) return "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.";
  if (response.status === 403) return "Bạn không có quyền thực hiện thao tác này.";
  if (response.status === 404) return "Không tìm thấy dữ liệu yêu cầu.";
  if (response.status >= 500) return "Máy chủ đang gặp sự cố. Vui lòng thử lại sau.";
  return "Yêu cầu thất bại. Vui lòng thử lại.";
}

export async function apiRequest<T>(path: string, options: RequestInit = {}, token?: string | null): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers });
  } catch {
    throw new ApiError(
      `Không kết nối được máy chủ. Frontend hiện đang gọi API tại ${API_URL}.`,
      0,
    );
  }

  if (!response.ok) {
    throw new ApiError(await parseError(response), response.status);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
