/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable image optimization
  images: {
    formats: ["image/avif", "image/webp"],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // Optimize compression and caching
  compress: true,
  poweredByHeader: false,
  generateEtags: true,

  // Server-side optimizations
  experimental: {
    serverActions: {
      bodySizeLimit: "10mb",
    },
  },

  // Enable SWR caching
  headers: async () => {
    return [
      {
        source: "/_next/static/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
