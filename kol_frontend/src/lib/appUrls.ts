export const CLIENT_APP_URL = import.meta.env.VITE_CLIENT_APP_URL ?? 'http://localhost:3001'

export function publicProfileUrl(username: string) {
  return `${CLIENT_APP_URL.replace(/\/$/, '')}/kol/${encodeURIComponent(username)}`
}
