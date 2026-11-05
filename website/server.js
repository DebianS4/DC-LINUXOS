import http from 'node:http';
import { readFile, realpath } from 'node:fs/promises';
import { extname, isAbsolute, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const siteRoot = resolve(fileURLToPath(new URL('.', import.meta.url)));
const assetsRoot = resolve(siteRoot, 'assets');
const publicRoot = resolve(siteRoot, 'public');
const manifestPath = resolve(publicRoot, 'manus-routes.json');
const port = Number(process.env.PORT || 3000);
const host = process.env.HOST || '127.0.0.1';
const rootFiles = new Set(['index.html', 'styles.css', 'script.js', 'favicon.ico', 'favicon.svg']);
const types = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.ico': 'image/x-icon',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
};
const securityHeaders = {
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'no-referrer',
  'X-Frame-Options': 'DENY',
  'Cross-Origin-Resource-Policy': 'same-origin',
  'Content-Security-Policy': "default-src 'none'; base-uri 'self'; object-src 'none'; form-action 'none'; frame-src 'none'; frame-ancestors 'none'; worker-src 'none'; media-src 'none'; manifest-src 'none'; img-src 'self' data:; script-src 'self'; style-src 'self'; style-src-attr 'none'; font-src 'self'; connect-src 'none'; upgrade-insecure-requests",
  'Cache-Control': 'no-store',
};

function sendText(response, status, message, extraHeaders = {}) {
  response.writeHead(status, {
    ...securityHeaders,
    'Content-Type': 'text/plain; charset=utf-8',
    ...extraHeaders,
  });
  response.end(message);
}

function resolvePublicFile(pathname) {
  if (pathname === '/') {
    return { filePath: resolve(siteRoot, 'index.html'), allowedRoot: siteRoot, exactPath: true };
  }
  if (pathname === '/manus-routes.json') {
    return { filePath: manifestPath, allowedRoot: publicRoot, exactPath: true };
  }

  const relativePath = pathname.slice(1);
  if (rootFiles.has(relativePath)) {
    return { filePath: resolve(siteRoot, relativePath), allowedRoot: siteRoot, exactPath: true };
  }
  if (relativePath.startsWith('assets/')) {
    const assetName = relativePath.slice('assets/'.length);
    if (!/^[A-Za-z0-9._-]+$/.test(assetName)) return null;
    return { filePath: resolve(assetsRoot, assetName), allowedRoot: assetsRoot, exactPath: false };
  }
  return null;
}

const server = http.createServer(async (request, response) => {
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    sendText(response, 405, 'Method not allowed', { Allow: 'GET, HEAD' });
    return;
  }

  const rawPath = (request.url || '/').split('?', 1)[0];
  let pathname;
  try {
    pathname = decodeURIComponent(rawPath);
  } catch {
    sendText(response, 400, 'Bad request');
    return;
  }

  if (!pathname.startsWith('/') || pathname.includes('\\') || pathname.includes('\0')) {
    sendText(response, 400, 'Bad request');
    return;
  }
  if (pathname !== '/' && pathname.slice(1).split('/').some((segment) => !segment || segment === '.' || segment === '..')) {
    sendText(response, 403, 'Forbidden');
    return;
  }

  const entry = resolvePublicFile(pathname);
  if (!entry) {
    sendText(response, 404, 'Not found');
    return;
  }

  try {
    const finalPath = await realpath(entry.filePath);
    const relativeToAllowedRoot = relative(entry.allowedRoot, finalPath);
    if (
      relativeToAllowedRoot === '..' ||
      relativeToAllowedRoot.startsWith(`..${sep}`) ||
      isAbsolute(relativeToAllowedRoot) ||
      (entry.exactPath && finalPath !== entry.filePath)
    ) {
      sendText(response, 403, 'Forbidden');
      return;
    }

    const body = await readFile(finalPath);
    response.writeHead(200, {
      ...securityHeaders,
      'Content-Type': types[extname(finalPath).toLowerCase()] || 'application/octet-stream',
    });
    if (request.method === 'HEAD') response.end();
    else response.end(body);
  } catch {
    sendText(response, 404, 'Not found');
  }
});

if (!Number.isInteger(port) || port < 0 || port > 65535) {
  throw new RangeError('PORT must be an integer between 0 and 65535.');
}

server.listen(port, host, () => console.log(`DC-LINUX preview listening on http://${host}:${port}`));
