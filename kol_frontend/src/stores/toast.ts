import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'info'

export interface ToastItem {
  id: string
  type: ToastType
  message: string
}

let toastCounter = 0

export const useToastStore = defineStore('toast', () => {
  const items = ref<ToastItem[]>([])

  function dismiss(id: string) {
    items.value = items.value.filter((item) => item.id !== id)
  }

  function push(type: ToastType, message: string, duration = 4200) {
    const id = `toast-${++toastCounter}-${Date.now()}`
    items.value.push({ id, type, message })

    if (duration > 0) {
      window.setTimeout(() => dismiss(id), duration)
    }

    return id
  }

  function success(message: string, duration?: number) {
    return push('success', message, duration)
  }

  function error(message: string, duration?: number) {
    return push('error', message, duration ?? 5200)
  }

  function info(message: string, duration?: number) {
    return push('info', message, duration)
  }

  return { items, dismiss, push, success, error, info }
})
