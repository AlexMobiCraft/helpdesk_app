/** @type {import('next').NextConfig} */
const HOST_IP = process.env.HOST_IP;

module.exports = {
  reactStrictMode: true,
  allowedDevOrigins: [
    '127.0.0.1',
    'localhost',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    HOST_IP,
    `${HOST_IP}:3000`,
    `http://${HOST_IP}:3000`
  ],

  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `http://${HOST_IP}:8000/api/:path*`,
      },
    ];
  },
};
