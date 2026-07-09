import { API_BASE_URL, API_URL, authHeaders, apiFetch, parseApiError } from "@/lib/api";
import type { AuthResponse, AuthUser, LoginPayload, RegisterPayload } from "@/types/auth";
import type { UserProfile } from "@/types/profile";

export function getGoogleOAuthUrl() {
  return `${API_BASE_URL}/auth/google?app=client`;
}

export async function loginLocal(payload: LoginPayload): Promise<AuthResponse> {
  const response = await apiFetch(`${API_URL}/auth/login-local`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    return parseApiError(response, "Không thể đăng nhập.");
  }

  return response.json() as Promise<AuthResponse>;
}

export async function registerLocal(payload: RegisterPayload): Promise<AuthResponse> {
  const response = await apiFetch(`${API_URL}/auth/register-local`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    return parseApiError(response, "Không thể tạo tài khoản.");
  }

  return response.json() as Promise<AuthResponse>;
}

export async function fetchCurrentUser(token: string): Promise<AuthUser> {
  const response = await apiFetch(`${API_URL}/auth/me`, {
    headers: authHeaders(token),
  });

  if (!response.ok) {
    return parseApiError(response, "Không tải được thông tin tài khoản.");
  }

  return response.json() as Promise<AuthUser>;
}

export async function fetchProfileByUserId(userId: string, token?: string): Promise<UserProfile> {
  const response = await apiFetch(`${API_URL}/profiles/by-user/${userId}`, {
    headers: authHeaders(token),
  });

  if (!response.ok) {
    return parseApiError(response, "Không tải được thông tin hồ sơ.");
  }

  return response.json() as Promise<UserProfile>;
}
