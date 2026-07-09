const NETWORK_PATTERNS = [
  'failed to fetch',
  'networkerror',
  'network error',
  'network request failed',
  'fetch failed',
  'load failed',
  'err_connection_refused',
  'err_connection_reset',
  'err_internet_disconnected',
  'econnrefused',
  'econnreset',
  'enotfound',
  'etimedout',
  'timeout',
]

const DEFAULT_NETWORK_MESSAGE =
  'Không kết nối được máy chủ. Kiểm tra lại domain API production hoặc cấu hình VITE_API_URL / VITE_API_BASE_URL.'

function isTechnicalNetworkMessage(message: string): boolean {
  const normalized = message.trim().toLowerCase()
  return NETWORK_PATTERNS.some((pattern) => normalized.includes(pattern))
}

function statusFallback(status: number): string {
  if (status === 401) return 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.'
  if (status === 403) return 'Bạn không có quyền thực hiện thao tác này.'
  if (status === 404) return 'Không tìm thấy dữ liệu yêu cầu.'
  if (status === 422) return 'Dữ liệu gửi lên không hợp lệ.'
  if (status >= 500) return 'Máy chủ đang gặp sự cố. Vui lòng thử lại sau.'
  return 'Yêu cầu thất bại. Vui lòng thử lại.'
}

export function getErrorMessage(
  error: unknown,
  fallback = 'Đã xảy ra lỗi. Vui lòng thử lại.',
): string {
  if (error instanceof TypeError && isTechnicalNetworkMessage(error.message)) {
    return DEFAULT_NETWORK_MESSAGE
  }

  if (error && typeof error === 'object') {
    const maybeAxios = error as {
      isAxiosError?: boolean;
      response?: { status?: number; data?: { detail?: unknown } };
      code?: string;
      message?: string;
    }

    if (maybeAxios.isAxiosError || maybeAxios.code === 'ERR_NETWORK') {
      if (!maybeAxios.response) {
        return DEFAULT_NETWORK_MESSAGE
      }
      const detail = maybeAxios.response.data?.detail
      if (typeof detail === 'string' && detail.trim()) return detail
      if (Array.isArray(detail) && (detail[0] as { msg?: string })?.msg) {
        return String((detail[0] as { msg: string }).msg)
      }
      if (maybeAxios.response.status) return statusFallback(maybeAxios.response.status)
    }

    if ('status' in error && typeof (error as { status: unknown }).status === 'number') {
      const status = (error as { status: number }).status
      const message = error instanceof Error ? error.message : ''
      if (message && !isTechnicalNetworkMessage(message) && message !== 'Request failed.') {
        return message
      }
      return statusFallback(status)
    }
  }

  if (error instanceof Error) {
    if (isTechnicalNetworkMessage(error.message)) {
      return DEFAULT_NETWORK_MESSAGE
    }
    return error.message?.trim() || fallback
  }

  if (typeof error === 'string' && error.trim()) {
    if (isTechnicalNetworkMessage(error)) return DEFAULT_NETWORK_MESSAGE
    return error
  }

  return fallback
}
