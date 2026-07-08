import { API_URL, authHeaders, apiFetch, parseApiError } from "@/lib/api";
import type { BookingCreatePayload, BookingResponse } from "@/types/booking";

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
