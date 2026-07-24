import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '../..');
const DIST = path.join(ROOT, 'web', 'dist');
const PORT = Number(process.env.PORT || 7788);

const MIME: Record<string, string> = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.woff2': 'font/woff2',
  '.ico': 'image/x-icon',
};

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': '*',
};

function serveStatic(reqUrl: string, res: http.ServerResponse) {
  let p = reqUrl === '/' ? '/index.html' : reqUrl.split('?')[0];
  const file = path.join(DIST, p);
  if (!file.startsWith(DIST) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404, { ...CORS });
    res.end('not found');
    return;
  }
  res.writeHead(200, {
    'Content-Type': MIME[path.extname(file)] || 'application/octet-stream',
    ...CORS,
  });
  fs.createReadStream(file).pipe(res);
}

let updating = false;

function handleUpdate(res: http.ServerResponse) {
  if (updating) {
    res.writeHead(409, { 'Content-Type': 'text/plain; charset=utf-8', ...CORS });
    res.end('已有一次更新在进行中，请等待。');
    return;
  }
  updating = true;
  res.writeHead(200, {
    'Content-Type': 'text/plain; charset=utf-8',
    'Cache-Control': 'no-cache',
    ...CORS,
  });
  const send = (s: string) => res.write(s);
  send('▶ 增量更新开始（scan → extract → build-data → build:web）\n');
  const child = spawn('npm', ['run', 'build'], {
    cwd: ROOT,
    env: { ...process.env },
    shell: true,
  });
  child.on('error', (err) => {
    send(`\n✗ 启动构建进程失败: ${err.message}\n`);
    updating = false;
    res.end();
  });
  child.stdout.on('data', (d) => send(d.toString()));
  child.stderr.on('data', (d) => send(d.toString()));
  child.on('close', (code) => {
    send(`\n${code === 0 ? '✓ 更新成功' : '✗ 更新失败 (exit ' + code + ')'}\n`);
    if (code === 0) send('DONE\n');
    updating = false;
    res.end();
  });
}

const server = http.createServer((req, res) => {
  if (req.method === 'OPTIONS') {
    res.writeHead(204, CORS);
    res.end();
    return;
  }
  if (req.method === 'POST' && req.url === '/api/update') return handleUpdate(res);
  if (req.method === 'GET' && req.url === '/api/health') {
    res.writeHead(200, { 'Content-Type': 'application/json', ...CORS });
    res.end(JSON.stringify({ ok: true, updating }));
    return;
  }
  if (req.method === 'GET') return serveStatic(req.url || '/', res);
  res.writeHead(404, CORS);
  res.end();
});

server.listen(PORT, () => {
  console.log(`Omni 文件索引服务已启动: http://localhost:${PORT}`);
  console.log(`  · 浏览器打开上面地址 → 页面右上角「增量更新」按钮可用`);
  console.log(`  · 或双击 web/dist/index.html（离线）+ 另开终端 npm run serve 提供更新 API`);
  console.log(`  · Ctrl+C 停止`);
});
