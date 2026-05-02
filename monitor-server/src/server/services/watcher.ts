import * as chokidar from 'chokidar';
import * as path from 'path';
import { EventEmitter } from 'events';

export interface WatchEvent {
  type: 'add' | 'change' | 'unlink';
  path: string;
  expId: string;
}

const EXP_ROOT_FILES = new Set([
  'action_sequence.json',
  'human_help_request.json',
  'hole_card_cache.json',
]);

export class ExperimentWatcher extends EventEmitter {
  private watcher: chokidar.FSWatcher | null = null;
  private debounceTimers: Map<string, NodeJS.Timeout> = new Map();
  private debounceMs = 100;

  watch(expDirs: string[]): void {
    if (this.watcher) {
      this.watcher.close();
    }

    const patterns = expDirs.flatMap((dir) => [
      path.join(dir, '*/action_sequence.json'),
      path.join(dir, '*/human_help_request.json'),
      path.join(dir, '*/hole_card_cache.json'),
      path.join(dir, '*/s*/00_capture.jpg'),
      path.join(dir, '*/s*/01_parsed_state.md'),
      path.join(dir, '*/s*/02_action.md'),
      path.join(dir, 'action_sequence.json'),
      path.join(dir, 'human_help_request.json'),
      path.join(dir, 'hole_card_cache.json'),
      path.join(dir, 's*/00_capture.jpg'),
      path.join(dir, 's*/01_parsed_state.md'),
      path.join(dir, 's*/02_action.md'),
    ]);

    console.log('Watching patterns:', patterns.slice(0, 6).join(', '), '...');

    this.watcher = chokidar.watch(patterns, {
      persistent: true,
      ignoreInitial: true,
      usePolling: process.env.CHOKIDAR_USEPOLLING === 'true',
      awaitWriteFinish: {
        stabilityThreshold: 200,
        pollInterval: 100,
      },
    });

    this.watcher.on('add', (filePath) => this.handleEvent('add', filePath));
    this.watcher.on('change', (filePath) => this.handleEvent('change', filePath));
    this.watcher.on('unlink', (filePath) => this.handleEvent('unlink', filePath));
    this.watcher.on('error', (error) => console.error('Watcher error:', error));
    this.watcher.on('ready', () => console.log('Watcher ready'));
  }

  private handleEvent(type: 'add' | 'change' | 'unlink', filePath: string): void {
    const expId = this.extractExpId(filePath);
    if (!expId) {
      console.log(`[watcher] Could not extract expId from: ${filePath}`);
      return;
    }

    console.log(`[watcher] ${type}: ${path.basename(filePath)} in ${expId}`);

    const key = expId;
    const existing = this.debounceTimers.get(key);
    if (existing) {
      clearTimeout(existing);
    }

    const timer = setTimeout(() => {
      this.debounceTimers.delete(key);
      const event: WatchEvent = { type, path: filePath, expId };
      this.emit('change', event);
    }, this.debounceMs);

    this.debounceTimers.set(key, timer);
  }

  private extractExpId(filePath: string): string | null {
    const parts = filePath.split(path.sep);
    for (let i = parts.length - 1; i >= 0; i--) {
      if (parts[i].startsWith('s') && /^s\d+$/.test(parts[i])) {
        return parts[i - 1] || null;
      }
      if (EXP_ROOT_FILES.has(parts[i])) {
        return parts[i - 1] || null;
      }
    }
    return null;
  }

  close(): void {
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
