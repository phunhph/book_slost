export interface AuthUser {
  id: string;
  email: string;
  role: string;
  auth_provider: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
  message: string;
}

export interface DashboardStats {
  total_kols: number;
  total_customers: number;
  total_bookings: number;
  pending_bookings: number;
}

export interface KolRow {
  id: string;
  email: string;
  is_active: boolean;
  username: string | null;
  display_name: string | null;
  created_at: string;
}

export interface CustomerRow {
  id: string;
  email: string;
  is_active: boolean;
  display_name: string | null;
  phone: string | null;
  created_at: string;
}

export interface BookingRow {
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
  kol_display_name: string | null;
  kol_username: string | null;
  customer_email: string | null;
}
