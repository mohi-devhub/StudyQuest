import { useState, useCallback } from "react";

interface UseLoadingStateReturn {
  isLoading: boolean;
  startLoading: () => void;
  stopLoading: () => void;
  setLoading: (loading: boolean) => void;
  withLoading: <T>(fn: () => Promise<T>) => Promise<T>;
}

/**
 * Custom hook for managing loading states
 *
 * @param initialState - Initial loading state (default: false)
 * @returns Loading state and control functions
 *
 * @example
 * const { isLoading, withLoading } = useLoadingState()
 *
 * const fetchData = async () => {
 *   await withLoading(async () => {
 *     const data = await api.fetch()
 *     setData(data)
 *   })
 * }
 */
export function useLoadingState(
  initialState: boolean = false,
): UseLoadingStateReturn {
  const [isLoading, setIsLoading] = useState(initialState);

  const startLoading = useCallback(() => {
    setIsLoading(true);
  }, []);

  const stopLoading = useCallback(() => {
    setIsLoading(false);
  }, []);

  const setLoading = useCallback((loading: boolean) => {
    setIsLoading(loading);
  }, []);

  /**
   * Wrapper function that automatically manages loading state
   * Sets loading to true before executing, and false after completion
   */
  const withLoading = useCallback(
    async <T>(fn: () => Promise<T>): Promise<T> => {
      try {
        setIsLoading(true);
        return await fn();
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  return {
    isLoading,
    startLoading,
    stopLoading,
    setLoading,
    withLoading,
  };
}
