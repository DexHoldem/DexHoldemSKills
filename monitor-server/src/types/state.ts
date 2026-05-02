export type LoopStage =
  | 'idle'
  | 'atom_idle'
  | 'acting'
  | 'to_recover'
  | 'down'
  | 'show_hand'
  | 'win'
  | 'lose';

export type Activity =
  | 'capturing'
  | 'perceiving'
  | 'reasoning'
  | 'acting'
  | 're-executing'
  | 'requesting_human'
  | 'idle';

export interface Step {
  name: string;
  status: 'pending' | 'dispatched' | 'done' | 'failed';
  description?: string;
}

export interface SafetyCounters {
  consecutive_waits: number;
  total_waits: number;
  consecutive_recoveries: number;
  total_recoveries: number;
  executor_failures: number;
  action_sequences_started: number;
  human_help_requests: number;
}

export interface ActionSequence {
  schema_version: number;
  sequence_id: string;
  loop_stage: LoopStage;
  intent: string;
  action: Record<string, unknown>;
  plan?: {
    prefix: string;
    commands: string[];
    command_steps: string[];
    sequence_steps: string[];
  };
  retry_count: number;
  last_error: string | null;
  human_required: boolean;
  updated_at: string;
  steps: Step[];
  current_step: string;
  safety_counters: SafetyCounters;
  current_action: string;
}

export interface ParsedState {
  loop_stage: LoopStage;
  robot: string;
  table: {
    scene_stable: boolean;
    is_my_turn: boolean;
    community_cards: string[];
    my_chips: Record<string, number>;
    opponent_chips: Record<string, number>;
    my_current_bet: Record<string, number>;
    opponent_bet: Record<string, number>;
  };
}

export interface StateSnapshot {
  stateNum: number;
  hasCapture: boolean;
  hasParsedState: boolean;
  hasAction: boolean;
  parsedState?: ParsedState;
  captureTime?: number;
}

export interface HumanHelpRequest {
  schema_version: number;
  requested_at: string;
  reason: string;
  resume_options: string[];
  context: Record<string, unknown>;
  state_name: string;
}

export interface ExperimentState {
  expId: string;
  expPath: string;
  currentStateNum: number;
  loopStage: LoopStage;
  activity: Activity;
  actionSequence: ActionSequence | null;
  humanHelpRequest: HumanHelpRequest | null;
  latestCapture: string | null;
  states: StateSnapshot[];
  lastModified: number;
}

export interface StageDisplay {
  stage: LoopStage;
  label: string;
  color: string;
}

export const STAGE_DISPLAY: Record<LoopStage, StageDisplay> = {
  idle: { stage: 'idle', label: 'Idle', color: '#5F8940' },
  atom_idle: { stage: 'atom_idle', label: 'Atom Idle', color: '#5F8940' },
  acting: { stage: 'acting', label: 'Acting', color: '#6C8EBF' },
  to_recover: { stage: 'to_recover', label: 'Recovering', color: '#FF7E79' },
  down: { stage: 'down', label: 'Down', color: '#B85450' },
  show_hand: { stage: 'show_hand', label: 'Show Hand', color: '#884ea0' },
  win: { stage: 'win', label: 'Win', color: '#5F8940' },
  lose: { stage: 'lose', label: 'Lose', color: '#B85450' },
};

export const ACTIVITY_DISPLAY: Record<Activity, { label: string; color: string }> = {
  capturing: { label: 'Capturing', color: '#6C8EBF' },
  perceiving: { label: 'Perceiving', color: '#884ea0' },
  reasoning: { label: 'Reasoning', color: '#FF7E79' },
  acting: { label: 'Acting', color: '#5F8940' },
  're-executing': { label: 'Re-executing', color: '#B85450' },
  requesting_human: { label: 'Requesting Human', color: '#B85450' },
  idle: { label: 'Idle', color: '#80461B' },
};
