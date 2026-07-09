import { apiRequest } from "./client";
import type { AuthResponse, BookingRow, CustomerRow, DashboardStats, KolRow } from "@/types";
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
