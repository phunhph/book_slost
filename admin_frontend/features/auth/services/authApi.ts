import { RegisterPayload, RegisterResponse } from "@/features/profile/types/profile.types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export async function registerLocal(payload: RegisterPayload): Promise<RegisterResponse> {
  const response = await fetch(`${API_URL}/auth/register-local`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    throw new Error(errorBody?.detail ?? "Failed to register user.");
  }

  return response.json() as Promise<RegisterResponse>;
}
