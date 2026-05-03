import express from 'express';
import * as http from 'http';
import * as path from 'path';
import { WebSocketServer, WebSocket } from 'ws';
import { createApiRouter } from './routes/api';
import { ExperimentWatcher } from './services/watcher';
import { getExperimentState } from './services/parser';

const DEFAULT_EXP_DIRS = ['../experiments', '../bench/problems'];

let server: http.Server | null = null;
let watcher: ExperimentWatcher | null = null;

export async function startServer(port: number, expDirs: string[]): Promise<void> {
  if (expDirs.length === 0) {
    expDirs = DEFAULT_EXP_DIRS.map((d) => path.resolve(d));
  } else {
    expDirs = expDirs.map((d) => path.resolve(d));
  }

  const app = express();
  server = http.createServer(app);
  const wss = new WebSocketServer({ server });

  app.use(express.static(path.join(__dirname, '../renderer')));
  app.use('/api', createApiRouter(expDirs));

  const clients = new Map<string, Set<WebSocket>>();
  watcher = new ExperimentWatcher();

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
        if (subs.size === 0) clients.delete(expId);
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

  return new Promise((resolve) => {
    server!.listen(port, () => {
      console.log(`Monitor server running at http://localhost:${port}`);
      console.log(`Watching experiment directories:`);
      for (const dir of expDirs) {
        console.log(`  - ${dir}`);
      }
      resolve();
    });
  });
}

export function stopServer(): void {
  if (watcher) {
    watcher.close();
    watcher = null;
  }
  if (server) {
    server.close();
    server = null;
  }
}
