import { API_URL, apiFetch, parseApiError } from "@/lib/api";
import type { KolPublicCard, UserProfile } from "@/types/profile";

export async function getPublicKols(): Promise<KolPublicCard[]> {
  const response = await apiFetch(`${API_URL}/public/kols`);

  if (!response.ok) {
    return parseApiError(response, "Không tải được danh sách creator.");
  }

  return response.json() as Promise<KolPublicCard[]>;
}

export async function getPublicProfile(username: string): Promise<UserProfile> {
  const response = await apiFetch(`${API_URL}/profiles/public/${username}`);

  if (!response.ok) {
    return parseApiError(response, "Không tải được hồ sơ creator.");
  }

  return response.json() as Promise<UserProfile>;
}
