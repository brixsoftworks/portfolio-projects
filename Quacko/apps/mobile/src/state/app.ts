import { create } from 'zustand';
import type { Goal, Mission, UserProfile } from '@quacko/types';
import { getApi } from '@/lib/api';
import { useAuth } from '@/state/auth';
import { isDemo } from '@/env';

export interface OnboardingDraft {
  selectedAreas: string[];
  displayName: string;
}

interface AppState {
  uid: string;
  booted: boolean;
  booting: boolean;
  error: string | null;
  profile: UserProfile | null;
  goals: Goal[];
  missions: Mission[];
  loadingMissions: boolean;

  bootstrap: () => Promise<void>;
  refreshGoals: () => Promise<void>;
  refreshMissions: () => Promise<void>;
  completeOnboarding: (draft: OnboardingDraft) => Promise<void>;
  setProfile: (p: UserProfile) => void;
}

export const DEMO_UID = 'local_ducky';

export const useApp = create<AppState>((set, get) => ({
  uid: DEMO_UID,
  booted: false,
  booting: false,
  error: null,
  profile: null,
  goals: [],
  missions: [],
  loadingMissions: false,

  bootstrap: async () => {
    set({ booting: true, error: null });
    try {
      if (isDemo) {
        const profile = await getApi().getOrCreateProfile(DEMO_UID, {
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone ?? 'UTC',
          displayName: 'Demo Ducky',
        });
        set({ profile, uid: profile.authUid ?? profile.id, booted: true });
        return;
      }
      const token = await useAuth.getState().restore();
      if (!token) {
        // No session → show the login screen.
        set({ booted: true });
        return;
      }
      const profile = await useAuth.getState().me();
      set({ profile, uid: profile.authUid ?? profile.id, booted: true });
    } catch (e) {
      set({ error: e instanceof Error ? e.message : 'bootstrap failed' });
    } finally {
      set({ booting: false });
    }
  },

  refreshGoals: async () => {
    const goals = await getApi().listGoals(get().uid);
    set({ goals });
  },

  refreshMissions: async () => {
    set({ loadingMissions: true });
    try {
      await getApi().generateDailyMissions();
      const missions = await getApi().listMissions(get().uid);
      set({ missions });
    } finally {
      set({ loadingMissions: false });
    }
  },

  completeOnboarding: async (draft) => {
    await getApi().setOnboarding(get().uid, {
      step: 'done',
      selectedAreas: draft.selectedAreas,
      completed: true,
    });
    const profile = get().profile;
    if (profile) set({ profile: { ...profile, hasSeenOnboarding: true, displayName: draft.displayName || profile.displayName } });
  },

  setProfile: (p) => set({ profile: p }),
}));