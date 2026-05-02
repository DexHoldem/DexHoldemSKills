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
exports.parseActionSequence = parseActionSequence;
exports.parseParsedState = parseParsedState;
exports.parseHumanHelpCache = parseHumanHelpCache;
exports.humanHelpRequested = humanHelpRequested;
exports.inferActivity = inferActivity;
exports.getStateFolders = getStateFolders;
exports.getExperimentState = getExperimentState;
exports.findExperiments = findExperiments;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const HUMAN_HELP_CACHE_FILE = 'human_help_request.json';
function parseActionSequence(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        return JSON.parse(content);
    }
    catch {
        return null;
    }
}
function parseParsedState(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const jsonMatch = content.match(/```json\s*([\s\S]*?)```/);
        if (jsonMatch && jsonMatch[1]) {
            return JSON.parse(jsonMatch[1].trim());
        }
        return null;
    }
    catch {
        return null;
    }
}
function parseHumanHelpCache(expDir) {
    try {
        const cachePath = path.join(expDir, HUMAN_HELP_CACHE_FILE);
        if (!fs.existsSync(cachePath))
            return null;
        const content = fs.readFileSync(cachePath, 'utf-8');
        return JSON.parse(content);
    }
    catch {
        return null;
    }
}
function humanHelpRequested(expDir) {
    return fs.existsSync(path.join(expDir, HUMAN_HELP_CACHE_FILE));
}
function inferActivity(stateDir, loopStage, expDir) {
    if (expDir && humanHelpRequested(expDir)) {
        return 'requesting_human';
    }
    const hasCapture = fs.existsSync(path.join(stateDir, '00_capture.jpg'));
    const hasParsed = fs.existsSync(path.join(stateDir, '01_parsed_state.md'));
    if (!hasCapture)
        return 'capturing';
    if (!hasParsed)
        return 'perceiving';
    if (loopStage === 'to_recover')
        return 're-executing';
    if (loopStage === 'acting')
        return 'acting';
    if (loopStage === 'idle' || loopStage === 'atom_idle')
        return 'reasoning';
    return 'idle';
}
function getStateFolders(expDir) {
    try {
        const entries = fs.readdirSync(expDir, { withFileTypes: true });
        return entries
            .filter((e) => e.isDirectory() && /^s\d+$/.test(e.name))
            .map((e) => e.name)
            .sort((a, b) => parseInt(a.slice(1)) - parseInt(b.slice(1)));
    }
    catch {
        return [];
    }
}
function getExperimentState(expDir) {
    const expId = path.basename(expDir);
    const actionSeqPath = path.join(expDir, 'action_sequence.json');
    const actionSequence = fs.existsSync(actionSeqPath)
        ? parseActionSequence(actionSeqPath)
        : null;
    const stateFolders = getStateFolders(expDir);
    if (stateFolders.length === 0 && !actionSequence) {
        return null;
    }
    const states = stateFolders.map((folder) => {
        const stateNum = parseInt(folder.slice(1));
        const stateDir = path.join(expDir, folder);
        const capturePath = path.join(stateDir, '00_capture.jpg');
        const parsedPath = path.join(stateDir, '01_parsed_state.md');
        const actionPath = path.join(stateDir, '02_action.md');
        const hasCapture = fs.existsSync(capturePath);
        const hasParsedState = fs.existsSync(parsedPath);
        const hasAction = fs.existsSync(actionPath);
        let captureTime;
        if (hasCapture) {
            try {
                captureTime = fs.statSync(capturePath).mtimeMs;
            }
            catch { }
        }
        let parsedState;
        if (hasParsedState) {
            const parsed = parseParsedState(parsedPath);
            if (parsed)
                parsedState = parsed;
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
    const loopStage = actionSequence?.loop_stage ?? 'idle';
    const humanHelpRequest = parseHumanHelpCache(expDir);
    const activity = fs.existsSync(currentStateDir)
        ? inferActivity(currentStateDir, loopStage, expDir)
        : humanHelpRequested(expDir)
            ? 'requesting_human'
            : 'idle';
    let latestCapture = null;
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
        }
        catch { }
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
function findExperiments(rootDir) {
    const experiments = [];
    try {
        const entries = fs.readdirSync(rootDir, { withFileTypes: true });
        for (const entry of entries) {
            if (!entry.isDirectory())
                continue;
            const fullPath = path.join(rootDir, entry.name);
            if (fs.existsSync(path.join(fullPath, 'action_sequence.json')) ||
                getStateFolders(fullPath).length > 0) {
                experiments.push(fullPath);
            }
        }
    }
    catch { }
    return experiments;
}
