/** @type {import('next').NextConfig} */
const nextConfig = {
  // Skip static optimization for pages that need runtime data
  // This prevents build errors when Supabase env vars are missing
  experimental: {
    missingSuspenseWithCSRBailout: false,
  },
  // Allow build to pass with ESLint warnings
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Ensure environment variables are available
  env: {
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL || '',
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '',
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
};

module.exports = nextConfig;
