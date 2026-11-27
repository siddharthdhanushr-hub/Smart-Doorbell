import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

const REPO_ROOT = path.resolve(__dirname, '..');

const ALLOWED_REPO_PREFIXES = [
  'shared/',
  'dataset/',
  'student1_esp32/benchmarks/',
  'student1_esp32/logs/',
  'student2_python/documentation/',
  'student4_validation/outputs/',
];

function repoStaticBridgePlugin(): Plugin {
  const serveRepoFile = (reqUrl: string | undefined, res: import('node:http').ServerResponse, next: () => void) => {
    if (!reqUrl || !reqUrl.startsWith('/repo/')) {
      next();
      return;
    }
    const relPath = decodeURIComponent(reqUrl.slice('/repo/'.length).split('?')[0]);
    const normalized = relPath.replace(/\\/g, '/').replace(/^\/+/, '');
    if (normalized.includes('..') || !ALLOWED_REPO_PREFIXES.some((p) => normalized.startsWith(p))) {
      res.statusCode = 403;
      res.end('Forbidden');
      return;
    }
    const absPath = path.resolve(REPO_ROOT, normalized);
    if (!absPath.startsWith(REPO_ROOT) || !fs.existsSync(absPath) || fs.statSync(absPath).isDirectory()) {
      res.statusCode = 404;
      res.end('Not found');
      return;
    }
    const ext = path.extname(absPath).toLowerCase();
    const mime =
      ext === '.json'
        ? 'application/json; charset=utf-8'
        : ext === '.csv'
          ? 'text/csv; charset=utf-8'
          : ext === '.md'
            ? 'text/markdown; charset=utf-8'
            : ext === '.png'
              ? 'image/png'
              : 'application/octet-stream';
    res.setHeader('Content-Type', mime);
    fs.createReadStream(absPath).pipe(res);
  };

  const forwardApiQuietly = (
    req: import('node:http').IncomingMessage,
    res: import('node:http').ServerResponse,
    next: () => void,
  ) => {
    if (!req.url || !req.url.startsWith('/api/')) {
      next();
      return;
    }
    const proxyReq = http.request(
      {
        hostname: '127.0.0.1',
        port: 5000,
        path: req.url,
        method: req.method,
        headers: { ...req.headers, host: '127.0.0.1:5000' },
        timeout: 1500,
      },
      (proxyRes) => {
        res.writeHead(proxyRes.statusCode ?? 200, proxyRes.headers);
        proxyRes.pipe(res);
      },
    );
    proxyReq.on('timeout', () => {
      proxyReq.destroy();
    });
    proxyReq.on('error', () => {
      if (!res.headersSent) {
        res.writeHead(503, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify({ status: 'offline', flaskOnline: false }));
      }
    });
    req.pipe(proxyReq);
  };

  return {
    name: 'smart-doorbell-repo-bridge',
    configureServer(server) {
      server.middlewares.use((req, res, next) => serveRepoFile(req.url, res, next));
      server.middlewares.use((req, res, next) => forwardApiQuietly(req, res, next));
    },
    configurePreviewServer(server) {
      server.middlewares.use((req, res, next) => serveRepoFile(req.url, res, next));
      server.middlewares.use((req, res, next) => forwardApiQuietly(req, res, next));
    },
  };
}

export default defineConfig({
  plugins: [react(), tailwindcss(), repoStaticBridgePlugin()],
  server: {
    port: 5173,
  },
});
