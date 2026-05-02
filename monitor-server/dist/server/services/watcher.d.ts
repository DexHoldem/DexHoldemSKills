import { EventEmitter } from 'events';
export interface WatchEvent {
    type: 'add' | 'change' | 'unlink';
    path: string;
    expId: string;
}
export declare class ExperimentWatcher extends EventEmitter {
    private watcher;
    private debounceTimers;
    private debounceMs;
    watch(expDirs: string[]): void;
    private handleEvent;
    private extractExpId;
    close(): void;
}
