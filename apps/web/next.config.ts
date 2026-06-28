import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Configure standalone build outputs for production Docker execution
  output: 'standalone',
};

export default nextConfig;
