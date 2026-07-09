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
        ? "Không kết nối được máy chủ. Vui lòng kiểm tra mạng và đảm bảo backend đang chạy tại http://localhost:8000."
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
