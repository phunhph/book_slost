import { apiRequest } from "./client";
import type { AuthResponse, BookingRow, CustomerRow, DashboardStats, KolRow, UserRow, PlatformRow } from "@/types";
import { API_BASE_URL } from "./client";

export function loginLocal(email: string, password: string) {
  return apiRequest<AuthResponse>("/auth/login-local", {
    method: "POST",
    body: JSON.stringify({ email, password })
  });
}

export function fetchMe(token: string) {
  return apiRequest<AuthResponse["user"]>("/auth/me", {}, token);
}

export function fetchDashboard(token: string) {
  return apiRequest<DashboardStats>("/admin/dashboard", {}, token);
}

export function fetchUsers(token: string, role?: string) {
  const path = role ? `/admin/users?role=${role}` : "/admin/users";
  return apiRequest<UserRow[]>(path, {}, token);
}

export function createAdminUser(token: string, data: Record<string, unknown>) {
  return apiRequest<UserRow>("/admin/users", {
    method: "POST",
    body: JSON.stringify(data)
  }, token);
}

export function updateAdminUser(token: string, userId: string, data: Record<string, unknown>) {
  return apiRequest<UserRow>(`/admin/users/${userId}`, {
    method: "PUT",
    body: JSON.stringify(data)
  }, token);
}

export function deleteAdminUser(token: string, userId: string) {
  return apiRequest<void>(`/admin/users/${userId}`, {
    method: "DELETE"
  }, token);
}

export function fetchAdminPlatforms(token: string) {
  return apiRequest<PlatformRow[]>("/admin/platforms", {}, token);
}

export function createAdminPlatform(token: string, data: Record<string, unknown>) {
  return apiRequest<PlatformRow>("/admin/platforms", {
    method: "POST",
    body: JSON.stringify(data)
  }, token);
}

export function updateAdminPlatform(token: string, platformId: string, data: Record<string, unknown>) {
  return apiRequest<PlatformRow>(`/admin/platforms/${platformId}`, {
    method: "PUT",
    body: JSON.stringify(data)
  }, token);
}

export function deleteAdminPlatform(token: string, platformId: string) {
  return apiRequest<void>(`/admin/platforms/${platformId}`, {
    method: "DELETE"
  }, token);
}

export function fetchPublicPlatforms() {
  return apiRequest<PlatformRow[]>("/profiles/platforms");
}


export function fetchKols(token: string) {
  return apiRequest<KolRow[]>("/admin/kols", {}, token);
}

export function fetchCustomers(token: string) {
  return apiRequest<CustomerRow[]>("/admin/customers", {}, token);
}

export function fetchBookings(token: string) {
  return apiRequest<BookingRow[]>("/admin/bookings", {}, token);
}

export function getGoogleOAuthUrl() {
  return `${API_BASE_URL}/auth/google?app=admin`;
}
