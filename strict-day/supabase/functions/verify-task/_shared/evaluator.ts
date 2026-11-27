/**
 * Shared, server-side rule evaluation for Strict Day.
 *
 * Mirrors the semantics of the device-side DefaultRuleEvaluator
 * (app/src/main/java/com/strictday/verification/DefaultRuleEvaluator.kt)
 * so that a rule yields the same verdict here as on the client. The server
 * copy is authoritative: the device uploads evidence events; only this code
 * decides whether a task's rules are satisfied.
 */

export type RuleRow = {
  id: string;
  task_id: string;
  provider: string;
  event_type: string;
  operator: string;
  target_value: string;
  min_count: number;
  min_duration_seconds: number;
  created_at: string;
};

export type EventRow = {
  id: number;
  task_id: string;
  provider: string;
  event_type: string;
  external_id: string;
  occurred_at: string;
  subject: string;
  metrics: Record<string, unknown>;
  received_at: string;
};

export type RuleEvaluation = {
  ruleId: string;
  eventType: string;
  operator: string;
  isMet: boolean;
  detail: string;
};

function toMillis(value: unknown): number {
  if (typeof value === "number") return value;
  if (typeof value === "string") {
    const n = Number(value);
    return Number.isFinite(n) ? n : 0;
  }
  if (typeof value === "boolean") return value ? 1 : 0;
  const big = value as { toNumber?: () => number };
  if (big && typeof big.toNumber === "function") return big.toNumber();
  return 0;
}

function matching(rule: RuleRow, events: EventRow[]): EventRow[] {
  return events.filter(
    (e) => e.event_type.toLowerCase() === rule.event_type.toLowerCase(),
  );
}

function subjectMatch(rule: RuleRow, event: EventRow): boolean {
  return event.subject
    .toLowerCase()
    .includes(rule.target_value.toLowerCase());
}

function aggregateMetric(rule: RuleRow, events: EventRow[]): number {
  if (!rule.target_value) return 0;
  return events.reduce((sum, e) => {
    const v = e.metrics[rule.target_value];
    return sum + (v === undefined || v === null ? 0 : toMillis(v));
  }, 0);
}

function metricEquals(rule: RuleRow, event: EventRow): boolean {
  return Object.values(event.metrics).some(
    (v) =>
      String(v).toLowerCase() === rule.target_value.toLowerCase(),
  );
}

function metricContains(rule: RuleRow, event: EventRow): boolean {
  if (subjectMatch(rule, event)) return true;
  return Object.values(event.metrics).some((v) =>
    String(v).toLowerCase().includes(rule.target_value.toLowerCase()),
  );
}

function withinWindow(rule: RuleRow, event: EventRow): boolean {
  const parts = rule.target_value.split("..");
  if (parts.length !== 2) return false;
  const start = Number(parts[0]);
  const end = Number(parts[1]);
  if (!Number.isFinite(start) || !Number.isFinite(end)) return false;
  const t = new Date(event.occurred_at).getTime();
  return t >= start && t <= end;
}

function evaluateRule(rule: RuleRow, events: EventRow[]): RuleEvaluation {
  const relevant = matching(rule, events);
  let isMet = false;
  let detail = "";
  const target = rule.target_value;

  switch (rule.operator) {
    case "count": {
      const count = relevant.filter((e) => subjectMatch(rule, e)).length;
      isMet = count >= rule.min_count;
      detail = `matched ${count}/${rule.min_count}`;
      break;
    }
    case "exists":
      isMet = relevant.length > 0;
      detail = isMet ? "events exist" : "no events";
      break;
    case "greater_than": {
      const sum = aggregateMetric(rule, relevant);
      const threshold = Number(target) || 0; // mirror toDoubleOrNull() ?: 0.0
      isMet = sum > threshold;
      detail = `${target} sum ${sum} > ${threshold}`;
      break;
    }
    case "less_than": {
      const sum = aggregateMetric(rule, relevant);
      const threshold = Number(target) || 0;
      isMet = sum < threshold;
      detail = `${target} sum ${sum} < ${threshold}`;
      break;
    }
    case "duration": {
      const total = relevant.reduce(
        (sum, e) => sum + toMillis(e.metrics.durationSeconds),
        0,
      );
      isMet = total >= rule.min_duration_seconds;
      detail = `total ${total}s >= ${rule.min_duration_seconds}s`;
      break;
    }
    case "equals":
      isMet = relevant.some((e) => metricEquals(rule, e));
      detail = isMet ? `value equals ${target}` : `no value equals ${target}`;
      break;
    case "contains":
      isMet = relevant.some((e) => metricContains(rule, e));
      detail = isMet ? `contains ${target}` : `no event contains ${target}`;
      break;
    case "within_time_window": {
      const count = relevant.filter((e) => withinWindow(rule, e)).length;
      isMet = count >= rule.min_count;
      detail = `${count}/${rule.min_count} events in window`;
      break;
    }
    default: {
      const found = relevant.some((e) => subjectMatch(rule, e));
      isMet = found;
      detail = `unknown operator '${rule.operator}'; fell back to subject match`;
      break;
    }
  }

  return {
    ruleId: rule.id,
    eventType: rule.event_type,
    operator: rule.operator,
    isMet,
    detail,
  };
}

/**
 * Evaluate a whole task. A task passes only when ALL of its rules are met.
 * A task with no rules is treated as pass-through (nothing to prove).
 */
export function evaluateTask(rules: RuleRow[], events: EventRow[]) {
  const perRule = rules.map((r) => evaluateRule(r, events));
  const verified =
    rules.length === 0 || perRule.every((r) => r.isMet);
  return { perRule, verified };
}