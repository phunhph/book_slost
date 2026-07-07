import { UserProfile } from "@/features/profile/types/profile.types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

async function parseJsonError(response: Response, fallback: string): Promise<never> {
  const errorBody = await response.json().catch(() => null);
  throw new Error(errorBody?.detail ?? fallback);
}

export async function getPublicProfile(username: string): Promise<UserProfile> {
  const response = await fetch(`${API_URL}/profiles/public/${username}`, {
    cache: "no-store"
  });

  if (!response.ok) {
    return parseJsonError(response, "Failed to load public profile.");
  }

  return response.json() as Promise<UserProfile>;
}
