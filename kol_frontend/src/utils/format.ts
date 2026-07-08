export function formatDateTime(value: string) {
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

export function formatDate(value: string) {
  return new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  }).format(new Date(value))
}

export function startOfDayKey(value: string) {
  return new Date(value).toISOString().slice(0, 10)
}

export function formatStatus(status: string) {
  return status.charAt(0).toUpperCase() + status.slice(1)
}
