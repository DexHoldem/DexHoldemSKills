import { ActionSequence, ParsedState, LoopStage, Activity, ExperimentState, HumanHelpRequest } from '../../types/state';
export declare function parseActionSequence(filePath: string): ActionSequence | null;
export declare function parseParsedState(filePath: string): ParsedState | null;
export declare function parseHumanHelpCache(expDir: string): HumanHelpRequest | null;
export declare function humanHelpRequested(expDir: string): boolean;
export declare function inferActivity(stateDir: string, loopStage: LoopStage | null, expDir?: string): Activity;
export declare function getStateFolders(expDir: string): string[];
export declare function getExperimentState(expDir: string): ExperimentState | null;
export declare function findExperiments(rootDir: string): string[];
