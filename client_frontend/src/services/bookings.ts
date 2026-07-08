import { API_URL, authHeaders, parseApiError } from "@/lib/api";
import type { BookingCreatePayload, BookingResponse } from "@/types/booking";

export async function createBooking(payload: BookingCreatePayload, token?: string): Promise<BookingResponse> {
  const response = await fetch(`${API_URL}/bookings`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    return parseApiError(response, "Unable to submit booking.");
  }

  return response.json() as Promise<BookingResponse>;
}
