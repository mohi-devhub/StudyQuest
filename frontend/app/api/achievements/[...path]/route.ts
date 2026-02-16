import { NextRequest, NextResponse } from "next/server";
import { createServerClient, type CookieOptions } from "@supabase/ssr";
import { cookies } from "next/headers";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

function isSegmentSafe(seg: string): boolean {
  return (
    seg.length > 0 &&
    seg !== "." &&
    seg !== ".." &&
    !seg.includes("/") &&
    !seg.includes("\\")
  );
}

async function getSession() {
  const cookieStore = await cookies();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value;
        },
        set(name: string, value: string, options: CookieOptions) {
          cookieStore.set({ name, value, ...options });
        },
        remove(name: string, options: CookieOptions) {
          cookieStore.set({ name, value: "", ...options });
        },
      },
    },
  );
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session;
}

export async function GET(request: NextRequest, context: RouteContext) {
  try {
    const session = await getSession();
    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { path } = await context.params;
    if (!path.every(isSegmentSafe)) {
      return NextResponse.json({ error: "Invalid path" }, { status: 400 });
    }

    const url = new URL(
      path.join("/"),
      `${API_BASE}/achievements/`,
    );
    request.nextUrl.searchParams.forEach((value, key) => {
      url.searchParams.set(key, value);
    });

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.access_token}`,
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    console.error("Achievements API error:", error);
    const message =
      error instanceof Error ? error.message : "Internal server error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

export async function POST(request: NextRequest, context: RouteContext) {
  try {
    const session = await getSession();
    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { path } = await context.params;
    if (!path.every(isSegmentSafe)) {
      return NextResponse.json({ error: "Invalid path" }, { status: 400 });
    }

    const url = new URL(
      path.join("/"),
      `${API_BASE}/achievements/`,
    );
    request.nextUrl.searchParams.forEach((value, key) => {
      url.searchParams.set(key, value);
    });

    const body = await request.json();

    const response = await fetch(url.toString(), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.access_token}`,
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    console.error("Achievements API error:", error);
    const message =
      error instanceof Error ? error.message : "Internal server error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
