  /** @type {import('next').NextConfig} */
  const nextConfig = {
    reactStrictMode: true,
    // Remove 'output: standalone' for Vercel
    images: {
      remotePatterns: [
        { protocol: 'https', hostname: '**' }
      ],
    },
  }

  module.exports = nextConfig
