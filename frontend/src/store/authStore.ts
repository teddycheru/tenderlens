import { create } from 'zustand'
import type { User } from '@/types/auth'
import { setAuthTokens, clearAuthTokens } from '@/lib/auth'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  setUser: (user: User) => void
  setAuth: (user: User, accessToken: string, refreshToken: string) => void
  logout: () => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  setUser: (user) => {
    set({ user, isAuthenticated: true })
  },

  setAuth: (user, accessToken, refreshToken) => {
    setAuthTokens(accessToken, refreshToken)
    set({ user, isAuthenticated: true, isLoading: false })
  },

  logout: () => {
    clearAuthTokens()
    set({ user: null, isAuthenticated: false, isLoading: false })
  },

  setLoading: (loading) => {
    set({ isLoading: loading })
  },
}))
