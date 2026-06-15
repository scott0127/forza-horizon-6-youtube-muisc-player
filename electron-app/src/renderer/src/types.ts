export type MusicService = 'youtube' | 'spotify' | 'apple' | 'kkbox' | 'windows'
export type ThemeMode = 'dark' | 'luxury' | 'radio'
export type GamepadAction = 'play_pause' | 'next_track' | 'previous_track' | 'volume_up' | 'volume_down'
export type AssignableGamepadButton =
  | 'A'
  | 'B'
  | 'X'
  | 'Y'
  | 'LB'
  | 'RB'
  | 'R3'
  | 'DPAD_UP'
  | 'DPAD_DOWN'
  | 'DPAD_LEFT'
  | 'DPAD_RIGHT'
  | 'LT'
  | 'RT'
  | 'LS_UP'
  | 'LS_DOWN'
  | 'LS_LEFT'
  | 'LS_RIGHT'
  | 'RS_UP'
  | 'RS_DOWN'
  | 'RS_LEFT'
  | 'RS_RIGHT'
export type GamepadBindings = Record<GamepadAction, AssignableGamepadButton>

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
  settings?: {
    overlay_x?: number
    overlay_y?: number
    music_service?: string
    volume_mode?: 'app' | 'system'
    show_lyrics?: boolean
    gamepad_bindings?: GamepadBindings
    gamepad_profile_overrides?: Record<string, 'xbox' | 'playstation'>
  }
  track?: TrackState
  command?: string
  message?: string
  code?: number | null
  pressed?: string[]
  deviceKey?: string
  deviceName?: string
  setting?: string
  volume?: number
  lyrics?: string
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

export interface PlayerTextScaleEvent {
  scale: number
}

export interface ForzaApi {
  onBackendEvent(callback: (event: BackendEvent) => void): () => void
  onPositionMode(callback: (event: PositionModeEvent) => void): () => void
  onThemeMode(callback: (event: ThemeModeEvent) => void): () => void
  onPlayerScale(callback: (event: PlayerScaleEvent) => void): () => void
  onPlayerTextScale(callback: (event: PlayerTextScaleEvent) => void): () => void
  sendBackendCommand(command: Record<string, unknown>): Promise<void>
  showControlWindow(): Promise<void>
  hideControlWindow(): Promise<void>
  togglePlayerWindow(): Promise<void>
  togglePositionMode(): Promise<boolean>
  getThemeMode(): Promise<ThemeMode>
  setThemeMode(themeMode: ThemeMode): Promise<ThemeMode>
  getPlayerScale(): Promise<number>
  setPlayerScale(playerScale: number): Promise<number>
  getPlayerTextScale(): Promise<number>
  setPlayerTextScale(playerTextScale: number): Promise<number>
}

declare global {
  interface Window {
    forzaApi: ForzaApi
  }
}
