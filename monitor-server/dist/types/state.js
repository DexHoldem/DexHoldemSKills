"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ACTIVITY_DISPLAY = exports.STAGE_DISPLAY = void 0;
exports.STAGE_DISPLAY = {
    idle: { stage: 'idle', label: 'Idle', color: '#5F8940' },
    atom_idle: { stage: 'atom_idle', label: 'Atom Idle', color: '#5F8940' },
    acting: { stage: 'acting', label: 'Acting', color: '#6C8EBF' },
    to_recover: { stage: 'to_recover', label: 'Recovering', color: '#FF7E79' },
    down: { stage: 'down', label: 'Down', color: '#B85450' },
    show_hand: { stage: 'show_hand', label: 'Show Hand', color: '#884ea0' },
    win: { stage: 'win', label: 'Win', color: '#5F8940' },
    lose: { stage: 'lose', label: 'Lose', color: '#B85450' },
};
exports.ACTIVITY_DISPLAY = {
    capturing: { label: 'Capturing', color: '#6C8EBF' },
    perceiving: { label: 'Perceiving', color: '#884ea0' },
    reasoning: { label: 'Reasoning', color: '#FF7E79' },
    acting: { label: 'Acting', color: '#5F8940' },
    're-executing': { label: 'Re-executing', color: '#B85450' },
    requesting_human: { label: 'Requesting Human', color: '#B85450' },
    idle: { label: 'Idle', color: '#80461B' },
};
