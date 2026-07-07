import { UserProfile, UserProfileUpdatePayload } from "@/features/profile/types/profile.types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

async function parseJsonError(response: Response, fallback: string): Promise<never> {
  const errorBody = await response.json().catch(() => null);
  throw new Error(errorBody?.detail ?? fallback);
}

export async function getProfileByUserId(userId: string): Promise<UserProfile> {
  const response = await fetch(`${API_URL}/profiles/by-user/${userId}`, {
    cache: "no-store"
  });

  if (!response.ok) {
    return parseJsonError(response, "Failed to load profile.");
  }

  return response.json() as Promise<UserProfile>;
}

export async function updateProfile(userId: string, payload: UserProfileUpdatePayload): Promise<UserProfile> {
  const response = await fetch(`${API_URL}/profiles/by-user/${userId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    return parseJsonError(response, "Failed to update profile.");
  }

  return response.json() as Promise<UserProfile>;
}
