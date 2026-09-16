import type { BackendCtx } from './ctx';
import type {
  Group,
  GroupMember,
  ChatMessage,
  Battle,
  Punishment,
  PunishmentVote,
  UserProfile,
} from '@quacko/types';
import { approval, battleXp } from '@quacko/domain/src/battle';
import { assertDoc, assertInput, assertUser } from './ctx';
import { awardXp } from './missions';
import {
  createBattleInput,
  createGroupInput,
  joinGroupInput,
  proposePunishmentInput,
  resolveBattleInput,
  sendMessageInput,
  simulateGroupAIMessageInput,
  tickBattleInput,
  voteInput,
  requestCoachMessageInput,
} from '@quacko/validation';
import { createNotification } from './notifications';

const INVITE_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
function inviteCode(): string {
  let out = '';
  for (let i = 0; i < 6; i += 1) {
    out += INVITE_CHARS[Math.floor(Math.random() * INVITE_CHARS.length)] ?? 'A';
  }
  return out;
}

async function memberIds(ctx: BackendCtx, groupId: string): Promise<string[]> {
  const members = await ctx.store.find<GroupMember>('groupMembers', { where: [{ field: 'groupId', equals: groupId }] });
  return members.filter((m) => m.status === 'active').map((m) => m.userId);
}

async function ensureActiveMember(ctx: BackendCtx, uid: string, groupId: string): Promise<void> {
  const members = await ctx.store.find<GroupMember>('groupMembers', { where: [{ field: 'userId', equals: uid }] });
  const inGroup = members.find((m) => m.groupId === groupId);
  if (!inGroup || inGroup.status !== 'active') throw new Error('not a member of this group');
}

export async function createGroup(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<Group> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, createGroupInput);
  const profile = assertDoc(await ctx.store.get<UserProfile>('userProfiles', uid), 'profile');
  const now = ctx.now().toISOString();
  const group: Group = {
    id: ctx.store.newId(),
    name: input.name,
    description: input.description,
    emoji: input.emoji,
    ownerId: uid,
    memberCount: 1,
    invitationCode: inviteCode(),
    createdAt: now,
    settings: {
      defaultStakesPoints: input.defaultStakesPoints,
      punishmentEnabled: true,
      batteryVersion: 'bq4',
    },
  };
  const member: GroupMember = {
    groupId: group.id,
    userId: uid,
    username: profile.username,
    avatarUrl: profile.avatarUrl,
    joinedAt: now,
    role: 'admin',
    status: 'active',
    balance: 1000,
  };
  await ctx.store.transaction(async (tx) => {
    await tx.create('groups', group);
    await tx.create('groupMembers', { ...member, id: ctx.store.newId() });
    await tx.create('messages', {
      id: ctx.store.newId(),
      groupId: group.id,
      authorId: 'quacko',
      authorName: 'Quacko',
      authorAvatar: null,
      kind: 'group_event',
      text: `Welcome to ${group.name}!`,
      seq: 1,
      createdAt: now,
    });
  });
  return group;
}

export async function joinGroup(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<Group> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, joinGroupInput);
  const group = (await ctx.store.find<Group>('groups', { where: [{ field: 'invitationCode', equals: input.invitationCode }], limit: 1 }))[0];
  if (!group) throw new Error('invitation code not found');
  const profile = assertDoc(await ctx.store.get<UserProfile>('userProfiles', uid), 'profile');
  const member: GroupMember = {
    groupId: group.id,
    userId: uid,
    username: profile.username,
    avatarUrl: profile.avatarUrl,
    joinedAt: ctx.now().toISOString(),
    role: 'member',
    status: 'active',
    balance: 1000,
  };
  await ctx.store.transaction(async (tx) => {
    await tx.create('groupMembers', { ...member, id: ctx.store.newId() });
    await tx.update<Group>('groups', group.id, { memberCount: group.memberCount + 1 });
    await tx.create('messages', {
      id: ctx.store.newId(),
      groupId: group.id,
      authorId: uid,
      authorName: profile.username,
      authorAvatar: profile.avatarUrl,
      kind: 'user_join',
      text: `${profile.displayName} joined the group`,
      seq: Date.now(),
      createdAt: ctx.now().toISOString(),
    });
  });
  return group;
}

export async function sendMessage(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<ChatMessage> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, sendMessageInput);
  const group = assertDoc(await ctx.store.get<Group>('groups', input.groupId), 'group');
  await ensureActiveMember(ctx, uid, group.id);
  const profile = assertDoc(await ctx.store.get<UserProfile>('userProfiles', uid), 'profile');
  const now = ctx.now().toISOString();
  const message: ChatMessage = {
    id: ctx.store.newId(),
    groupId: group.id,
    authorId: uid,
    authorName: profile.username,
    authorAvatar: profile.avatarUrl,
    kind: input.kind ?? 'text',
    text: input.text ?? null,
    createdAt: now,
    seq: Date.now(),
  };
  await ctx.store.transaction(async (tx) => {
    await tx.create('messages', message);
  });
  return message;
}

export async function createBattle(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<Battle> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, createBattleInput);
  const group = assertDoc(await ctx.store.get<Group>('groups', input.groupId), 'group');
  await ensureActiveMember(ctx, uid, group.id);
  await ensureActiveMember(ctx, input.challengeeId, group.id);
  const battle: Battle = {
    id: ctx.store.newId(),
    groupId: group.id,
    challengeeId: input.challengeeId,
    challengerId: uid,
    killCriteria: input.killCriteria,
    timeLimitSeconds: input.timeLimitSeconds,
    stakesPoints: input.stakesPoints,
    status: 'active',
    punishments: [],
    outcome: null,
    winnerId: null,
    tickAt: null,
    createdAt: ctx.now().toISOString(),
    finishedAt: null,
  };
  await ctx.store.transaction(async (tx) => {
    await tx.create('battles', battle);
    await tx.create('messages', {
      id: ctx.store.newId(),
      groupId: group.id,
      authorId: 'quacko',
      authorName: 'Quacko',
      authorAvatar: null,
      kind: 'battle_challenge',
      text: `Battle started: ${input.killCriteria} — stakes ${input.stakesPoints} pts`,
      seq: Date.now(),
      createdAt: ctx.now().toISOString(),
    });
  });
  return battle;
}

export async function tickBattle(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<Battle> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, tickBattleInput);
  const battle = assertDoc(await ctx.store.get<Battle>('battles', input.battleId), 'battle');
  await ensureActiveMember(ctx, uid, battle.groupId);
  const isParticipant = uid === battle.challengerId || uid === battle.challengeeId;
  if (!isParticipant) throw new Error('not a battle participant');

  const now = ctx.now().toISOString();
  await ctx.store.transaction(async (tx) => {
    await tx.set('battleTicks', {
      id: ctx.store.newId(),
      battleId: battle.id,
      at: now,
      checkin1: uid === battle.challengerId ? input.checkin : true,
      checkin2: uid === battle.challengeeId ? input.checkin : true,
      xp1: 0,
      xp2: 0,
    });
    await tx.update<Battle>('battles', battle.id, { tickAt: now });
  });
  return (await ctx.store.get<Battle>('battles', battle.id)) ?? battle;
}

export async function resolveBattle(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<Battle> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, resolveBattleInput);
  const battle = assertDoc(await ctx.store.get<Battle>('battles', input.battleId), 'battle');
  await ensureActiveMember(ctx, uid, battle.groupId);
  const ticks = await ctx.store.find<{ battleId: string; checkin1: boolean; checkin2: boolean; at: string }>('battleTicks', {
    where: [{ field: 'battleId', equals: battle.id }],
    orderBy: { field: 'at', direction: 'asc' },
    limit: 30,
  });
  const latest = ticks[ticks.length - 1];
  let winnerId: string | null = null;
  let outcome: Battle['outcome'] = 'time_limit';
  if (latest && latest.checkin1 !== latest.checkin2) {
    const challengerMissed = !latest.checkin1;
    winnerId = challengerMissed ? battle.challengeeId : battle.challengerId;
    outcome = 'kill';
  } else if (latest && !latest.checkin1 && !latest.checkin2) {
    outcome = 'double_kill';
  } else if (ticks.length >= 2) {
    const bothLast = ticks[ticks.length - 2];
    if (bothLast && !bothLast.checkin1 && !bothLast.checkin2) outcome = 'time_limit';
  }

  const meId = uid;
  const meActive = tickCheck(ticks, meId, battle);
  const themId = meId === battle.challengerId ? battle.challengeeId : battle.challengerId;
  const themActive = tickCheck(ticks, themId, battle);
  const { mine, theirs } = battleXp(300, meActive ? 1 : 0, themActive ? 1 : 0);

  const finished: Battle = {
    ...battle,
    id: battle.id,
    status: 'finished',
    outcome,
    winnerId,
    finishedAt: ctx.now().toISOString(),
  };
  await ctx.store.transaction(async (tx) => {
    await tx.set('battles', finished);
    await tx.create('messages', {
      id: ctx.store.newId(),
      groupId: battle.groupId,
      authorId: 'quacko',
      authorName: 'Quacko',
      authorAvatar: null,
      kind: 'group_event',
      text: winnerId ? `Battle decided — ${winnerId.slice(0, 8)} wins!` : 'Battle ended in a draw.',
      seq: Date.now(),
      createdAt: ctx.now().toISOString(),
    });
  });

  await awardXp(ctx, meId, mine, null);
  await awardXp(ctx, themId, theirs, null);
  if (winnerId) {
    const loserId = winnerId === battle.challengerId ? battle.challengeeId : battle.challengerId;
    await createNotification(ctx, loserId, 'battle', 'Battle lost', `You lost a battle. Comeback stronger!`, { battleId: battle.id });
  }
  return finished;
}

function tickCheck(
  ticks: { checkin1: boolean; checkin2: boolean }[],
  participantId: string,
  battle: Battle,
): number {
  const is1 = participantId === battle.challengerId;
  return ticks.filter((t) => (is1 ? t.checkin1 : t.checkin2)).length;
}

/* ------------------------------ punishment council ------------------------- */

export async function proposePunishment(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<Punishment> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, proposePunishmentInput);
  const group = assertDoc(await ctx.store.get<Group>('groups', input.groupId), 'group');
  await ensureActiveMember(ctx, uid, group.id);
  const members = await memberIds(ctx, group.id);
  if (!members.includes(input.targetUserId)) throw new Error('target is not a member');
  const councilSize = Math.max(members.length - 1, 1);

  const punishment: Punishment = {
    id: ctx.store.newId(),
    groupId: group.id,
    targetUserId: input.targetUserId,
    title: input.title,
    description: input.description,
    durationDays: input.durationDays,
    severity: input.severity,
    emoji: input.emoji,
    link: input.link ?? null,
    status: 'voting',
    proposerId: uid,
    councilSize,
    approvalThreshold: 0.6,
    votesFor: 0,
    votesAgainst: 0,
    assignedDay: '',
    deadlineAt: null,
    proof: null,
    createdAt: ctx.now().toISOString(),
    updatedAt: ctx.now().toISOString(),
  };
  await ctx.store.transaction(async (tx) => {
    await tx.create('punishments', punishment);
    await tx.create('messages', {
      id: ctx.store.newId(),
      groupId: group.id,
      authorId: 'quacko',
      authorName: 'Quacko',
      authorAvatar: null,
      kind: 'punishment_verdict',
      text: `Council case opened: ${punishment.title}`,
      seq: Date.now(),
      createdAt: ctx.now().toISOString(),
    });
  });
  return punishment;
}

export async function castVote(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<Punishment> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, voteInput);
  const punishment = assertDoc(await ctx.store.get<Punishment>('punishments', input.punishmentId), 'punishment');
  if (punishment.status !== 'voting') throw new Error('voting closed');
  if (punishment.proposerId === uid) throw new Error('proposer cannot vote');

  const existing = await ctx.store.find<PunishmentVote>('punishmentVotes', {
    where: [{ field: 'punishmentId', equals: punishment.id }, { field: 'voterId', equals: uid }],
  });
  const votesFor = punishment.votesFor + (!existing.length && input.vote === 'for' ? 1 : 0);
  const votesAgainst = punishment.votesAgainst + (!existing.length && input.vote === 'against' ? 1 : 0);
  const passed = votesFor + votesAgainst >= punishment.councilSize && approval({ votesFor, votesAgainst }, punishment.approvalThreshold);

  await ctx.store.transaction(async (tx) => {
    if (!existing.length) {
      await tx.create<PunishmentVote>('punishmentVotes', {
        id: ctx.store.newId(),
        punishmentId: punishment.id,
        voterId: uid,
        vote: input.vote,
        createdAt: ctx.now().toISOString(),
      });
    }
    await tx.update<Punishment>('punishments', punishment.id, {
      votesFor,
      votesAgainst,
      status: passed || (votesFor + votesAgainst >= punishment.councilSize) ? (passed ? 'approved' : 'rejected') : 'voting',
      updatedAt: ctx.now().toISOString(),
    });
  });
  return (await ctx.store.get<Punishment>('punishments', punishment.id)) ?? punishment;
}

export async function submitPunishmentProof(ctx: BackendCtx, rawUid: unknown, punishmentId: unknown, evidence: string | null): Promise<Punishment> {
  const uid = assertUser(rawUid);
  const punishment = assertDoc(await ctx.store.get<Punishment>('punishments', String(punishmentId)), 'punishment');
  if (punishment.targetUserId !== uid) throw new Error('not the punished member');
  const now = ctx.now().toISOString();
  const completed: Punishment = {
    ...punishment,
    id: punishment.id,
    status: 'completed',
    proof: { accepted: evidence != null, verifiedAt: now, details: evidence ?? 'accepted' },
    updatedAt: now,
  };
  await ctx.store.transaction(async (tx) => {
    await tx.set('punishments', completed);
    await tx.create('messages', {
      id: ctx.store.newId(),
      groupId: punishment.groupId,
      authorId: 'quacko',
      authorName: 'Quacko',
      authorAvatar: null,
      kind: 'punishment_verdict',
      text: `Punishment served: ${punishment.title} 🎉`,
      seq: Date.now(),
      createdAt: now,
    });
  });
  await createNotification(ctx, uid, 'punishment', 'Punishment served', `You completed "${punishment.title}" — welcome back, quack.`, {});
  return completed;
}

export async function requestCoachMessage(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<{ message: string; emoji: string }> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, requestCoachMessageInput);
  const goal = input.goalId ? await ctx.store.get<import('@quacko/types').Goal>('goals', input.goalId) : null;
  const result = await ctx.ai.generateCoachMessage({
    goalTitle: goal?.title ?? 'your goal',
    streak: 0,
    recentNote: goal?.description ?? '',
    context: input.context,
  });
  await createNotification(ctx, uid, 'system', `Quacko says ${result.emoji}`, result.message, {});
  return result;
}

export async function simulateGroupAIMessage(ctx: BackendCtx, rawUid: unknown, rawInput: unknown): Promise<ChatMessage> {
  const uid = assertUser(rawUid);
  const input = assertInput(rawInput, simulateGroupAIMessageInput);
  const group = assertDoc(await ctx.store.get<Group>('groups', input.groupId), 'group');
  await ensureActiveMember(ctx, uid, group.id);
  const recent = await ctx.store.find<ChatMessage>('messages', {
    where: [{ field: 'groupId', equals: group.id }],
    orderBy: { field: 'seq', direction: 'desc' },
    limit: 8,
  });
  const result = await ctx.ai.generateGroupMessage({
    groupName: group.name,
    recentMessages: recent.map((r) => r.text ?? '').filter(Boolean),
  });
  const message: ChatMessage = {
    id: ctx.store.newId(),
    groupId: group.id,
    authorId: 'quacko',
    authorName: result.as,
    authorAvatar: null,
    kind: 'ai_comment',
    text: result.message,
    createdAt: ctx.now().toISOString(),
    seq: Date.now(),
  };
  await ctx.store.transaction(async (tx) => {
    await tx.create('messages', message);
  });
  return message;
}

export { memberIds };