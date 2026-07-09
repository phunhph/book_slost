import { API_BASE_URL, API_URL, authHeaders, apiFetch, parseApiError } from "@/lib/api";
import type { BookingCreatePayload, BookingResponse } from "@/types/booking";

export function resolveMediaUrl(path: string | null | undefined): string | null {
  if (!path) return null;
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  return `${API_BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;
}

export async function createBooking(payload: BookingCreatePayload, token?: string): Promise<BookingResponse> {
  const response = await apiFetch(`${API_URL}/bookings`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    return parseApiError(response, "Không gửi được yêu cầu đặt lịch.");
  }

  return response.json() as Promise<BookingResponse>;
}

export async function getMyBookings(token: string): Promise<BookingResponse[]> {
  const response = await apiFetch(`${API_URL}/customer/bookings`, {
    headers: authHeaders(token),
  });

  if (!response.ok) {
    return parseApiError(response, "Không tải được danh sách booking của bạn.");
  }

  return response.json() as Promise<BookingResponse[]>;
}

export async function uploadPaymentProof(
  bookingId: string,
  file: File,
  token: string,
  note?: string,
): Promise<BookingResponse> {
  const form = new FormData();
  form.append("file", file);
  if (note?.trim()) {
    form.append("note", note.trim());
  }

  const response = await apiFetch(`${API_URL}/customer/bookings/${bookingId}/payment-proof`, {
    method: "POST",
    headers: authHeaders(token),
    body: form,
  });

  if (!response.ok) {
    return parseApiError(response, "Không gửi được bill chuyển khoản.");
  }

  return response.json() as Promise<BookingResponse>;
}
