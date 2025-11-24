import { NextRequest, NextResponse } from "next/server";
import { createBrowserClient } from "@supabase/ssr";

export async function GET(request: NextRequest) {
  const healthStatus: {
    status: string;
    timestamp: string;
    dependencies: {
      backend?: {
        status: string;
        response_time_ms?: number;
        error?: string;
      };
      supabase?: {
        status: string;
        error?: string;
      };
    };
  } = {
    status: "healthy",
    timestamp: new Date().toISOString(),
    dependencies: {},
  };

  // Check backend API connectivity
  try {
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const startTime = Date.now();

    const response = await fetch(`${API_BASE}/health`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      // Add timeout
      signal: AbortSignal.timeout(5000),
    });

    const responseTime = Date.now() - startTime;

    if (response.ok) {
      healthStatus.dependencies.backend = {
        status: "healthy",
        response_time_ms: responseTime,
      };
    } else {
      healthStatus.status = "degraded";
      healthStatus.dependencies.backend = {
        status: "degraded",
        response_time_ms: responseTime,
        error: `HTTP ${response.status}`,
      };
    }
  } catch (error) {
    healthStatus.status = "degraded";
    healthStatus.dependencies.backend = {
      status: "unhealthy",
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }

  // Check Supabase client initialization
  try {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!supabaseUrl || !supabaseKey) {
      healthStatus.status = "degraded";
      healthStatus.dependencies.supabase = {
        status: "unhealthy",
        error: "Supabase credentials not configured",
      };
    } else {
      // Try to create client (this validates the configuration)
      const supabase = createBrowserClient(supabaseUrl, supabaseKey);

      healthStatus.dependencies.supabase = {
        status: "healthy",
      };
    }
  } catch (error) {
    healthStatus.status = "degraded";
    healthStatus.dependencies.supabase = {
      status: "unhealthy",
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }

  return NextResponse.json(healthStatus);
}
