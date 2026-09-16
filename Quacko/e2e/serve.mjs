// Minimal static server for the exported Expo web build (apps/mobile/dist).
import http from 'node:http';
import { createReadStream, existsSync, statSync } from 'node:fs';
import { join, extname, normalize } from 'node:path';

const ROOT = join(import.meta.dirname, '..', 'apps', 'mobile', 'dist');
const PORT = Number(process.env.PORT ?? 3535);

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.map': 'application/json',
};

const server = http.createServer((req, res) => {
  try {
    let pathname = decodeURIComponent((req.url ?? '/').split('?')[0]);
    if (pathname.endsWith('/')) pathname += 'index.html';

    let file = normalize(join(ROOT, pathname));
    if (!file.startsWith(ROOT)) {
      res.writeHead(403).end('forbidden');
      return;
    }

    if (!existsSync(file) || statSync(file).isDirectory()) {
      // SPA fallback: client-side router (mission/[id] etc.) reassembles the route.
      file = join(ROOT, 'index.html');
    }

    res.writeHead(200, { 'Content-Type': MIME[extname(file)] ?? 'application/octet-stream' });
    createReadStream(file).pipe(res);
  } catch {
    res.writeHead(500).end('server error');
  }
});

server.listen(PORT, () => {
  console.log(`[e2e] serving ${ROOT} on http://127.0.0.1:${PORT}`);
});