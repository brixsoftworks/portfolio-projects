import type { ProofType } from '@quacko/types';
import { clamp, round1 } from './streak';

/**
 * Proof auto-verification rules ("auto" tier). Media-based types still need
 * AI/peer verification — the server marks those with a verifier gate instead
 * of trusting the client.
 */
export interface AutoVerifyResult {
  verified: boolean;
  reason: string;
  result: Record<string, unknown> | null;
}

export const MEDIA_PROOF: ReadonlySet<ProofType> = new Set(['photo', 'video', 'audio', 'screenshot', 'code_tests']);

export function requiresHumanVerification(type: ProofType): boolean {
  return MEDIA_PROOF.has(type);
}

export function autoVerify(
  type: ProofType,
  metadata: Record<string, unknown>,
  rules: { minDistanceM?: number; minDurationSec?: number } = {},
): AutoVerifyResult {
  switch (type) {
    case 'gps': {
      const meters = typeof metadata.distanceMeters === 'number' ? metadata.distanceMeters : 0;
      const min = rules.minDistanceM ?? 1000;
      const verified = meters >= min;
      return {
        verified,
        reason: verified ? `GPS distance ${round1(meters)}m recorded` : `Distance ${meters}m below minimum ${min}m`,
        result: { distanceMeters: round1(meters), paceSecPerKm: metadata.paceSecPerKm ?? null },
      };
    }
    case 'quiz': {
      const score = typeof metadata.score === 'number' ? metadata.score : 0;
      const minimum = clamp(Number(metadata.passingScore ?? 0.7), 0, 1);
      const passed = score >= minimum;
      return {
        verified: passed,
        reason: passed ? `Quiz score ${Math.round(score * 100)}%` : `Quiz score below pass bar`,
        result: { score, passingScore: minimum },
      };
    }
    case 'timer': {
      const seconds = typeof metadata.durationSeconds === 'number' ? metadata.durationSeconds : 0;
      const min = rules.minDurationSec ?? 60;
      const verified = seconds >= min;
      return {
        verified,
        reason: verified ? `${seconds}s of focus recorded` : `Duration ${seconds}s below ${min}s`,
        result: { durationSeconds: seconds },
      };
    }
    case 'health_data': {
      const steps = typeof metadata.steps === 'number' ? metadata.steps : 0;
      const verified = steps >= (rules.minDistanceM ?? 1);
      return {
        verified,
        reason: verified ? `${steps} steps synced` : `No step data`,
        result: { steps },
      };
    }
    case 'manual_log': {
      const confirm = metadata.confirm === true;
      return {
        verified: confirm,
        reason: confirm ? 'Manual confirmation accepted' : 'Manual confirmation missing',
        result: confirm ? { confirmed: true } : null,
      };
    }
    default:
      return { verified: false, reason: `Type ${type} needs human/AI verification`, result: null };
  }
}