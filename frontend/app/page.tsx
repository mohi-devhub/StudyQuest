"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import LoadingScreen from "@/components/LoadingScreen";
import LandingPage from "@/app/landing/page";

export default function RootPage() {
  const { userId, loading: authLoading } = useAuth();
  const router = useRouter();

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (!authLoading && userId) {
      router.push("/dashboard");
    }
  }, [authLoading, userId, router]);

  // Show loading screen while checking authentication
  if (authLoading) {
    return <LoadingScreen />;
  }

  // Show landing page for unauthenticated users
  if (!userId) {
    return <LandingPage />;
  }

  // Return null while redirecting (prevents flash)
  return null;
}
