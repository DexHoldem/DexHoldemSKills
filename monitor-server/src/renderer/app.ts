interface Step {
  name: string;
  status: 'pending' | 'dispatched' | 'done' | 'failed';
}

interface SafetyCounters {
  consecutive_waits: number;
  total_waits: number;
  consecutive_recoveries: number;
  total_recoveries: number;
  executor_failures: number;
  human_help_requests: number;
}

interface ActionSequence {
  loop_stage: string;
  intent: string;
  steps: Step[];
  current_step: string;
  safety_counters: SafetyCounters;
  human_required: boolean;
  last_error: string | null;
}

interface ParsedState {
  loop_stage: string;
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

interface StateSnapshot {
  stateNum: number;
  hasCapture: boolean;
  hasParsedState: boolean;
  parsedState?: ParsedState;
}

interface HumanHelpRequest {
  schema_version: number;
  requested_at: string;
  reason: string;
  resume_options: string[];
  context: Record<string, unknown>;
  state_name: string;
}

interface ExperimentState {
  expId: string;
  expPath: string;
  currentStateNum: number;
  loopStage: string;
  activity: string;
  actionSequence: ActionSequence | null;
  humanHelpRequest: HumanHelpRequest | null;
  latestCapture: string | null;
  states: StateSnapshot[];
  lastModified: number;
}

interface Experiment {
  id: string;
  path: string;
  lastModified: number;
}

class MonitorApp {
  private ws: WebSocket | null = null;
  private currentExpId: string | null = null;
  private currentExpPath: string | null = null;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  private pingInterval: ReturnType<typeof setInterval> | null = null;
  private pollInterval: ReturnType<typeof setInterval> | null = null;
  private lastStateJson: string = '';

  constructor() {
    this.init();
  }

  private async init(): Promise<void> {
    await this.loadExperiments();

    document.getElementById('experiment-select')?.addEventListener('change', (e) => {
      const select = e.target as HTMLSelectElement;
      const option = select.selectedOptions[0];
      if (option && option.value) {
        this.selectExperiment(option.value, option.dataset.path || '');
      }
    });

    document.getElementById('refresh-btn')?.addEventListener('click', () => {
      this.loadExperiments();
    });

    setInterval(() => this.loadExperiments(), 10000);
  }

  private async loadExperiments(): Promise<void> {
    try {
      const res = await fetch('/api/experiments');
      const data = await res.json();
      const select = document.getElementById('experiment-select') as HTMLSelectElement;

      const currentValue = select.value;
      select.innerHTML = '<option value="">Select experiment...</option>';

      for (const exp of data.experiments as Experiment[]) {
        const option = document.createElement('option');
        option.value = exp.id;
        option.dataset.path = exp.path;
        option.textContent = exp.id;
        select.appendChild(option);
      }

      if (currentValue) {
        select.value = currentValue;
      }

      if (!select.value && data.experiments.length > 0) {
        const first = data.experiments[0] as Experiment;
        select.value = first.id;
        this.selectExperiment(first.id, first.path);
      }
    } catch (err) {
      console.error('Failed to load experiments:', err);
    }
  }

  private async selectExperiment(expId: string, expPath: string): Promise<void> {
    this.currentExpId = expId;
    this.currentExpPath = expPath;

    await this.loadState();
    this.connectWebSocket();
    this.startPolling();
  }

  private async loadState(): Promise<void> {
    if (!this.currentExpId) return;

    try {
      const url = `/api/experiments/${this.currentExpId}/state?path=${encodeURIComponent(this.currentExpPath || '')}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to load state');
      const state = await res.json() as ExperimentState;
      this.updateUI(state);
    } catch (err) {
      console.error('Failed to load state:', err);
    }
  }

  private startPolling(): void {
    if (this.pollInterval) clearInterval(this.pollInterval);
    this.pollInterval = setInterval(() => this.loadState(), 2000);
  }

  private connectWebSocket(): void {
    if (this.ws) {
      this.ws.close();
    }
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${this.currentExpId}`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      this.setConnectionStatus(true);
      this.pingInterval = setInterval(() => {
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 15000);
    };

    this.ws.onclose = () => {
      this.setConnectionStatus(false);
      if (this.pingInterval) {
        clearInterval(this.pingInterval);
        this.pingInterval = null;
      }
      this.reconnectTimeout = setTimeout(() => {
        if (this.currentExpId) {
          this.connectWebSocket();
        }
      }, 1500);
    };

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'state') {
          const stateJson = JSON.stringify(msg.data);
          if (stateJson !== this.lastStateJson) {
            this.lastStateJson = stateJson;
            this.updateUI(msg.data as ExperimentState);
          }
        }
      } catch (err) {
        console.error('Failed to parse message:', err);
      }
    };
  }

  private setConnectionStatus(connected: boolean): void {
    const el = document.getElementById('connection-status');
    if (el) {
      el.textContent = connected ? 'Live' : 'Reconnecting...';
      el.classList.toggle('connected', connected);
    }
  }

  private updateUI(state: ExperimentState): void {
    this.updateLoopStage(state.loopStage);
    this.updateActivity(state.activity);
    this.updateActionSequence(state.actionSequence);
    this.updateSafetyCounters(state.actionSequence?.safety_counters || null);
    this.updateHumanHelp(state.humanHelpRequest);
    this.updateStateInfo(state);
    this.updateCapture(state);
    this.updateTableState(state);
  }

  private updateLoopStage(stage: string): void {
    const badge = document.querySelector('.stage-badge');
    if (badge) {
      badge.textContent = stage.replace(/_/g, ' ');
      badge.className = `stage-badge ${stage}`;
    }
  }

  private updateActivity(activity: string): void {
    const items = document.querySelectorAll('.activity-list li');
    items.forEach((item) => {
      const el = item as HTMLElement;
      const act = el.dataset.activity;
      el.classList.toggle('active', act === activity);
    });
  }

  private updateActionSequence(seq: ActionSequence | null): void {
    const intentEl = document.getElementById('current-intent');
    const stepLabel = document.getElementById('step-label');
    const progressFill = document.getElementById('step-progress');

    if (!seq) {
      if (intentEl) intentEl.textContent = '—';
      if (stepLabel) stepLabel.textContent = 'Step: —';
      if (progressFill) progressFill.style.width = '0%';
      return;
    }

    if (intentEl) intentEl.textContent = seq.intent || '—';

    const steps = seq.steps || [];
    const currentIdx = steps.findIndex((s) => s.name === seq.current_step);
    const doneCount = steps.filter((s) => s.status === 'done').length;

    if (stepLabel) {
      stepLabel.textContent = `Step: ${currentIdx + 1} / ${steps.length}`;
    }

    if (progressFill && steps.length > 0) {
      const pct = (doneCount / steps.length) * 100;
      progressFill.style.width = `${pct}%`;
    }

    const errorEl = document.getElementById('error-display');
    if (errorEl) {
      if (seq.last_error) {
        errorEl.textContent = seq.last_error;
        errorEl.classList.add('visible');
      } else {
        errorEl.classList.remove('visible');
      }
    }

    const humanEl = document.getElementById('human-required');
    if (humanEl) {
      humanEl.style.display = seq.human_required ? 'block' : 'none';
    }
  }

  private updateSafetyCounters(counters: SafetyCounters | null): void {
    const waitsEl = document.getElementById('waits-count');
    const recoveriesEl = document.getElementById('recoveries-count');
    const failuresEl = document.getElementById('failures-count');
    const humanHelpEl = document.getElementById('human-help-count');

    if (waitsEl) waitsEl.textContent = String(counters?.total_waits || 0);
    if (recoveriesEl) recoveriesEl.textContent = String(counters?.total_recoveries || 0);
    if (failuresEl) failuresEl.textContent = String(counters?.executor_failures || 0);
    if (humanHelpEl) humanHelpEl.textContent = String(counters?.human_help_requests || 0);
  }

  private updateHumanHelp(request: HumanHelpRequest | null): void {
    const panel = document.getElementById('human-help-panel');
    const reasonEl = document.getElementById('help-reason');
    const optionsEl = document.getElementById('help-options');
    const timeEl = document.getElementById('help-time');

    if (!panel) return;

    if (!request) {
      panel.style.display = 'none';
      return;
    }

    panel.style.display = 'block';

    if (reasonEl) {
      reasonEl.textContent = request.reason;
    }

    if (optionsEl) {
      optionsEl.innerHTML = request.resume_options
        .map((opt) => `<span class="option-tag">${opt}</span>`)
        .join('');
    }

    if (timeEl) {
      const date = new Date(request.requested_at);
      timeEl.textContent = `Requested at ${date.toLocaleTimeString()} (state: ${request.state_name})`;
    }
  }

  private updateStateInfo(state: ExperimentState): void {
    const currentEl = document.getElementById('current-state-num');
    const totalEl = document.getElementById('total-states');
    const updatedEl = document.getElementById('last-updated');

    if (currentEl) currentEl.textContent = `s${state.currentStateNum}`;
    if (totalEl) totalEl.textContent = String(state.states.length);

    if (updatedEl && state.lastModified) {
      const date = new Date(state.lastModified);
      updatedEl.textContent = date.toLocaleTimeString();
    }
  }

  private updateCapture(state: ExperimentState): void {
    const wrapper = document.getElementById('capture-wrapper');
    if (!wrapper) return;

    if (state.latestCapture && state.currentStateNum >= 0) {
      const imgUrl = `/api/experiments/${state.expId}/capture/${state.currentStateNum}?path=${encodeURIComponent(state.expPath)}&t=${Date.now()}`;
      const existingImg = wrapper.querySelector('img');
      if (existingImg) {
        existingImg.src = imgUrl;
      } else {
        wrapper.innerHTML = `<img src="${imgUrl}" alt="Latest capture" />`;
      }
    } else {
      wrapper.innerHTML = '<div class="no-capture">No capture available</div>';
    }
  }

  private updateTableState(state: ExperimentState): void {
    const container = document.getElementById('table-info');
    if (!container) return;

    const latestState = state.states[state.states.length - 1];
    const table = latestState?.parsedState?.table;

    if (!table) {
      container.innerHTML = '<div class="no-data">No table data</div>';
      return;
    }

    const formatChips = (chips: Record<string, number>): string => {
      return Object.entries(chips)
        .map(([k, v]) => `<div class="chip-row"><span>${k}:</span><span>${v}</span></div>`)
        .join('');
    };

    container.innerHTML = `
      <div class="info-card">
        <h3>My Chips</h3>
        ${formatChips(table.my_chips)}
      </div>
      <div class="info-card">
        <h3>Opponent Chips</h3>
        ${formatChips(table.opponent_chips)}
      </div>
      <div class="info-card">
        <h3>My Bet</h3>
        ${formatChips(table.my_current_bet)}
      </div>
      <div class="info-card">
        <h3>Opponent Bet</h3>
        ${formatChips(table.opponent_bet)}
      </div>
      <div class="info-card">
        <h3>Status</h3>
        <div class="chip-row"><span>My Turn:</span><span>${table.is_my_turn ? 'Yes' : 'No'}</span></div>
        <div class="chip-row"><span>Stable:</span><span>${table.scene_stable ? 'Yes' : 'No'}</span></div>
        <div class="chip-row"><span>Community:</span><span>${table.community_cards.length || 0}</span></div>
      </div>
    `;
  }
}

new MonitorApp();
