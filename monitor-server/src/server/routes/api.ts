import { Router, Request, Response } from 'express';
import * as path from 'path';
import * as fs from 'fs';
import { getExperimentState, findExperiments } from '../services/parser';

export function createApiRouter(expDirs: string[]): Router {
  const router = Router();

  router.get('/experiments', (_req: Request, res: Response) => {
    const experiments: Array<{ id: string; path: string; lastModified: number }> = [];

    for (const dir of expDirs) {
      const found = findExperiments(dir);
      for (const expPath of found) {
        const state = getExperimentState(expPath);
        if (state) {
          experiments.push({
            id: state.expId,
            path: expPath,
            lastModified: state.lastModified,
          });
        }
      }

      const rootState = getExperimentState(dir);
      if (rootState && rootState.states.length > 0) {
        experiments.push({
          id: rootState.expId,
          path: dir,
          lastModified: rootState.lastModified,
        });
      }
    }

    const seen = new Set<string>();
    const unique = experiments.filter((e) => {
      if (seen.has(e.path)) return false;
      seen.add(e.path);
      return true;
    });

    res.json({ experiments: unique.sort((a, b) => b.lastModified - a.lastModified) });
  });

  router.get('/experiments/:id/state', (req: Request, res: Response) => {
    const { id } = req.params;
    const expPath = req.query.path as string | undefined;

    let targetPath: string | null = null;

    if (expPath) {
      targetPath = expPath;
    } else {
      for (const dir of expDirs) {
        const candidate = path.join(dir, id);
        if (fs.existsSync(candidate)) {
          targetPath = candidate;
          break;
        }
        const found = findExperiments(dir);
        for (const p of found) {
          if (path.basename(p) === id) {
            targetPath = p;
            break;
          }
        }
        if (targetPath) break;
      }
    }

    if (!targetPath || !fs.existsSync(targetPath)) {
      res.status(404).json({ error: 'Experiment not found' });
      return;
    }

    const state = getExperimentState(targetPath);
    if (!state) {
      res.status(404).json({ error: 'No state data found' });
      return;
    }

    res.json(state);
  });

  router.get('/experiments/:id/capture/:stateNum', (req: Request, res: Response) => {
    const { id, stateNum } = req.params;
    const expPath = req.query.path as string | undefined;

    let targetPath: string | null = null;

    if (expPath) {
      targetPath = expPath;
    } else {
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
