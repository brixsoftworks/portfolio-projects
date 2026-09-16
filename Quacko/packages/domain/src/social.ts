import type { ChatMessage } from '@quacko/types';

/** Server-rendered card summary for inline chat messages. */
export function chatCardFor(message: ChatMessage): {
  kind: ChatMessage['kind'];
  title: string;
  subtitle: string;
} | null {
  switch (message.kind) {
    case 'mission_verified':
      return {
        kind: 'mission_verified',
        title: message.text ?? 'Mission verified',
        subtitle: 'Quacko confirmed your mission',
      };
    case 'user_join':
      return { kind: 'user_join', title: 'New member', subtitle: message.text ?? '' };
    case 'battle_challenge':
      return { kind: 'battle_challenge', title: 'Battle challenge', subtitle: message.text ?? '' };
    case 'group_event':
      return { kind: 'group_event', title: 'Group event', subtitle: message.text ?? '' };
    case 'ai_comment':
      return { kind: 'ai_comment', title: 'Quacko says', subtitle: message.text ?? '' };
    case 'punishment_verdict':
      return { kind: 'punishment_verdict', title: 'Council verdict', subtitle: message.text ?? '' };
    case 'comeback':
      return { kind: 'comeback', title: 'Comeback', subtitle: message.text ?? '' };
    default:
      return null;
  }
}