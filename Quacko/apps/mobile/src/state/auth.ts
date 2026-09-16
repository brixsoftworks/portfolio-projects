import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { fetchMe, loginUser, registerUser, type RegisterInput } from '@quacko/client';
import type { UserProfile } from '@quacko/types';
import { env, isDemo } from '@/env';

const TOKEN_KEY = 'quacko.token';

interface AuthState {
  token: string | null;
  busy: boolean;
  error: string | null;
  /** Load the persisted token (no-op in demo mode). */
  restore: () => Promise<string | null>;
  login: (email: string, password: string) => Promise<UserProfile>;
  register: (input: RegisterInput) => Promise<UserProfile>;
  /** Validate the current token and return the profile it belongs to. */
  me: () => Promise<UserProfile>;
  logout: () => Promise<void>;
  setError: (message: string | null) => void;
}

const baseUrl = env.apiUrl;

export const useAuth = create<AuthState>((set, get) => ({
  token: null,
  busy: false,
  error: null,

  restore: async () => {
    if (isDemo) return null;
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      if (token) set({ token });
      return token;
    } catch {
      return null;
    }
  },

  login: async (email, password) => {
    set({ busy: true, error: null });
    try {
      const { token, profile } = await loginUser(baseUrl, email, password);
      await AsyncStorage.setItem(TOKEN_KEY, token);
      set({ token });
      return profile;
    } catch (e) {
      set({ error: e instanceof Error ? e.message : 'login failed' });
      throw e;
    } finally {
      set({ busy: false });
    }
  },

  register: async (input) => {
    set({ busy: true, error: null });
    try {
      const { token, profile } = await registerUser(baseUrl, {
        ...input,
        timezone: input.timezone ?? Intl.DateTimeFormat().resolvedOptions().timeZone ?? 'UTC',
      });
      await AsyncStorage.setItem(TOKEN_KEY, token);
      set({ token });
      return profile;
    } catch (e) {
      set({ error: e instanceof Error ? e.message : 'registration failed' });
      throw e;
    } finally {
      set({ busy: false });
    }
  },

  me: async () => {
    const { token } = get();
    if (!token) throw new Error('not signed in');
    return (await fetchMe(baseUrl, token)) as UserProfile;
  },

  logout: async () => {
    await AsyncStorage.removeItem(TOKEN_KEY);
    set({ token: null, error: null });
  },

  setError: (message) => set({ error: message }),
}));