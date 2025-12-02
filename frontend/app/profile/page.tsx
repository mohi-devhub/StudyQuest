"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { useAuth } from "@/lib/useAuth";
import { supabase } from "@/lib/supabase";
import { createLogger } from "@/lib/logger";

const logger = createLogger("ProfilePage");

interface UserProfile {
  username: string;
  email: string;
  total_xp: number;
  level: number;
  created_at: string;
}

export default function ProfilePage() {
  const router = useRouter();
  const { userId, user, signOut } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [loggingOut, setLoggingOut] = useState(false);
  const [isEditingUsername, setIsEditingUsername] = useState(false);
  const [newUsername, setNewUsername] = useState("");
  const [savingUsername, setSavingUsername] = useState(false);
  const [usernameError, setUsernameError] = useState<string | null>(null);

  useEffect(() => {
    if (!userId) {
      router.push("/login");
      return;
    }
    fetchProfile();
  }, [userId, router]);

  const fetchProfile = async () => {
    if (!userId) return;

    try {
      setLoading(true);

      // Fetch user data from users table
      const { data: userData, error: userError } = await supabase
        .from("users")
        .select("username, total_xp, level, created_at")
        .eq("user_id", userId)
        .single();

      if (userError) throw userError;

      setProfile({
        username: userData?.username || "Unknown",
        email: user?.email || "No email",
        total_xp: userData?.total_xp || 0,
        level: userData?.level || 1,
        created_at: userData?.created_at || new Date().toISOString(),
      });
    } catch (error) {
      logger.error("Error fetching profile", { userId, error: String(error) });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await signOut();
      router.push("/login");
    } catch (error) {
      logger.error("Logout error", { userId, error: String(error) });
      setLoggingOut(false);
    }
  };

  const handleEditUsername = () => {
    setNewUsername(profile?.username || "");
    setUsernameError(null);
    setIsEditingUsername(true);
  };

  const handleCancelEdit = () => {
    setIsEditingUsername(false);
    setNewUsername("");
    setUsernameError(null);
  };

  const handleSaveUsername = async () => {
    if (!userId || !newUsername.trim()) return;

    const trimmedUsername = newUsername.trim();

    // Validate username
    if (trimmedUsername.length < 3) {
      setUsernameError("Username must be at least 3 characters");
      return;
    }

    if (trimmedUsername.length > 20) {
      setUsernameError("Username must be 20 characters or less");
      return;
    }

    if (!/^[a-zA-Z0-9_]+$/.test(trimmedUsername)) {
      setUsernameError("Username can only contain letters, numbers, and underscores");
      return;
    }

    setSavingUsername(true);
    setUsernameError(null);

    try {
      const { error } = await supabase
        .from("users")
        .update({ username: trimmedUsername })
        .eq("user_id", userId);

      if (error) throw error;

      // Update local state
      setProfile((prev) => prev ? { ...prev, username: trimmedUsername } : null);
      setIsEditingUsername(false);
      setNewUsername("");
    } catch (error: any) {
      logger.error("Error updating username", { userId, error: String(error) });
      setUsernameError(error.message || "Failed to update username");
    } finally {
      setSavingUsername(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-terminal-black flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="text-terminal-white text-xl font-mono">
            LOADING PROFILE<span className="animate-pulse">...</span>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-terminal-black text-terminal-white p-6 md:p-8 font-mono">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Link
            href="/"
            className="text-terminal-gray text-sm hover:text-terminal-white transition-colors mb-4 inline-block"
          >
            ← BACK_TO_DASHBOARD
          </Link>
          <div className="bg-terminal-white text-terminal-black px-6 py-4">
            <h1 className="text-3xl font-bold text-center">
              ═══════════ USER PROFILE ═══════════
            </h1>
          </div>
        </motion.div>

        {/* Profile Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="border border-terminal-white mb-6"
        >
          {/* User Info Section */}
          <div className="p-6 border-b border-terminal-gray">
            <div className="flex items-center justify-between mb-6">
              <div className="flex-1">
                <div className="text-sm text-terminal-gray mb-1">
                  // USERNAME
                </div>
                {isEditingUsername ? (
                  <div className="space-y-2">
                    <input
                      type="text"
                      value={newUsername}
                      onChange={(e) => setNewUsername(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleSaveUsername();
                        if (e.key === "Escape") handleCancelEdit();
                      }}
                      className="w-full max-w-xs bg-terminal-black border border-terminal-white px-3 py-2 text-terminal-white focus:outline-none focus:ring-1 focus:ring-terminal-white"
                      placeholder="Enter new username"
                      maxLength={20}
                      autoFocus
                    />
                    {usernameError && (
                      <div className="text-red-400 text-xs">{usernameError}</div>
                    )}
                    <div className="flex gap-2">
                      <button
                        onClick={handleSaveUsername}
                        disabled={savingUsername}
                        className="px-4 py-1 border border-terminal-white text-sm hover:bg-terminal-white hover:text-terminal-black transition-colors disabled:opacity-50"
                      >
                        {savingUsername ? "SAVING..." : "SAVE"}
                      </button>
                      <button
                        onClick={handleCancelEdit}
                        disabled={savingUsername}
                        className="px-4 py-1 border border-terminal-gray text-terminal-gray text-sm hover:border-terminal-white hover:text-terminal-white transition-colors disabled:opacity-50"
                      >
                        CANCEL
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-3">
                    <div className="text-2xl font-bold">{profile?.username}</div>
                    <button
                      onClick={handleEditUsername}
                      className="text-terminal-gray hover:text-terminal-white transition-colors text-sm border border-terminal-gray hover:border-terminal-white px-2 py-1"
                    >
                      EDIT
                    </button>
                  </div>
                )}
              </div>
              <div className="border border-terminal-white px-4 py-2">
                <div className="text-terminal-gray text-xs">LEVEL</div>
                <div className="text-2xl font-bold text-center">
                  {profile?.level}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <div className="text-sm text-terminal-gray mb-1">// EMAIL</div>
                <div className="text-lg">{profile?.email}</div>
              </div>

              <div>
                <div className="text-sm text-terminal-gray mb-1">
                  // TOTAL XP
                </div>
                <div className="text-lg font-bold">
                  {profile?.total_xp.toLocaleString()} XP
                </div>
              </div>

              <div>
                <div className="text-sm text-terminal-gray mb-1">
                  // MEMBER SINCE
                </div>
                <div className="text-lg">
                  {profile && formatDate(profile.created_at)}
                </div>
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 p-6 border-b border-terminal-gray">
            <div className="border border-terminal-gray p-4">
              <div className="text-terminal-gray text-xs mb-2">
                XP TO NEXT LEVEL
              </div>
              <div className="text-xl font-bold">
                {profile ? Math.max(0, (profile.level * 500) - profile.total_xp) : 0}
              </div>
            </div>
            <div className="border border-terminal-gray p-4">
              <div className="text-terminal-gray text-xs mb-2">
                CURRENT LEVEL
              </div>
              <div className="text-xl font-bold">{profile?.level}</div>
            </div>
            <div className="border border-terminal-gray p-4 col-span-2 md:col-span-1">
              <div className="text-terminal-gray text-xs mb-2">
                ACCOUNT STATUS
              </div>
              <div className="text-xl font-bold">ACTIVE</div>
            </div>
          </div>

          {/* Actions */}
          <div className="p-6">
            <button
              onClick={handleLogout}
              disabled={loggingOut}
              className="w-full bg-terminal-black text-terminal-white border border-terminal-white px-6 py-3 hover:bg-terminal-white hover:text-terminal-black transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loggingOut ? "LOGGING OUT..." : "> LOGOUT"}
            </button>
          </div>
        </motion.div>

        {/* Additional Info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="border border-terminal-gray p-4"
        >
          <div className="text-terminal-gray text-sm space-y-2">
            <p>// Session Information</p>
            <p>User ID: {userId}</p>
            <p>Authentication: Supabase Auth</p>
            <p>Session: Active</p>
          </div>
        </motion.div>

        {/* Terminal Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-8 text-center text-terminal-gray text-xs"
        >
          <p>$ user --profile --session=active</p>
        </motion.div>
      </div>
    </div>
  );
}
