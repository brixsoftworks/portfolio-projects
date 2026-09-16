import type { BackendCtx } from './ctx';
import type { NotificationCategory, NotificationItem, NotificationPreference } from '@quacko/types';
import { assertUser } from './ctx';

export async function createNotification(
  ctx: BackendCtx,
  uid: string,
  category: NotificationCategory,
  title: string,
  body: string,
  data: Record<string, string> = {},
): Promise<void> {
  const item: NotificationItem = {
    id: ctx.store.newId(),
    userId: uid,
    category,
    title,
    body,
    data,
    read: false,
    createdAt: ctx.now().toISOString(),
  };
  await ctx.store.transaction(async (tx) => {
    await tx.create('notifications', item);
  });
}

export async function saveNotificationPreference(ctx: BackendCtx, rawUid: unknown, rawPrefs: unknown): Promise<NotificationPreference> {
  const uid = assertUser(rawUid);
  const current: NotificationPreference | null = await ctx.store.get<NotificationPreference>('notificationPreferences', uid);
  const base = current ?? {
    userId: uid,
    missionReminder: { enabled: true, timeMinutes: 480 },
    streak: { enabled: true },
    checkIn: { enabled: true, timeMinutes: 1020 },
    group: { enabled: true },
    battle: { enabled: true },
    punishment: { enabled: true },
    achievement: { enabled: true },
  };
  const merged = { ...base, ...(rawPrefs as Partial<NotificationPreference>) };
  await ctx.store.transaction(async (tx) => {
    await tx.set('notificationPreferences', { id: uid, ...merged });
  });
  return merged;
}

export async function updateDeviceConnection(ctx: BackendCtx, rawUid: unknown, raw: unknown): Promise<void> {
  const uid = assertUser(rawUid);
  const body = raw as { pushToken?: string | null; platform: 'ios' | 'android' | 'web' };
  const existing = await ctx.store.find<{ id: string; userId: string }>('deviceConnections', {
    where: [{ field: 'userId', equals: uid }],
    limit: 1,
  });
  const id = existing[0]?.id ?? ctx.store.newId();
  await ctx.store.transaction(async (tx) => {
    await tx.set('deviceConnections', {
      id,
      userId: uid,
      pushToken: body.pushToken ?? null,
      platform: body.platform,
      lastSeenAt: ctx.now().toISOString(),
    });
  });
}

export async function listNotifications(ctx: BackendCtx, rawUid: unknown): Promise<NotificationItem[]> {
  const uid = assertUser(rawUid);
  const items = await ctx.store.find<NotificationItem>('notifications', {
    where: [{ field: 'userId', equals: uid }],
    orderBy: { field: 'createdAt', direction: 'desc' },
    limit: 100,
  });
  return items;
}