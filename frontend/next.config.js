/** @type {import('next').NextConfig} */
const nextConfig = {
  // Skip static optimization for pages that need runtime data
  // This prevents build errors when Supabase env vars are missing
  experimental: {
    missingSuspenseWithCSRBailout: false,
  },
  // Ensure environment variables are available
  env: {
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL || '',
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '',
  },
};

module.exports = nextConfig;
