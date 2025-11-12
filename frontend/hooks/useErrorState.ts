import { useState, useCallback } from 'react'

interface UseErrorStateReturn {
  error: string | null
  setError: (error: string | null) => void
  clearError: () => void
  handleError: (error: unknown) => void
  withErrorHandling: <T>(fn: () => Promise<T>) => Promise<T | null>
}

/**
 * Custom hook for managing error states
 * 
 * @param initialError - Initial error state (default: null)
 * @returns Error state and control functions
 * 
 * @example
 * const { error, setError, clearError, withErrorHandling } = useErrorState()
 * 
 * const fetchData = async () => {
 *   const result = await withErrorHandling(async () => {
 *     return await api.fetch()
 *   })
 *   if (result) setData(result)
 * }
 */
export function useErrorState(initialError: string | null = null): UseErrorStateReturn {
  const [error, setErrorState] = useState<string | null>(initialError)

  const setError = useCallback((error: string | null) => {
    setErrorState(error)
  }, [])

  const clearError = useCallback(() => {
    setErrorState(null)
  }, [])

  /**
   * Handle errors with proper type checking
   */
  const handleError = useCallback((error: unknown) => {
    if (error instanceof Error) {
      setErrorState(error.message)
    } else if (typeof error === 'string') {
      setErrorState(error)
    } else {
      setErrorState('An unexpected error occurred')
    }
  }, [])

  /**
   * Wrapper function that automatically manages error state
   * Clears error before executing, sets error if exception occurs
   * Returns null if error occurs, otherwise returns result
   */
  const withErrorHandling = useCallback(
    async <T,>(fn: () => Promise<T>): Promise<T | null> => {
      try {
        setErrorState(null)
        return await fn()
      } catch (err) {
        handleError(err)
        return null
      }
    },
    [handleError]
  )

  return {
    error,
    setError,
    clearError,
    handleError,
    withErrorHandling,
  }
}
