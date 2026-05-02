import express from 'express';
import * as http from 'http';
import * as path from 'path';
import { WebSocketServer, WebSocket } from 'ws';
import { createApiRouter } from './routes/api';
import { ExperimentWatcher } from './services/watcher';
import { getExperimentState } from './services/parser';

const DEFAULT_PORT = 3000;
const DEFAULT_EXP_DIRS = ['./experiments', './bench/problems'];

function parseArgs(): { port: number; expDirs: string[] } {
  const args = process.argv.slice(2);
  let port = DEFAULT_PORT;
  const expDirs: string[] = [];

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--port' && args[i + 1]) {
      port = parseInt(args[++i], 10);
    } else if (args[i] === '--exp-dir' && args[i + 1]) {
      expDirs.push(path.resolve(args[++i]));
    }
  }

  if (expDirs.length === 0) {
    expDirs.push(...DEFAULT_EXP_DIRS.map((d) => path.resolve(d)));
  }

  return { port, expDirs };
}

function main(): void {
  const { port, expDirs } = parseArgs();

  const app = express();
  const server = http.createServer(app);
  const wss = new WebSocketServer({ server });

  app.use(express.static(path.join(__dirname, '../client')));
  app.use('/api', createApiRouter(expDirs));

  const clients = new Map<string, Set<WebSocket>>();
  const watcher = new ExperimentWatcher();

  watcher.on('change', (event) => {
    const expId = event.expId;
    const subs = clients.get(expId);
    if (!subs || subs.size === 0) return;

    let expPath: string | null = null;
    for (const dir of expDirs) {
      const candidate = path.join(dir, expId);
      try {
        const { existsSync } = require('fs');
        if (existsSync(candidate)) {
          expPath = candidate;
          break;
        }
      } catch {}
    }

    if (!expPath) return;

    const state = getExperimentState(expPath);
    if (!state) return;

    const message = JSON.stringify({ type: 'state', data: state });
    for (const client of subs) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    }
  });

  watcher.watch(expDirs);

  wss.on('connection', (ws, req) => {
    const url = new URL(req.url || '/', `http://localhost:${port}`);
    const expId = url.pathname.replace(/^\/ws\//, '').replace(/\/$/, '');

    if (!expId) {
      ws.close(1002, 'Missing experiment ID');
      return;
    }

    if (!clients.has(expId)) {
      clients.set(expId, new Set());
    }
    clients.get(expId)!.add(ws);

    ws.on('close', () => {
      const subs = clients.get(expId);
      if (subs) {
        subs.delete(ws);
        if (subs.size === 0) {
          clients.delete(expId);
        }
      }
    });

    ws.on('message', (data) => {
      try {
        const msg = JSON.parse(data.toString());
        if (msg.type === 'ping') {
          ws.send(JSON.stringify({ type: 'pong' }));
        }
      } catch {}
    });
  });

  server.listen(port, () => {
    console.log(`Monitor server running at http://localhost:${port}`);
    console.log(`Watching experiment directories:`);
    for (const dir of expDirs) {
      console.log(`  - ${dir}`);
    }
  });

  process.on('SIGINT', () => {
    console.log('\nShutting down...');
    watcher.close();
    wss.close();
    server.close();
    process.exit(0);
  });
}

main();
