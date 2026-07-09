export interface BookingCreatePayload {
  kol_user_id: string;
  scheduled_at: string;
  pricing_type?: "match" | "hourly";
  quantity?: number;
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
  pricing_type: string;
  quantity: number;
  unit_price: number;
  total_amount: number;
  currency: string;
  payment_qr_url: string | null;
  payment_code: string | null;
  payment_status: string;
  payment_proof_url?: string | null;
  payment_proof_note?: string | null;
  payment_proof_uploaded_at?: string | null;
  payment_reviewed_at?: string | null;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  kol_display_name: string | null;
  kol_username: string | null;
  customer_email: string | null;
  bank_name?: string | null;
  bank_account_number?: string | null;
  bank_account_name?: string | null;
}
