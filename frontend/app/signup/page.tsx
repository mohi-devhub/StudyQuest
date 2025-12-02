"use client";

import { useState } from "react";
import { useAuth } from "@/lib/useAuth";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const { signUp } = useAuth();
  const router = useRouter();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Validation
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      setLoading(false);
      return;
    }

    if (!username.trim()) {
      setError("Username is required");
      setLoading(false);
      return;
    }

    try {
      await signUp(email, password, username);
      setSuccess(true);
      // User needs to confirm email before logging in
    } catch (err: any) {
      setError(err.message || "Failed to create account");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="border border-white p-8 max-w-md w-full text-center"
        >
          <div className="text-4xl mb-4">✉️</div>
          <h2 className="text-2xl font-bold mb-4">// CHECK_YOUR_EMAIL</h2>
          <p className="text-gray-400 mb-6">
            We've sent a confirmation link to your email address.
            Please check your inbox and click the link to activate your account.
          </p>
          <p className="text-sm text-gray-500 mb-4">
            Don't see it? Check your spam folder.
          </p>
          <button
            onClick={() => router.push('/login')}
            className="w-full border border-white py-3 hover:bg-white hover:text-black transition-all"
          >
            GO TO LOGIN →
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-sm text-gray-500 mb-2"
          >
            // ACCOUNT_CREATION
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-4xl font-bold mb-2"
          >
            StudyQuest
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-gray-400 text-sm"
          >
            Create Your Learning Profile
          </motion.p>
        </div>

        {/* Signup Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="border border-white p-8"
        >
          <div className="text-sm text-gray-500 mb-6">// SIGNUP</div>

          {error && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="border border-red-500 bg-red-950 bg-opacity-20 p-3 mb-6 text-sm"
            >
              <span className="text-red-500">ERROR:</span> {error}
            </motion.div>
          )}

          <form onSubmit={handleSignup} className="space-y-6">
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                USERNAME
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-black border border-gray-600 px-4 py-3 focus:border-white focus:outline-none transition-colors font-mono"
                placeholder="your_username"
                required
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                EMAIL_ADDRESS
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-black border border-gray-600 px-4 py-3 focus:border-white focus:outline-none transition-colors font-mono"
                placeholder="user@example.com"
                required
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                PASSWORD
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-black border border-gray-600 px-4 py-3 focus:border-white focus:outline-none transition-colors font-mono"
                placeholder="••••••••"
                required
                disabled={loading}
                minLength={6}
              />
              <p className="text-xs text-gray-500 mt-1">Minimum 6 characters</p>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                CONFIRM_PASSWORD
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full bg-black border border-gray-600 px-4 py-3 focus:border-white focus:outline-none transition-colors font-mono"
                placeholder="••••••••"
                required
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-white text-black px-6 py-3 hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-mono font-bold"
            >
              {loading ? "CREATING_ACCOUNT..." : "CREATE_ACCOUNT >"}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-800">
            <p className="text-sm text-gray-400 text-center mb-4">
              Already have an account?
            </p>
            <Link
              href="/login"
              className="block w-full border border-white px-6 py-3 hover:bg-white hover:text-black transition-colors text-center font-mono"
            >
              LOGIN
            </Link>
          </div>
        </motion.div>

        {/* Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-6 border border-gray-700 p-6 bg-gray-950"
        >
          <div className="text-xs text-gray-500 mb-3">// ACCOUNT_FEATURES</div>
          <ul className="space-y-2 text-sm text-gray-400">
            <li>→ Personalized AI study notes</li>
            <li>→ Adaptive quiz generation</li>
            <li>→ XP & level progression system</li>
            <li>→ Achievement badges & milestones</li>
            <li>→ Real-time progress tracking</li>
          </ul>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-8 text-center text-xs text-gray-600"
        >
          <p>StudyQuest v1.0 // Production Build</p>
          <p className="mt-1">Powered by Supabase Auth</p>
        </motion.div>
      </motion.div>
    </div>
  );
}
