import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  // Turbopack is dev-only; use Webpack for production builds (docker)
  // Do NOT set experimental.turbopack here — it causes panics in `next build`
};

export default nextConfig;
