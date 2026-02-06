import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  rewrites: async () => {
    return [
      {
        source: '/api/:path*',
        destination:
          process.env.NODE_ENV === 'development'
            ? 'http://127.0.0.1:8000/api/:path*' // Local Testing
            : 'https://f1-telemetry-fy5v.onrender.com/api/:path*', // Production Link (We will get this in Step 4)
      },
    ];
  },
};

export default nextConfig;