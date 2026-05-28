const BASE = import.meta.env.VITE_API_URL ?? ''

export const API = {
  predict: `${BASE}/api/predict`,
  explore: (params) => `${BASE}/api/explore?${params}`,
}
