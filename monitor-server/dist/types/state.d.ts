export type LoopStage = 'idle' | 'atom_idle' | 'acting' | 'to_recover' | 'down' | 'show_hand' | 'win' | 'lose';
export type Activity = 'capturing' | 'perceiving' | 'reasoning' | 'acting' | 're-executing' | 'requesting_human' | 'idle';
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
export declare const STAGE_DISPLAY: Record<LoopStage, StageDisplay>;
export declare const ACTIVITY_DISPLAY: Record<Activity, {
    label: string;
    color: string;
}>;
