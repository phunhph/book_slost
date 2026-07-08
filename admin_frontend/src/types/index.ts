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
  expires_in?: number;
  user: AuthUser;
  message: string;
}

export interface RevenueSeries {
  labels: string[];
  gross: number[];
  collected: number[];
  booking_counts: number[];
}

export interface TopKolRevenue {
  kol_user_id: string;
  display_name: string;
  username: string | null;
  revenue: number;
  bookings: number;
}

export interface DashboardStats {
  total_kols: number;
  total_customers: number;
  total_bookings: number;
  pending_bookings: number;
  confirmed_bookings?: number;
  completed_bookings?: number;
  cancelled_bookings?: number;
  currency?: string;
  gross_revenue?: number;
  collected_revenue?: number;
  unpaid_revenue?: number;
  month_gross_revenue?: number;
  month_collected_revenue?: number;
  year_gross_revenue?: number;
  year_collected_revenue?: number;
  revenue_by_month?: RevenueSeries;
  revenue_by_year?: RevenueSeries;
  top_kols_by_revenue?: TopKolRevenue[];
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
  pricing_type?: string;
  quantity?: number;
  unit_price?: number;
  total_amount?: number;
  currency?: string;
  payment_qr_url?: string | null;
  payment_code?: string | null;
  payment_status?: string;
  status: string;
  notes: string | null;
  kol_display_name: string | null;
  kol_username: string | null;
  customer_email: string | null;
}
