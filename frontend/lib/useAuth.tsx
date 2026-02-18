"use client";

import { User } from "@supabase/supabase-js";
import { createContext, useContext, useEffect, useState } from "react";

import { supabase } from "@/lib/supabase";

interface AuthContextType {
  user: User | null;
  userId: string | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, username: string) => Promise<{ requiresEmailConfirmation: boolean }>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check active session on mount
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setLoading(false);
    });

    // Listen for auth state changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signIn = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw error;

    // Wait for the session to be established
    if (data.session) {
      setUser(data.session.user);
    }
  };

  const signUp = async (email: string, password: string, username: string): Promise<{ requiresEmailConfirmation: boolean }> => {
    // Get the current origin for redirect URL — must point to the auth callback
    // handler so the PKCE code can be exchanged for a session.
    const redirectUrl = typeof window !== 'undefined'
      ? `${window.location.origin}/auth/callback`
      : 'https://study-quest-mohi-devhubs-projects.vercel.app/auth/callback';

    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          username,
        },
        emailRedirectTo: redirectUrl,
      },
    });
    if (error) throw error;

    // If a session was returned immediately, Supabase auto-confirmed the user
    // (email confirmation disabled). Otherwise, confirmation email was sent.
    if (data.session) {
      setUser(data.session.user);
      return { requiresEmailConfirmation: false };
    }

    return { requiresEmailConfirmation: true };
  };

  const signOut = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
  };

  const value = {
    user,
    userId: user?.id ?? null, // No fallback - require real auth
    loading,
    signIn,
    signUp,
    signOut,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
