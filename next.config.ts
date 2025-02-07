const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "https://pawn-buy-shop.onrender.com/:path*", // Proxy to backend
      },
    ];
  },
};
