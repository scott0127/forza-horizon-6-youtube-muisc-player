export type MusicService = 'youtube' | 'spotify' | 'apple' | 'windows'
export type ThemeMode = 'dark' | 'luxury' | 'radio'

export interface TrackState {
  title: string
  artist: string
  album: string
  appId: string
  status: string
  error: string
  isEmpty: boolean
  positionSeconds: number
  durationSeconds: number
  timelineUpdatedAt: number
  playbackRate: number
  sourceLabel: string
  service: MusicService
  accent: string
  artworkKey: string
  artworkDataUrl: string | null
}

export interface BackendEvent {
  type: string
  version?: string
  appTitle?: string
  track?: TrackState
  command?: string
  message?: string
  code?: number | null
  pressed?: string[]
}

export interface PositionModeEvent {
  enabled: boolean
}

export interface ThemeModeEvent {
  themeMode: ThemeMode
}

export interface PlayerScaleEvent {
  scale: number
}

export interface ForzaApi {
  onBackendEvent(callback: (event: BackendEvent) => void): () => void
  onPositionMode(callback: (event: PositionModeEvent) => void): () => void
  onThemeMode(callback: (event: ThemeModeEvent) => void): () => void
  onPlayerScale(callback: (event: PlayerScaleEvent) => void): () => void
  sendBackendCommand(command: Record<string, unknown>): Promise<void>
  showControlWindow(): Promise<void>
  hideControlWindow(): Promise<void>
  togglePlayerWindow(): Promise<void>
  togglePositionMode(): Promise<boolean>
  getThemeMode(): Promise<ThemeMode>
  setThemeMode(themeMode: ThemeMode): Promise<ThemeMode>
  getPlayerScale(): Promise<number>
  setPlayerScale(playerScale: number): Promise<number>
}

declare global {
  interface Window {
    forzaApi: ForzaApi
  }
}
