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
Object.defineProperty(exports, "__esModule", { value: true });
exports.ExperimentWatcher = void 0;
const chokidar = __importStar(require("chokidar"));
const path = __importStar(require("path"));
const events_1 = require("events");
class ExperimentWatcher extends events_1.EventEmitter {
    constructor() {
        super(...arguments);
        this.watcher = null;
        this.debounceTimers = new Map();
        this.debounceMs = 100;
    }
    watch(expDirs) {
        if (this.watcher) {
            this.watcher.close();
        }
        const patterns = expDirs.flatMap((dir) => [
            path.join(dir, '*/action_sequence.json'),
            path.join(dir, '*/human_help_request.json'),
            path.join(dir, '*/s*/00_capture.jpg'),
            path.join(dir, '*/s*/01_parsed_state.md'),
            path.join(dir, '*/s*/02_action.md'),
            path.join(dir, 'action_sequence.json'),
            path.join(dir, 'human_help_request.json'),
            path.join(dir, 's*/00_capture.jpg'),
            path.join(dir, 's*/01_parsed_state.md'),
            path.join(dir, 's*/02_action.md'),
        ]);
        this.watcher = chokidar.watch(patterns, {
            persistent: true,
            ignoreInitial: true,
            awaitWriteFinish: {
                stabilityThreshold: 100,
                pollInterval: 50,
            },
        });
        this.watcher.on('add', (filePath) => this.handleEvent('add', filePath));
        this.watcher.on('change', (filePath) => this.handleEvent('change', filePath));
        this.watcher.on('unlink', (filePath) => this.handleEvent('unlink', filePath));
    }
    handleEvent(type, filePath) {
        const expId = this.extractExpId(filePath);
        if (!expId)
            return;
        const key = `${expId}:${type}`;
        const existing = this.debounceTimers.get(key);
        if (existing) {
            clearTimeout(existing);
        }
        const timer = setTimeout(() => {
            this.debounceTimers.delete(key);
            const event = { type, path: filePath, expId };
            this.emit('change', event);
        }, this.debounceMs);
        this.debounceTimers.set(key, timer);
    }
    extractExpId(filePath) {
        const parts = filePath.split(path.sep);
        for (let i = parts.length - 1; i >= 0; i--) {
            if (parts[i].startsWith('s') && /^s\d+$/.test(parts[i])) {
                return parts[i - 1] || null;
            }
            if (parts[i] === 'action_sequence.json') {
                return parts[i - 1] || null;
            }
        }
        return null;
    }
    close() {
        if (this.watcher) {
            this.watcher.close();
            this.watcher = null;
        }
        for (const timer of this.debounceTimers.values()) {
            clearTimeout(timer);
        }
        this.debounceTimers.clear();
    }
}
exports.ExperimentWatcher = ExperimentWatcher;
