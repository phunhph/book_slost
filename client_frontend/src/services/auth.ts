import { API_BASE_URL, API_URL, authHeaders, parseApiError } from "@/lib/api";
import type { AuthResponse, AuthUser, LoginPayload, RegisterPayload } from "@/types/auth";
import type { UserProfile } from "@/types/profile";

export function getGoogleOAuthUrl() {
  return `${API_BASE_URL}/auth/google?app=client`;
}

export async function loginLocal(payload: LoginPayload): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/auth/login-local`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    return parseApiError(response, "Unable to sign in.");
  }

  return response.json() as Promise<AuthResponse>;
}

export async function registerLocal(payload: RegisterPayload): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/auth/register-local`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    return parseApiError(response, "Unable to create account.");
  }

  return response.json() as Promise<AuthResponse>;
}

export async function fetchCurrentUser(token: string): Promise<AuthUser> {
  const response = await fetch(`${API_URL}/auth/me`, {
    headers: authHeaders(token),
  });

  if (!response.ok) {
    return parseApiError(response, "Unable to load your account.");
  }

  return response.json() as Promise<AuthUser>;
}

export async function fetchProfileByUserId(userId: string, token?: string): Promise<UserProfile> {
  const response = await fetch(`${API_URL}/profiles/by-user/${userId}`, {
    headers: authHeaders(token),
  });

  if (!response.ok) {
    return parseApiError(response, "Unable to load profile details.");
  }

  return response.json() as Promise<UserProfile>;
}
