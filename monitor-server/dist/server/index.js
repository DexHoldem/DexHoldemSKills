"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const http = __importStar(require("http"));
const path = __importStar(require("path"));
const ws_1 = require("ws");
const api_1 = require("./routes/api");
const watcher_1 = require("./services/watcher");
const parser_1 = require("./services/parser");
const DEFAULT_PORT = 3000;
const DEFAULT_EXP_DIRS = ['./experiments', './bench/problems'];
function parseArgs() {
    const args = process.argv.slice(2);
    let port = DEFAULT_PORT;
    const expDirs = [];
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--port' && args[i + 1]) {
            port = parseInt(args[++i], 10);
        }
        else if (args[i] === '--exp-dir' && args[i + 1]) {
            expDirs.push(path.resolve(args[++i]));
        }
    }
    if (expDirs.length === 0) {
        expDirs.push(...DEFAULT_EXP_DIRS.map((d) => path.resolve(d)));
    }
    return { port, expDirs };
}
function main() {
    const { port, expDirs } = parseArgs();
    const app = (0, express_1.default)();
    const server = http.createServer(app);
    const wss = new ws_1.WebSocketServer({ server });
    app.use(express_1.default.static(path.join(__dirname, '../client')));
    app.use('/api', (0, api_1.createApiRouter)(expDirs));
    const clients = new Map();
    const watcher = new watcher_1.ExperimentWatcher();
    watcher.on('change', (event) => {
        const expId = event.expId;
        const subs = clients.get(expId);
        if (!subs || subs.size === 0)
            return;
        let expPath = null;
        for (const dir of expDirs) {
            const candidate = path.join(dir, expId);
            try {
                const { existsSync } = require('fs');
                if (existsSync(candidate)) {
                    expPath = candidate;
                    break;
                }
            }
            catch { }
        }
        if (!expPath)
            return;
        const state = (0, parser_1.getExperimentState)(expPath);
        if (!state)
            return;
        const message = JSON.stringify({ type: 'state', data: state });
        for (const client of subs) {
            if (client.readyState === ws_1.WebSocket.OPEN) {
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
        clients.get(expId).add(ws);
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
            }
            catch { }
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
