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
exports.createApiRouter = createApiRouter;
const express_1 = require("express");
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const parser_1 = require("../services/parser");
function createApiRouter(expDirs) {
    const router = (0, express_1.Router)();
    router.get('/experiments', (_req, res) => {
        const experiments = [];
        for (const dir of expDirs) {
            const found = (0, parser_1.findExperiments)(dir);
            for (const expPath of found) {
                const state = (0, parser_1.getExperimentState)(expPath);
                if (state) {
                    experiments.push({
                        id: state.expId,
                        path: expPath,
                        lastModified: state.lastModified,
                    });
                }
            }
            const rootState = (0, parser_1.getExperimentState)(dir);
            if (rootState && rootState.states.length > 0) {
                experiments.push({
                    id: rootState.expId,
                    path: dir,
                    lastModified: rootState.lastModified,
                });
            }
        }
        const seen = new Set();
        const unique = experiments.filter((e) => {
            if (seen.has(e.path))
                return false;
            seen.add(e.path);
            return true;
        });
        res.json({ experiments: unique.sort((a, b) => b.lastModified - a.lastModified) });
    });
    router.get('/experiments/:id/state', (req, res) => {
        const { id } = req.params;
        const expPath = req.query.path;
        let targetPath = null;
        if (expPath) {
            targetPath = expPath;
        }
        else {
            for (const dir of expDirs) {
                const candidate = path.join(dir, id);
                if (fs.existsSync(candidate)) {
                    targetPath = candidate;
                    break;
                }
                const found = (0, parser_1.findExperiments)(dir);
                for (const p of found) {
                    if (path.basename(p) === id) {
                        targetPath = p;
                        break;
                    }
                }
                if (targetPath)
                    break;
            }
        }
        if (!targetPath || !fs.existsSync(targetPath)) {
            res.status(404).json({ error: 'Experiment not found' });
            return;
        }
        const state = (0, parser_1.getExperimentState)(targetPath);
        if (!state) {
            res.status(404).json({ error: 'No state data found' });
            return;
        }
        res.json(state);
    });
    router.get('/experiments/:id/capture/:stateNum', (req, res) => {
        const { id, stateNum } = req.params;
        const expPath = req.query.path;
        let targetPath = null;
        if (expPath) {
            targetPath = expPath;
        }
        else {
            for (const dir of expDirs) {
                const candidate = path.join(dir, id);
                if (fs.existsSync(candidate)) {
                    targetPath = candidate;
                    break;
                }
            }
        }
        if (!targetPath) {
            res.status(404).json({ error: 'Experiment not found' });
            return;
        }
        const capturePath = path.join(targetPath, `s${stateNum}`, '00_capture.jpg');
        if (!fs.existsSync(capturePath)) {
            res.status(404).json({ error: 'Capture not found' });
            return;
        }
        res.sendFile(capturePath);
    });
    return router;
}
