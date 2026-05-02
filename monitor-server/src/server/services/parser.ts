import * as fs from 'fs';
import * as path from 'path';
import {
  ActionSequence,
  ParsedState,
  LoopStage,
  Activity,
  ExperimentState,
  StateSnapshot,
  HumanHelpRequest,
} from '../../types/state';

const HUMAN_HELP_CACHE_FILE = 'human_help_request.json';

export function parseActionSequence(filePath: string): ActionSequence | null {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(content) as ActionSequence;
  } catch {
    return null;
  }
}

export function parseParsedState(filePath: string): ParsedState | null {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const jsonMatch = content.match(/```json\s*([\s\S]*?)```/);
    if (jsonMatch && jsonMatch[1]) {
      return JSON.parse(jsonMatch[1].trim()) as ParsedState;
    }
    return null;
  } catch {
    return null;
  }
}

export function parseHumanHelpCache(expDir: string): HumanHelpRequest | null {
  try {
    const cachePath = path.join(expDir, HUMAN_HELP_CACHE_FILE);
    if (!fs.existsSync(cachePath)) return null;
    const content = fs.readFileSync(cachePath, 'utf-8');
    return JSON.parse(content) as HumanHelpRequest;
  } catch {
    return null;
  }
}

export function humanHelpRequested(expDir: string): boolean {
  return fs.existsSync(path.join(expDir, HUMAN_HELP_CACHE_FILE));
}

export function inferActivity(
  stateDir: string,
  loopStage: LoopStage | null,
  expDir?: string
): Activity {
  if (expDir && humanHelpRequested(expDir)) {
    return 'requesting_human';
  }

  const hasCapture = fs.existsSync(path.join(stateDir, '00_capture.jpg'));
  const hasParsed = fs.existsSync(path.join(stateDir, '01_parsed_state.md'));

  if (!hasCapture) return 'capturing';
  if (!hasParsed) return 'perceiving';
  if (loopStage === 'to_recover') return 're-executing';
  if (loopStage === 'acting') return 'acting';
  if (loopStage === 'idle' || loopStage === 'atom_idle') return 'reasoning';
  return 'idle';
}

export function getStateFolders(expDir: string): string[] {
  try {
    const entries = fs.readdirSync(expDir, { withFileTypes: true });
    return entries
      .filter((e) => e.isDirectory() && /^s\d+$/.test(e.name))
      .map((e) => e.name)
      .sort((a, b) => parseInt(a.slice(1)) - parseInt(b.slice(1)));
  } catch {
    return [];
  }
}

export function getExperimentState(expDir: string): ExperimentState | null {
  const expId = path.basename(expDir);

  const actionSeqPath = path.join(expDir, 'action_sequence.json');
  const actionSequence = fs.existsSync(actionSeqPath)
    ? parseActionSequence(actionSeqPath)
    : null;

  const stateFolders = getStateFolders(expDir);
  if (stateFolders.length === 0 && !actionSequence) {
    return null;
  }

  const states: StateSnapshot[] = stateFolders.map((folder) => {
    const stateNum = parseInt(folder.slice(1));
    const stateDir = path.join(expDir, folder);
    const capturePath = path.join(stateDir, '00_capture.jpg');
    const parsedPath = path.join(stateDir, '01_parsed_state.md');
    const actionPath = path.join(stateDir, '02_action.md');

    const hasCapture = fs.existsSync(capturePath);
    const hasParsedState = fs.existsSync(parsedPath);
    const hasAction = fs.existsSync(actionPath);

    let captureTime: number | undefined;
    if (hasCapture) {
      try {
        captureTime = fs.statSync(capturePath).mtimeMs;
      } catch {}
    }

    let parsedState: ParsedState | undefined;
    if (hasParsedState) {
      const parsed = parseParsedState(parsedPath);
      if (parsed) parsedState = parsed;
    }

    return {
      stateNum,
      hasCapture,
      hasParsedState,
      hasAction,
      parsedState,
      captureTime,
    };
  });

  const currentStateNum = states.length > 0 ? states[states.length - 1].stateNum : 0;
  const currentStateDir = path.join(expDir, `s${currentStateNum}`);
  const loopStage: LoopStage = actionSequence?.loop_stage ?? 'idle';
  const humanHelpRequest = parseHumanHelpCache(expDir);
  const activity = fs.existsSync(currentStateDir)
    ? inferActivity(currentStateDir, loopStage, expDir)
    : humanHelpRequested(expDir)
      ? 'requesting_human'
      : 'idle';

  let latestCapture: string | null = null;
  for (let i = states.length - 1; i >= 0; i--) {
    if (states[i].hasCapture) {
      latestCapture = path.join(expDir, `s${states[i].stateNum}`, '00_capture.jpg');
      break;
    }
  }

  let lastModified = 0;
  if (fs.existsSync(actionSeqPath)) {
    try {
      lastModified = fs.statSync(actionSeqPath).mtimeMs;
    } catch {}
  }

  return {
    expId,
    expPath: expDir,
    currentStateNum,
    loopStage,
    activity,
    actionSequence,
    humanHelpRequest,
    latestCapture,
    states,
    lastModified,
  };
}

export function findExperiments(rootDir: string): string[] {
  const experiments: string[] = [];

  try {
    const entries = fs.readdirSync(rootDir, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const fullPath = path.join(rootDir, entry.name);

      if (
        fs.existsSync(path.join(fullPath, 'action_sequence.json')) ||
        getStateFolders(fullPath).length > 0
      ) {
        experiments.push(fullPath);
      }
    }
  } catch {}

  return experiments;
}
