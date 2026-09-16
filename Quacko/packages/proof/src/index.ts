import type { ProofType } from '@quacko/types';
import { requiresHumanVerification } from '@quacko/domain';

export interface ProofDescriptor {
  type: ProofType;
  label: string;
  icon: string;
  hint: string;
  auto: boolean;
}

export const PROOF_DESCRIPTORS: Record<ProofType, ProofDescriptor> = {
  gps: { type: 'gps', label: 'GPS route', icon: 'near_me', hint: 'Automatic from a tracked run', auto: true },
  quiz: { type: 'quiz', label: 'Quiz score', icon: 'quiz', hint: 'Pass a generated quiz', auto: true },
  timer: { type: 'timer', label: 'Focus timer', icon: 'timer', hint: 'Logged focus time', auto: true },
  health_data: { type: 'health_data', label: 'Health data', icon: 'monitor_heart', hint: 'Synced from device', auto: true },
  photo: { type: 'photo', label: 'Photo', icon: 'photo_camera', hint: 'Snap your result', auto: false },
  video: { type: 'video', label: 'Video', icon: 'videocam', hint: 'Short clip proof', auto: false },
  audio: { type: 'audio', label: 'Audio', icon: 'mic', hint: 'Voice note proof', auto: false },
  screenshot: { type: 'screenshot', label: 'Screenshot', icon: 'screenshot', hint: 'Screen capture of result', auto: false },
  code_tests: { type: 'code_tests', label: 'Code tests', icon: 'terminal', hint: 'Failing tests = no proof', auto: true },
  manual_log: { type: 'manual_log', label: 'Manual log', icon: 'check_circle', hint: 'Your word (honor system)', auto: true },
};

export function descriptor(type: ProofType): ProofDescriptor {
  return PROOF_DESCRIPTORS[type];
}

export function needsHumanCheck(type: ProofType): boolean {
  return requiresHumanVerification(type);
}

/** Build the payload the backend accepts. Never a client trust assertion. */
export function buildProofPayload(type: ProofType, values: Record<string, unknown>): {
  type: ProofType;
  metadata: Record<string, unknown>;
} {
  return { type, metadata: values };
}