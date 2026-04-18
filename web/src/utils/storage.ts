const PREFIX = 'el_swe_'

export const storage = {
  get<T>(key: string): T | null {
    try {
      const value = localStorage.getItem(PREFIX + key)
      if (value === null) return null
      return JSON.parse(value) as T
    } catch {
      return null
    }
  },

  set<T>(key: string, value: T): void {
    localStorage.setItem(PREFIX + key, JSON.stringify(value))
  },

  remove(key: string): void {
    localStorage.removeItem(PREFIX + key)
  },

  clear(): void {
    localStorage.clear()
  },
}
