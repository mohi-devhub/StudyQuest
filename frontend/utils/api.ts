const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Get full API URL
 */
export function getApiUrl(path: string): string {
  // Remove leading slash if present
  const cleanPath = path.startsWith('/') ? path.slice(1) : path
  return `${API_BASE}/${cleanPath}`
}

/**
 * Create authorization headers with token
 */
export function createAuthHeaders(token: string): HeadersInit {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  }
}

/**
 * Handle API response errors
 */
export async function handleApiError(response: Response): Promise<never> {
  let errorMessage = 'An error occurred'
  
  try {
    const data = await response.json()
    errorMessage = data.detail?.message || data.message || data.detail || errorMessage
  } catch {
    // If response is not JSON, use status text
    errorMessage = response.statusText || errorMessage
  }

  throw new Error(errorMessage)
}

/**
 * Fetch with error handling
 */
export async function fetchApi<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(url, options)

  if (!response.ok) {
    await handleApiError(response)
  }

  return response.json()
}

/**
 * POST request helper
 */
export async function postApi<T>(
  path: string,
  body: any,
  token?: string
): Promise<T> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return fetchApi<T>(getApiUrl(path), {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })
}

/**
 * GET request helper
 */
export async function getApi<T>(
  path: string,
  token?: string
): Promise<T> {
  const headers: HeadersInit = {}

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return fetchApi<T>(getApiUrl(path), {
    method: 'GET',
    headers,
  })
}

/**
 * Upload file helper
 */
export async function uploadFile<T>(
  path: string,
  formData: FormData,
  token?: string
): Promise<T> {
  const headers: HeadersInit = {}

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return fetchApi<T>(getApiUrl(path), {
    method: 'POST',
    headers,
    body: formData,
  })
}

/**
 * Fetch dashboard data with optimized loading
 * Progress loads immediately, recommendations load separately
 */
export async function fetchDashboardData(userId: string): Promise<{
  progress: any
  recommendations: any
}> {
  if (!userId) {
    throw new Error('User ID is required to fetch dashboard data')
  }

  // Fetch progress immediately (fast)
  const progress = await getApi(`progress/v2/${userId}`)

  // Return progress immediately, recommendations will be null
  return { progress, recommendations: null }
}

/**
 * Fetch recommendations separately (can be slow due to AI)
 */
export async function fetchRecommendations(userId: string): Promise<any> {
  if (!userId) {
    throw new Error('User ID is required to fetch recommendations')
  }

  return getApi(`study/recommendations?user_id=${userId}`)
}
