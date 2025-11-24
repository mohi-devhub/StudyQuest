/**
 * Simple cache utility for API calls
 * Implements stale-while-revalidate pattern for better performance
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

class APICache {
  private cache: Map<string, CacheEntry<any>>;
  private defaultTTL: number = 5 * 60 * 1000; // 5 minutes

  constructor() {
    this.cache = new Map();
  }

  /**
   * Get cached data or fetch new data
   */
  async get<T>(
    key: string,
    fetcher: () => Promise<T>,
    options: { ttl?: number; staleWhileRevalidate?: boolean } = {},
  ): Promise<T> {
    const { ttl = this.defaultTTL, staleWhileRevalidate = true } = options;
    const now = Date.now();
    const cached = this.cache.get(key);

    // Return fresh cache
    if (cached && now < cached.expiresAt) {
      console.log(`[CACHE] HIT: ${key} (fresh)`);
      return cached.data;
    }

    // Return stale cache and revalidate in background
    if (cached && staleWhileRevalidate) {
      console.log(`[CACHE] HIT: ${key} (stale, revalidating...)`);

      // Return stale data immediately
      const staleData = cached.data;

      // Revalidate in background
      this.revalidate(key, fetcher, ttl);

      return staleData;
    }

    // No cache or expired without stale-while-revalidate
    console.log(`[CACHE] MISS: ${key} (fetching...)`);
    const data = await fetcher();
    this.set(key, data, ttl);
    return data;
  }

  /**
   * Revalidate cache in background
   */
  private async revalidate<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttl: number,
  ): Promise<void> {
    try {
      const data = await fetcher();
      this.set(key, data, ttl);
      console.log(`[CACHE] REVALIDATED: ${key}`);
    } catch (error) {
      console.error(`[CACHE] REVALIDATION_FAILED: ${key}`, error);
    }
  }

  /**
   * Set cache entry
   */
  set<T>(key: string, data: T, ttl?: number): void {
    const now = Date.now();
    const expiresAt = now + (ttl || this.defaultTTL);

    this.cache.set(key, {
      data,
      timestamp: now,
      expiresAt,
    });
  }

  /**
   * Invalidate specific cache entry
   */
  invalidate(key: string): void {
    this.cache.delete(key);
    console.log(`[CACHE] INVALIDATED: ${key}`);
  }

  /**
   * Invalidate all cache entries matching pattern
   */
  invalidatePattern(pattern: string): void {
    const regex = new RegExp(pattern);
    let count = 0;

    Array.from(this.cache.keys()).forEach((key) => {
      if (regex.test(key)) {
        this.cache.delete(key);
        count++;
      }
    });

    console.log(`[CACHE] INVALIDATED_PATTERN: ${pattern} (${count} entries)`);
  }

  /**
   * Clear all cache
   */
  clear(): void {
    const size = this.cache.size;
    this.cache.clear();
    console.log(`[CACHE] CLEARED: ${size} entries`);
  }

  /**
   * Get cache stats
   */
  getStats(): {
    size: number;
    keys: string[];
    entries: Array<{ key: string; age: number; ttl: number }>;
  } {
    const now = Date.now();
    const entries = Array.from(this.cache.entries()).map(([key, entry]) => ({
      key,
      age: now - entry.timestamp,
      ttl: entry.expiresAt - now,
    }));

    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
      entries,
    };
  }

  /**
   * Clean expired entries
   */
  cleanup(): void {
    const now = Date.now();
    let count = 0;

    Array.from(this.cache.entries()).forEach(([key, entry]) => {
      if (now > entry.expiresAt) {
        this.cache.delete(key);
        count++;
      }
    });

    if (count > 0) {
      console.log(`[CACHE] CLEANUP: Removed ${count} expired entries`);
    }
  }
}

// Singleton instance
export const apiCache = new APICache();

// Auto cleanup every 5 minutes
if (typeof window !== "undefined") {
  setInterval(
    () => {
      apiCache.cleanup();
    },
    5 * 60 * 1000,
  );
}

/**
 * Helper hook for caching API calls in React components
 */
export function useCachedFetch<T>(
  key: string,
  fetcher: () => Promise<T>,
  options?: { ttl?: number; enabled?: boolean },
) {
  const [data, setData] = React.useState<T | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);

  React.useEffect(() => {
    if (options?.enabled === false) return;

    let isMounted = true;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const result = await apiCache.get(key, fetcher, {
          ttl: options?.ttl,
          staleWhileRevalidate: true,
        });

        if (isMounted) {
          setData(result);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err : new Error("Unknown error"));
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, [key, options?.enabled, options?.ttl]);

  return { data, loading, error, refetch: () => apiCache.invalidate(key) };
}

// Import React for the hook
import React from "react";

/**
 * Prefetch data and cache it
 */
export async function prefetch<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl?: number,
): Promise<void> {
  await apiCache.get(key, fetcher, { ttl, staleWhileRevalidate: false });
}

/**
 * Cache keys for common API endpoints
 */
export const CACHE_KEYS = {
  userProgress: (userId: string) => `user-progress-${userId}`,
  recommendations: (userId: string) => `recommendations-${userId}`,
  leaderboard: () => "leaderboard",
  quizResult: (quizId: string) => `quiz-result-${quizId}`,
  studyPackage: (topic: string) => `study-package-${topic}`,
} as const;
