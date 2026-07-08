export interface BookingCreatePayload {
  kol_user_id: string;
  scheduled_at: string;
  notes?: string;
  guest_name?: string;
  guest_phone?: string;
  guest_zalo?: string;
  guest_messenger?: string;
}

export interface BookingResponse {
  id: string;
  kol_user_id: string;
  customer_user_id: string | null;
  guest_name: string | null;
  guest_phone: string | null;
  guest_zalo: string | null;
  guest_messenger: string | null;
  scheduled_at: string;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  kol_display_name: string | null;
  kol_username: string | null;
  customer_email: string | null;
}
