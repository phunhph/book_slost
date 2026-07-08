import { API_URL, parseApiError } from "@/lib/api";
import type { KolPublicCard, UserProfile } from "@/types/profile";

export async function getPublicKols(): Promise<KolPublicCard[]> {
  const response = await fetch(`${API_URL}/public/kols`);

  if (!response.ok) {
    return parseApiError(response, "Unable to load creators.");
  }

  return response.json() as Promise<KolPublicCard[]>;
}

export async function getPublicProfile(username: string): Promise<UserProfile> {
  const response = await fetch(`${API_URL}/profiles/public/${username}`);

  if (!response.ok) {
    return parseApiError(response, "Unable to load creator profile.");
  }

  return response.json() as Promise<UserProfile>;
}
