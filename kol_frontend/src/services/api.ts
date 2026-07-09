import axios from 'axios'
import type {
  AuthResponse,
  Booking,
  DashboardStats,
  ProfileUpdatePayload,
  User,
  UserProfile,
} from '../types'

export const TOKEN_KEY = 'abc_kol_access_token'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const googleOAuthUrl = `${API_BASE_URL}/auth/google?app=kol`

export function resolveMediaUrl(path: string | null | undefined): string | null {
  if (!path) return null
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  return `${API_BASE_URL}${path.startsWith('/') ? '' : '/'}${path}`
}

export const api = axios.create({
  baseURL: API_URL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      error.message =
        'Không kết nối được máy chủ. Vui lòng kiểm tra mạng và đảm bảo backend đang chạy tại http://localhost:8000.'
    } else if (typeof error.response.data?.detail === 'string') {
      error.message = error.response.data.detail
    } else if (Array.isArray(error.response.data?.detail) && error.response.data.detail[0]?.msg) {
      error.message = String(error.response.data.detail[0].msg)
    }
    return Promise.reject(error)
  },
)

export async function loginLocal(email: string, password: string) {
  const { data } = await api.post<AuthResponse>('/auth/login-local', { email, password })
  return data
}

export async function getCurrentUser() {
  const { data } = await api.get<User>('/auth/me')
  return data
}

export async function getKolDashboard() {
  const { data } = await api.get<DashboardStats>('/kol/dashboard')
  return data
}

export async function getKolBookings() {
  const { data } = await api.get<Booking[]>('/kol/bookings')
  return data
}

export async function updateBookingStatus(bookingId: string, status: string) {
  const { data } = await api.patch<Booking>(`/kol/bookings/${bookingId}`, { status })
  return data
}

export async function reviewPaymentProof(
  bookingId: string,
  action: 'approve' | 'reject',
  note?: string,
) {
  const { data } = await api.patch<Booking>(`/kol/bookings/${bookingId}/payment-review`, {
    action,
    note: note || undefined,
  })
  return data
}

export async function getProfileByUser(userId: string) {
  const { data } = await api.get<UserProfile>(`/profiles/by-user/${userId}`)
  return data
}

export async function updateProfileByUser(userId: string, payload: ProfileUpdatePayload) {
  const { data } = await api.put<UserProfile>(`/profiles/by-user/${userId}`, payload)
  return data
}
