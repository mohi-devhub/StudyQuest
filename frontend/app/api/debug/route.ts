import { NextResponse } from "next/server";

export async function GET() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "NOT_SET";
  
  // Try to fetch from backend
  let backendStatus = "unknown";
  let backendError = null;
  
  try {
    const response = await fetch(`${apiUrl}/health`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    
    if (response.ok) {
      const data = await response.json();
      backendStatus = data.status || "ok";
    } else {
      backendStatus = `error: ${response.status}`;
    }
  } catch (error: any) {
    backendStatus = "fetch_failed";
    backendError = error.message;
  }
  
  return NextResponse.json({
    environment: process.env.NODE_ENV,
    api_url_configured: apiUrl,
    api_url_is_localhost: apiUrl.includes("localhost"),
    backend_status: backendStatus,
    backend_error: backendError,
    timestamp: new Date().toISOString(),
  });
}
