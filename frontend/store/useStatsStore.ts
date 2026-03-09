'use client'

import { create } from 'zustand'

type StatState = {
  listeners: number
  sources: number
  bandwidth: number
  setStats: (payload: { listeners?: number; sources?: number; bandwidth?: number }) => void
}

export const useStatsStore = create<StatState>((set) => ({
  listeners: 0,
  sources: 0,
  bandwidth: 0,
  setStats: (payload) => set((state) => ({ ...state, ...payload }))
}))
