<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import gsap from 'gsap'
import {
  ChevronsLeft,
  ChevronsRight,
  CirclePlay,
  Gamepad2,
  Gem,
  MonitorUp,
  Move,
  Music2,
  Minus,
  Minimize2,
  Plus,
  Power,
  Radio,
  RotateCcw,
  Sparkles,
  Volume2,
  VolumeX
} from '@lucide/vue'
import bmcQr from './assets/bmc_qr.png'
import xboxA from './assets/xbox-a.svg'
import xboxB from './assets/xbox-b.svg'
import xboxL3 from './assets/xbox-l3.png'
import xboxL3Active from './assets/xbox-l3-active.png'
import xboxUp from './assets/xbox-up.png'
import xboxX from './assets/xbox-x.svg'
import psCross from './assets/ps-cross.svg'
import psCircle from './assets/ps-circle.svg'
import psSquare from './assets/ps-square.svg'
import youtubeMusicIcon from './assets/brand-icons/youtube-music.png'
import spotifyIcon from './assets/brand-icons/spotify.png'
import appleIcon from './assets/brand-icons/apple.svg'
import kkboxIcon from './assets/brand-icons/kkbox.png'
import ControlThemeToolbar from './components/ControlThemeToolbar.vue'
import LiquidRuptureBackground from './components/LiquidRuptureBackground.vue'
import NowPlayingPanel from './components/NowPlayingPanel.vue'
import ServiceSourcePanel from './components/ServiceSourcePanel.vue'
import SponsorSupportPanel from './components/SponsorSupportPanel.vue'
import type { BackendEvent, MusicService, ThemeMode, TrackState } from './types'

const IDLE_ACCENT = '#8b5cf6'
const SERVICE_ACCENTS: Record<Exclude<MusicService, 'windows'>, string> = {
  youtube: '#ff0033',
  spotify: '#1ed760',
  apple: '#e5e7eb',
  kkbox: '#39c5ff'
}
const sourceServices: Array<{
  id: Exclude<MusicService, 'windows'>
  label: string
  iconSrc: string
  iconClass?: string
}> = [
  { id: 'youtube', label: 'YouTube Music', iconSrc: youtubeMusicIcon },
  { id: 'spotify', label: 'Spotify', iconSrc: spotifyIcon },
  { id: 'apple', label: 'Apple Music', iconSrc: appleIcon, iconClass: 'apple-brand-image' },
  { id: 'kkbox', label: 'KKBOX', iconSrc: kkboxIcon, iconClass: 'kkbox-brand-image' }
]
const MANUAL_SERVICE_LOCK_MS = 10000
const IDLE_GRACE_MS = 2200
const SPONSOR_URL = 'https://buymeacoffee.com/scott5497'
const DEFAULT_PLAYER_SCALE = 0.8
const MIN_PLAYER_SCALE = 0.6
const MAX_PLAYER_SCALE = 1
const PLAYER_SCALE_STEP = 0.05
const DEFAULT_PLAYER_TEXT_SCALE = 1
const MIN_PLAYER_TEXT_SCALE = 0.85
const MAX_PLAYER_TEXT_SCALE = 1.25
const PLAYER_TEXT_SCALE_STEP = 0.05
const SPOTIFY_TIP_AUTO_CLOSE_MS = 5000
type GraphicalControllerButton = 'L3' | 'L3_ACTIVE' | 'A' | 'B' | 'X' | 'DPAD_LEFT' | 'DPAD_RIGHT'
type AssignableControllerButton =
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
type GamepadAction = 'play_pause' | 'next_track' | 'previous_track' | 'volume_up' | 'volume_down'
type GamepadBindings = Record<GamepadAction, AssignableControllerButton>
const DEFAULT_GAMEPAD_BINDINGS: GamepadBindings = {
  play_pause: 'A',
  next_track: 'B',
  previous_track: 'X',
  volume_up: 'DPAD_RIGHT',
  volume_down: 'DPAD_LEFT'
}
const gamepadBindingRows: Array<{ action: GamepadAction; label: string }> = [
  { action: 'play_pause', label: '播放 / 暫停' },
  { action: 'next_track', label: '下一首' },
  { action: 'previous_track', label: '上一首' },
  { action: 'volume_up', label: '調高音量' },
  { action: 'volume_down', label: '調低音量' }
]
const assignableControllerButtons: AssignableControllerButton[] = [
  'A',
  'B',
  'X',
  'Y',
  'LB',
  'RB',
  'R3',
  'DPAD_UP',
  'DPAD_DOWN',
  'DPAD_LEFT',
  'DPAD_RIGHT',
  'LT',
  'RT',
  'LS_UP',
  'LS_DOWN',
  'LS_LEFT',
  'LS_RIGHT',
  'RS_UP',
  'RS_DOWN',
  'RS_LEFT',
  'RS_RIGHT'
]
const view = new URLSearchParams(window.location.search).get('view') === 'player' ? 'player' : 'control'
const controlRoot = ref<HTMLElement | null>(null)
const now = ref(Date.now() / 1000)
const backendStatus = ref('後端啟動中')
const gamepadStatus = ref('手把狀態尚未回報')
const isPlayStation = computed(() => {
  return gamepadStatus.value.toLowerCase().includes('playstation')
})
const lastMessage = ref('')
const positionMode = ref(false)
const themeMode = ref<ThemeMode>('dark')
const playerScale = ref(DEFAULT_PLAYER_SCALE)
const playerTextScale = ref(DEFAULT_PLAYER_TEXT_SCALE)
const volumeMode = ref<'app' | 'system'>('app')
const showLyrics = ref<boolean>(false)
const rawLyrics = ref<string>('')
const pressedGamepadButtons = ref<string[]>([])
const gamepadBindings = ref<GamepadBindings>({ ...DEFAULT_GAMEPAD_BINDINGS })
const confirmedGamepadBindings = ref<GamepadBindings>({ ...DEFAULT_GAMEPAD_BINDINGS })
const gamepadBindingError = ref('')
const listeningGamepadAction = ref<GamepadAction | null>(null)
const gamepadCaptureArmed = ref(false)
const pendingGamepadProfile = ref<{ deviceKey: string; deviceName: string } | null>(null)
const selectedService = ref<Exclude<MusicService, 'windows'>>('youtube')
const showSpotifyTip = ref(view === 'control')
let spotifyTipTimer: number | null = null
let controlAnimationContext: gsap.Context | null = null
let activeServiceTween: gsap.core.Tween | null = null
let manualServiceLockUntil = 0

function clearSpotifyTipTimer(): void {
  if (spotifyTipTimer !== null) {
    window.clearTimeout(spotifyTipTimer)
    spotifyTipTimer = null
  }
}

function startSpotifyTipTimer(): void {
  clearSpotifyTipTimer()
  if (view !== 'control' || !showSpotifyTip.value) return

  spotifyTipTimer = window.setTimeout(() => {
    showSpotifyTip.value = false
    spotifyTipTimer = null
  }, SPOTIFY_TIP_AUTO_CLOSE_MS)
}

function openSpotifyTip(): void {
  showSpotifyTip.value = true
  startSpotifyTipTimer()
}

function closeSpotifyTip(): void {
  showSpotifyTip.value = false
  clearSpotifyTipTimer()
}

startSpotifyTipTimer()

const emptyTrack: TrackState = {
  title: '',
  artist: '',
  album: '',
  appId: '',
  status: 'NO_SESSION',
  error: '',
  isEmpty: true,
  positionSeconds: 0,
  durationSeconds: 0,
  timelineUpdatedAt: 0,
  playbackRate: 1,
  sourceLabel: 'YOUTUBE MUSIC',
  service: 'youtube',
  accent: '#ff0033',
  artworkKey: '',
  artworkDataUrl: null
}

const track = ref<TrackState>({ ...emptyTrack })
const lastArtwork = ref<{ key: string; dataUrl: string } | null>(null)
const lastPlayableTrack = ref<TrackState | null>(null)
const lastPlayableAt = ref(0)

const appVolume = ref<number | null>(null)
let volumeHideTimer: number | undefined
const volumePercent = computed(() => Math.max(0, Math.min(100, Math.round((appVolume.value ?? 0) * 100))))
const volumeFill = computed(() => `${volumePercent.value}%`)

const isIdle = computed(() => track.value.isEmpty || track.value.status === 'NO_SESSION' || track.value.status === 'NO_MEDIA')
const accent = computed(() => {
  if (view === 'control') {
    return SERVICE_ACCENTS[selectedService.value]
  }

  if (isIdle.value) return IDLE_ACCENT
  if (track.value.service && track.value.service !== 'windows') {
    return track.value.accent || SERVICE_ACCENTS[track.value.service]
  }

  return track.value.accent || '#ff0033'
})
const visibleAccent = computed(() => {
  const nextAccent = accent.value.toLowerCase()
  if (view === 'control' && selectedService.value === 'apple') {
    return '#d8dee8'
  }
  if (view === 'player' && track.value.appId && track.value.appId.toLowerCase().includes('apple')) {
    return '#d8dee8'
  }
  if (themeMode.value === 'dark' && (nextAccent === '#111111' || nextAccent === '#000000')) {
    return '#f8fafc'
  }

  return accent.value
})
const sourceDisplayLabel = computed(() => (isIdle.value ? '待機中' : track.value.sourceLabel))
const trackContentKey = computed(() =>
  [
    isIdle.value ? 'idle' : 'playing',
    track.value.title,
    track.value.artist,
    track.value.album,
    track.value.appId,
    track.value.artworkKey
  ].join('|')
)
const serviceName = computed(() => {
  if (isIdle.value) return 'Ready'
  if (track.value.service === 'apple') return 'Apple Music'
  if (track.value.service === 'kkbox') return 'KKBOX'
  if (track.value.service === 'spotify') return 'Spotify'
  if (track.value.service === 'youtube') return 'YouTube Music'
  return 'Windows Media'
})

const activeService = computed<Exclude<MusicService, 'windows'>>(() => {
  return selectedService.value
})

const isAd = computed(() => {
  if (track.value.isEmpty || !track.value.title) return false
  const title = track.value.title.toLowerCase().trim()
  const artist = (track.value.artist || '').toLowerCase().trim()
  
  const adTitles = ['廣告', 'advertisement', 'spotify', 'spotify free']
  const browserArtists = ['chrome', 'edge', 'firefox', 'brave', 'safari', 'opera', 'spotify']
  
  if (adTitles.includes(title)) {
    if (!artist || browserArtists.some(b => artist.includes(b))) {
      return true
    }
  }
  return false
})

const displayTitle = computed(() => {
  if (track.value.error) return '讀取媒體資訊失敗'
  if (track.value.isEmpty || !track.value.title) return '等待音樂播放'
  if (isAd.value) return `${serviceName.value} 廣告放送中`
  return track.value.title
})

const displayArtist = computed(() => {
  if (track.value.error) return track.value.error
  if (track.value.isEmpty) return '請先登入並播放 YouTube Music、Spotify、Apple Music 或 KKBOX'
  if (isAd.value) return '（此為串流平台原生廣告，非本程式植入）'
  return track.value.artist || track.value.album || track.value.appId || '未知來源'
})

const titleChars = computed(() => displayTitle.value.split(''))
const artistChars = computed(() => displayArtist.value.split(''))

const displayPosition = computed(() => {
  if (track.value.durationSeconds <= 0) return 0

  let position = track.value.positionSeconds
  if (track.value.status.toUpperCase() === 'PLAYING' && track.value.timelineUpdatedAt > 0) {
    position += Math.max(0, now.value - track.value.timelineUpdatedAt) * Math.max(0, track.value.playbackRate)
  }

  return Math.min(Math.max(position, 0), track.value.durationSeconds)
})

const progressRatio = computed(() => {
  if (track.value.durationSeconds <= 0) return 0
  return Math.min(Math.max(displayPosition.value / track.value.durationSeconds, 0), 1)
})

const currentTimeLabel = computed(() => formatTime(displayPosition.value))
const durationTimeLabel = computed(() => (track.value.durationSeconds > 0 ? formatTime(track.value.durationSeconds) : '--:--'))
const combinedTimeLabel = computed(() => `${currentTimeLabel.value}/${durationTimeLabel.value}`)
const progressPercent = computed(() => `${progressRatio.value * 100}%`)
const themeClass = computed(() => {
  if (themeMode.value === 'luxury') return 'theme-luxury'
  if (themeMode.value === 'radio') return 'theme-radio'
  return 'theme-dark'
})
const playerScalePercent = computed(() => Math.round(playerScale.value * 100))
const playerTextScalePercent = computed(() => Math.round(playerTextScale.value * 100))
const keyboardShortcuts = [
  { keys: 'Ctrl+Alt+Space', action: '播放 / 暫停' },
  { keys: 'Ctrl+Alt+Right', action: '下一首' },
  { keys: 'Ctrl+Alt+Left', action: '上一首' },
  { keys: 'Ctrl+Alt+Up', action: '音量加' },
  { keys: 'Ctrl+Alt+Down', action: '音量減' },
  { keys: 'Ctrl+Alt+End', action: '靜音' },
  { keys: 'Ctrl+Alt+Home', action: '顯示 / 隱藏懸浮播放器' },
  { keys: 'Ctrl+Alt+P', action: '調整懸浮位置' },
  { keys: 'Ctrl+Alt+H', action: '顯示 / 隱藏控制台' },
  { keys: 'Ctrl+Alt+Q', action: '退出程式' }
]
const controllerShortcuts = computed(() =>
  gamepadBindingRows.map(({ action, label }) => {
    const button = gamepadBindings.value[action]
    const isCustom = button !== DEFAULT_GAMEPAD_BINDINGS[action]
    return {
      actionId: action,
      action: label,
      buttons: ['L3', button] as GraphicalControllerButton[],
      comboLabel: `L3 + ${formatGamepadButton(button)}`,
      isCustom
    }
  })
)
const controllerButtonAssets = computed<Record<GraphicalControllerButton, string>>(() => {
  const isPs = isPlayStation.value
  return {
    L3: xboxL3,
    L3_ACTIVE: xboxL3Active,
    A: isPs ? psCross : xboxA,
    B: isPs ? psCircle : xboxB,
    X: isPs ? psSquare : xboxX,
    DPAD_LEFT: xboxUp,
    DPAD_RIGHT: xboxUp
  }
})

interface LyricChunk {
  text: string
  time: number
  duration: number
}

interface LyricLine {
  time: number
  text: string
  chunks: LyricChunk[]
  hasEnhancedTiming: boolean
}

const parsedLyrics = computed<LyricLine[]>(() => {
  if (!rawLyrics.value) return []
  const lines = rawLyrics.value.split('\n')
  const result: LyricLine[] = []
  
  for (const line of lines) {
    const match = line.match(/^\[(\d{2}):(\d{2}\.\d{2,3})\](.*)/)
    if (match) {
      const min = parseInt(match[1], 10)
      const sec = parseFloat(match[2])
      const lineTime = min * 60 + sec
      const rawText = match[3].trim()
      
      const enhancedRegex = /<(\d{2}):(\d{2}\.\d{2,3})>([^<]*)/g
      const chunks: LyricChunk[] = []
      let enhancedMatch
      let hasEnhancedTiming = false
      let cleanText = ''
      
      if (/<(\d{2}):(\d{2}\.\d{2,3})>/.test(rawText)) {
        hasEnhancedTiming = true
        while ((enhancedMatch = enhancedRegex.exec(rawText)) !== null) {
          const cMin = parseInt(enhancedMatch[1], 10)
          const cSec = parseFloat(enhancedMatch[2])
          const cTime = cMin * 60 + cSec
          const cText = enhancedMatch[3]
          
          if (cText) {
             chunks.push({ text: cText, time: cTime, duration: 0 })
             cleanText += cText
          }
        }
        for (let i = 0; i < chunks.length - 1; i++) {
          chunks[i].duration = Math.max(0.1, chunks[i + 1].time - chunks[i].time)
        }
        if (chunks.length > 0) {
           chunks[chunks.length - 1].duration = 0.5
        }
      } else {
        cleanText = rawText
      }
      
      result.push({ time: lineTime, text: cleanText, chunks, hasEnhancedTiming })
    }
  }
  return result
})

const currentLyricData = computed(() => {
  const currentPos = displayPosition.value
  const lines = parsedLyrics.value
  if (!lines.length) return { text: '', id: 0, startTime: 0, duration: 1, chunks: [] as LyricChunk[], hasEnhancedTiming: false }
  
  let currentLine = lines[0]
  let currentId = 0
  let startTime = 0
  let endTime = 0
  
  for (let i = 0; i < lines.length; i++) {
    if (currentPos >= lines[i].time) {
      currentLine = lines[i]
      currentId = i
      startTime = lines[i].time
      endTime = (i + 1 < lines.length) ? lines[i + 1].time : startTime + 4
    } else {
      break
    }
  }
  
  const maxDuration = 15.0
  const duration = Math.min(endTime - startTime, maxDuration) || 1
  let finalChunks = currentLine.chunks
  
  if (!currentLine.hasEnhancedTiming) {
    const rawChunks = currentLine.text.match(/[A-Za-zÀ-ÿ0-9_'\-]+|\s+|./gu) || []
    finalChunks = rawChunks.map((text, idx) => ({
       text,
       time: startTime + (idx / rawChunks.length) * duration,
       duration: duration / rawChunks.length
    }))
  } else if (finalChunks.length > 0) {
    const lastChunk = finalChunks[finalChunks.length - 1]
    lastChunk.duration = Math.min(Math.max(0.5, endTime - lastChunk.time), maxDuration)
  }
  
  return { text: currentLine.text, id: currentId, startTime, duration, chunks: finalChunks, hasEnhancedTiming: currentLine.hasEnhancedTiming }
})

const activeCharIndex = computed(() => {
  const data = currentLyricData.value
  if (!data.chunks.length) return -1
  const currentPos = displayPosition.value
  let activeIdx = -1
  for (let i = 0; i < data.chunks.length; i++) {
    if (currentPos >= data.chunks[i].time) {
      activeIdx = i
    } else {
      break
    }
  }
  return activeIdx
})

const activeCharProgress = computed(() => {
  const data = currentLyricData.value
  const idx = activeCharIndex.value
  if (idx >= 0 && idx < data.chunks.length) {
    const chunk = data.chunks[idx]
    const elapsed = displayPosition.value - chunk.time
    return Math.max(0, Math.min(1, elapsed / Math.max(0.01, chunk.duration)))
  }
  return 0
})

const currentLyric = computed(() => currentLyricData.value.text)

const currentLyricChars = computed(() => {
  const data = currentLyricData.value
  if (!data.chunks.length) return []
  
  return data.chunks.map((chunk, index) => ({
    char: chunk.text,
    key: `lyric-${data.id}-${index}`
  }))
})

const lyricsStatus = computed(() => {
  if (isFetchingLyrics.value) return '尋找歌詞中...'
  if (!rawLyrics.value) return '未找到此歌曲歌詞'
  if (parsedLyrics.value.some(line => line.hasEnhancedTiming)) return '已取得逐字動態歌詞'
  if (parsedLyrics.value.length > 0) return '已取得逐句動態歌詞'
  return '僅有靜態歌詞'
})

const lyricsStatusStyle = computed(() => {
  if (isFetchingLyrics.value) return { color: '#f59e0b' }
  if (!rawLyrics.value) return { color: '#ef4444' }
  if (parsedLyrics.value.some(line => line.hasEnhancedTiming)) return { color: '#10b981' }
  if (parsedLyrics.value.length > 0) return { color: '#3b82f6' }
  return { color: '#ef4444' }
})

function setShowLyrics(show: boolean): void {
  showLyrics.value = show
  window.forzaApi.sendBackendCommand({ type: 'settings:setShowLyrics', show })
}

function setVolumeMode(mode: 'app' | 'system'): void {
  volumeMode.value = mode
  window.forzaApi.sendBackendCommand({ type: 'settings:setVolumeMode', mode })
}

function normalizeGamepadBindings(value: unknown): GamepadBindings {
  if (!value || typeof value !== 'object') return { ...DEFAULT_GAMEPAD_BINDINGS }

  const candidate = value as Partial<Record<GamepadAction, unknown>>
  const normalized = { ...DEFAULT_GAMEPAD_BINDINGS }
  const assignedButtons = new Set<AssignableControllerButton>()

  for (const { action } of gamepadBindingRows) {
    const button = candidate[action] ?? DEFAULT_GAMEPAD_BINDINGS[action]
    if (!assignableControllerButtons.includes(button as AssignableControllerButton)) {
      return { ...DEFAULT_GAMEPAD_BINDINGS }
    }
    const normalizedButton = button as AssignableControllerButton
    if (assignedButtons.has(normalizedButton)) {
      return { ...DEFAULT_GAMEPAD_BINDINGS }
    }
    normalized[action] = normalizedButton
    assignedButtons.add(normalizedButton)
  }

  return normalized
}

function isGamepadButtonAssigned(button: AssignableControllerButton, currentAction: GamepadAction): boolean {
  return gamepadBindingRows.some(({ action }) => action !== currentAction && gamepadBindings.value[action] === button)
}

function formatGamepadButton(button: AssignableControllerButton): string {
  const labels: Record<AssignableControllerButton, string> = {
    A: 'A',
    B: 'B',
    X: 'X',
    Y: 'Y',
    LB: 'LB',
    RB: 'RB',
    R3: 'R3',
    DPAD_UP: '↑',
    DPAD_DOWN: '↓',
    DPAD_LEFT: '←',
    DPAD_RIGHT: '→',
    LT: 'LT',
    RT: 'RT',
    LS_UP: '左搖桿 ↑',
    LS_DOWN: '左搖桿 ↓',
    LS_LEFT: '左搖桿 ←',
    LS_RIGHT: '左搖桿 →',
    RS_UP: '右搖桿 ↑',
    RS_DOWN: '右搖桿 ↓',
    RS_LEFT: '右搖桿 ←',
    RS_RIGHT: '右搖桿 →'
  }
  return labels[button]
}

function beginGamepadCapture(action: GamepadAction): void {
  listeningGamepadAction.value = listeningGamepadAction.value === action ? null : action
  gamepadCaptureArmed.value = listeningGamepadAction.value !== null
    && !assignableControllerButtons.some((button) => pressedGamepadButtons.value.includes(button))
  if (!listeningGamepadAction.value) {
    gamepadBindingError.value = ''
  } else if (gamepadCaptureArmed.value) {
    gamepadBindingError.value = '請直接按下想與 L3 組合的第二個手把按鍵。'
  } else {
    gamepadBindingError.value = '請先放開目前按住的手把按鍵，再按下新的組合鍵。'
  }
}

async function saveGamepadBinding(action: GamepadAction, button: AssignableControllerButton): Promise<boolean> {
  if (isGamepadButtonAssigned(button, action)) {
    gamepadBindingError.value = `L3 + ${formatGamepadButton(button)} 已經被其他功能使用，請按不同按鍵。`
    return false
  }

  const previousBindings = { ...gamepadBindings.value }
  const nextBindings = {
    ...gamepadBindings.value,
    [action]: button
  }
  gamepadBindings.value = nextBindings
  gamepadBindingError.value = ''
  try {
    await window.forzaApi.sendBackendCommand({
      type: 'settings:setGamepadBindings',
      // Electron IPC cannot clone Vue reactive proxies reliably.
      bindings: { ...nextBindings }
    })
    return true
  } catch (error) {
    console.error('Failed to save gamepad binding:', error)
    gamepadBindings.value = previousBindings
    gamepadBindingError.value = '手把快捷鍵無法傳送到後端，請重新嘗試。'
    return false
  }
}

async function captureGamepadButton(pressed: string[]): Promise<void> {
  const action = listeningGamepadAction.value
  if (!action) return

  const pressedAssignableButtons = assignableControllerButtons.filter((candidate) => pressed.includes(candidate))
  if (!gamepadCaptureArmed.value) {
    if (pressedAssignableButtons.length === 0) {
      gamepadCaptureArmed.value = true
      gamepadBindingError.value = '請直接按下想與 L3 組合的第二個手把按鍵。'
    }
    return
  }

  const button = pressedAssignableButtons[0]
  if (!button) return

  if (await saveGamepadBinding(action, button)) {
    listeningGamepadAction.value = null
    gamepadCaptureArmed.value = false
    gamepadBindingError.value = `已設定為 L3 + ${formatGamepadButton(button)}。`
  }
}

async function resetGamepadBinding(action: GamepadAction): Promise<void> {
  if (await saveGamepadBinding(action, DEFAULT_GAMEPAD_BINDINGS[action])) {
    listeningGamepadAction.value = null
    gamepadCaptureArmed.value = false
    gamepadBindingError.value = '已還原預設手把快捷鍵。'
  }
}

function chooseGamepadProfile(profile: 'xbox' | 'playstation'): void {
  if (!pendingGamepadProfile.value) return

  window.forzaApi.sendBackendCommand({
    type: 'settings:setGamepadProfile',
    deviceKey: pendingGamepadProfile.value.deviceKey,
    profile
  })
  gamepadStatus.value = `已套用${profile === 'xbox' ? '類 Xbox' : '類 PlayStation'}映射：${pendingGamepadProfile.value.deviceName}`
  pendingGamepadProfile.value = null
}

function formatTime(seconds: number): string {
  const total = Math.max(0, Math.floor(seconds))
  const minutes = Math.floor(total / 60)
  const remaining = total % 60
  return `${minutes}:${remaining.toString().padStart(2, '0')}`
}

function command(type: string): void {
  window.forzaApi.sendBackendCommand({ type })
}

function openService(type: 'open:youtube' | 'open:spotify' | 'open:apple' | 'open:kkbox'): void {
  const nextService = type.replace('open:', '') as Exclude<MusicService, 'windows'>
  selectedService.value = nextService
  manualServiceLockUntil = Date.now() + MANUAL_SERVICE_LOCK_MS
  commitAccent(SERVICE_ACCENTS[nextService])
  animateServiceSelection(nextService)
  command(type)
}

function openServiceById(service: Exclude<MusicService, 'windows'>): void {
  openService(`open:${service}` as 'open:youtube' | 'open:spotify' | 'open:apple' | 'open:kkbox')
}

function animateServiceSelection(service: Exclude<MusicService, 'windows'>): void {
  if (view !== 'control' || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  const target = controlRoot.value?.querySelector<HTMLElement>(`.service-button.${service}`)
  if (!target) return

  gsap.fromTo(
    target,
    { scale: 0.985 },
    { scale: 1, duration: 0.38, ease: 'back.out(2.2)', overwrite: 'auto' }
  )
}

function togglePlayerWindow(): void {
  window.forzaApi.togglePlayerWindow()
}

function minimizeToTray(): void {
  window.forzaApi.hideControlWindow()
}

async function togglePositionMode(): Promise<void> {
  positionMode.value = await window.forzaApi.togglePositionMode()
}

function normalizePlayerScale(nextScale: number): number {
  if (!Number.isFinite(nextScale)) return DEFAULT_PLAYER_SCALE
  const clamped = Math.min(Math.max(nextScale, MIN_PLAYER_SCALE), MAX_PLAYER_SCALE)
  return Math.round(clamped * 100) / 100
}

function applyPlayerScale(nextScale: number): void {
  document.documentElement.style.setProperty('--player-scale', normalizePlayerScale(nextScale).toFixed(2))
}

function normalizePlayerTextScale(nextScale: number): number {
  if (!Number.isFinite(nextScale)) return DEFAULT_PLAYER_TEXT_SCALE
  const clamped = Math.min(Math.max(nextScale, MIN_PLAYER_TEXT_SCALE), MAX_PLAYER_TEXT_SCALE)
  return Math.round(clamped * 100) / 100
}

function applyPlayerTextScale(nextScale: number): void {
  document.documentElement.style.setProperty('--player-text-scale', normalizePlayerTextScale(nextScale).toFixed(2))
}

async function setPlayerScale(nextScale: number): Promise<void> {
  const normalizedScale = normalizePlayerScale(nextScale)
  playerScale.value = normalizedScale
  applyPlayerScale(normalizedScale)
  playerScale.value = await window.forzaApi.setPlayerScale(normalizedScale)
  applyPlayerScale(playerScale.value)
}

async function setPlayerTextScale(nextScale: number): Promise<void> {
  const normalizedScale = normalizePlayerTextScale(nextScale)
  playerTextScale.value = normalizedScale
  applyPlayerTextScale(normalizedScale)
  playerTextScale.value = await window.forzaApi.setPlayerTextScale(normalizedScale)
  applyPlayerTextScale(playerTextScale.value)
}

function onPlayerScaleInput(event: Event): void {
  const target = event.target as HTMLInputElement
  void setPlayerScale(Number(target.value))
}

function onPlayerTextScaleInput(event: Event): void {
  const target = event.target as HTMLInputElement
  void setPlayerTextScale(Number(target.value))
}

function adjustPlayerScale(delta: number): void {
  void setPlayerScale(playerScale.value + delta)
}

function adjustPlayerTextScale(delta: number): void {
  void setPlayerTextScale(playerTextScale.value + delta)
}

function resetPlayerScale(): void {
  void setPlayerScale(DEFAULT_PLAYER_SCALE)
}

function resetPlayerTextScale(): void {
  void setPlayerTextScale(DEFAULT_PLAYER_TEXT_SCALE)
}

async function setThemeMode(nextThemeMode: ThemeMode): Promise<void> {
  themeMode.value = await window.forzaApi.setThemeMode(nextThemeMode)
  document.documentElement.style.setProperty('--accent', visibleAccent.value)
}

function mergeTrackArtwork(nextTrack: TrackState): TrackState {
  if (nextTrack.artworkDataUrl) {
    lastArtwork.value = {
      key: nextTrack.artworkKey,
      dataUrl: nextTrack.artworkDataUrl
    }
    return nextTrack
  }

  if (lastArtwork.value && nextTrack.artworkKey === lastArtwork.value.key) {
    return {
      ...nextTrack,
      artworkDataUrl: lastArtwork.value.dataUrl
    }
  }

  if (nextTrack.error || nextTrack.isEmpty) {
    lastArtwork.value = null
  }

  return nextTrack
}

const isFetchingLyrics = ref(false)

function isIdleTrack(nextTrack: TrackState): boolean {
  return nextTrack.isEmpty || nextTrack.status === 'NO_SESSION' || nextTrack.status === 'NO_MEDIA'
}

function setTrack(nextTrack: TrackState): void {
  if (track.value.title !== nextTrack.title) {
    rawLyrics.value = ''
    isFetchingLyrics.value = true
  }
  track.value = nextTrack
  applyAccent(nextTrack)

  if (nextTrack.service === selectedService.value) {
    manualServiceLockUntil = 0
  } else if (nextTrack.service && nextTrack.service !== 'windows' && Date.now() > manualServiceLockUntil) {
    selectedService.value = nextTrack.service
  }

  if (!isIdleTrack(nextTrack)) {
    lastPlayableTrack.value = nextTrack
    lastPlayableAt.value = Date.now()
  }
}



let idleColorTimer: any = undefined

function applyAccent(nextTrack: TrackState): void {
  if (view === 'control') {
    commitAccent(visibleAccent.value)
    return
  }

  if (idleColorTimer) {
    window.clearTimeout(idleColorTimer)
    idleColorTimer = undefined
  }

  const isIdle = isIdleTrack(nextTrack)

  if (isIdle) {
    idleColorTimer = window.setTimeout(() => {
      commitAccent(IDLE_ACCENT)
      idleColorTimer = undefined
    }, IDLE_GRACE_MS)
  } else {
    commitAccent(nextTrack.accent || '#ff0033')
  }
}

function commitAccent(color: string): void {
  const normalizedAccent = color.toLowerCase()
  const readableAccent =
    themeMode.value === 'dark' && (normalizedAccent === '#111111' || normalizedAccent === '#000000')
      ? '#f8fafc'
      : color
  document.documentElement.style.setProperty('--accent', readableAccent)
}

let removeListener: (() => void) | undefined
let removePositionModeListener: (() => void) | undefined
let removeThemeModeListener: (() => void) | undefined
let removePlayerScaleListener: (() => void) | undefined
let removePlayerTextScaleListener: (() => void) | undefined
let clock: number | undefined
let idleTimer: number | undefined

function runControlEntranceAnimation(): void {
  if (view !== 'control' || !controlRoot.value) return

  controlAnimationContext?.revert()
  controlAnimationContext = gsap.context(() => {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reducedMotion) return

    const timeline = gsap.timeline({ defaults: { ease: 'power3.out' } })
    timeline
      .from('.hero-copy', { y: 18, duration: 0.62 })
      .from('.hero-side', { y: 18, duration: 0.58 }, '-=0.4')
      .from('.source-panel', { y: 18, duration: 0.48 }, '-=0.26')
      .from('.service-button', { y: 16, scale: 0.985, duration: 0.46, stagger: 0.07 }, '-=0.18')
      .from('.now-playing, .size-panel, .compact-panel', { y: 14, duration: 0.44, stagger: 0.05 }, '-=0.28')
  }, controlRoot.value)
}

function refreshActiveServiceAnimation(): void {
  activeServiceTween?.kill()
  activeServiceTween = null

  if (view !== 'control' || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  const target = controlRoot.value?.querySelector<HTMLElement>('.service-button.active-service')
  if (!target) return

  activeServiceTween = gsap.to(target, {
    y: -3,
    scale: 1.012,
    duration: 1.7,
    ease: 'sine.inOut',
    repeat: -1,
    yoyo: true
  })
}

onMounted(async () => {
  await nextTick()
  runControlEntranceAnimation()
  refreshActiveServiceAnimation()

  themeMode.value = await window.forzaApi.getThemeMode()
  playerScale.value = await window.forzaApi.getPlayerScale()
  playerTextScale.value = await window.forzaApi.getPlayerTextScale()
  document.documentElement.style.setProperty('--accent', visibleAccent.value)
  applyPlayerScale(playerScale.value)
  applyPlayerTextScale(playerTextScale.value)

  removeListener = window.forzaApi.onBackendEvent((event: BackendEvent) => {
    if (event.type === 'backend:ready') {
      backendStatus.value = `v${event.version ?? ''}`
      if (event.settings?.volume_mode) {
        volumeMode.value = event.settings.volume_mode
      }
      if (event.settings?.show_lyrics !== undefined) {
        showLyrics.value = event.settings.show_lyrics
      }
      if (event.settings?.gamepad_bindings) {
        const normalizedBindings = normalizeGamepadBindings(event.settings.gamepad_bindings)
        gamepadBindings.value = normalizedBindings
        confirmedGamepadBindings.value = { ...normalizedBindings }
      }
    } else if (event.type === 'settings:update' && event.settings?.gamepad_bindings) {
      const normalizedBindings = normalizeGamepadBindings(event.settings.gamepad_bindings)
      gamepadBindings.value = normalizedBindings
      confirmedGamepadBindings.value = { ...normalizedBindings }
    } else if (event.type === 'settings:error' && event.message) {
      gamepadBindings.value = { ...confirmedGamepadBindings.value }
      listeningGamepadAction.value = null
      gamepadCaptureArmed.value = false
      gamepadBindingError.value = event.message
    } else if (event.type === 'track:update' && event.track) {
      const nextTrack = mergeTrackArtwork(event.track)
      setTrack(nextTrack)
    } else if (event.type === 'volume:update' && typeof event.volume === 'number') {
      appVolume.value = event.volume
      if (volumeHideTimer) window.clearTimeout(volumeHideTimer)
      volumeHideTimer = window.setTimeout(() => {
        appVolume.value = null
      }, 2500)
    } else if (event.type === 'lyrics:update') {
      rawLyrics.value = event.lyrics || ''
      isFetchingLyrics.value = false
    } else if (event.type === 'command') {
      if (event.command === 'toggle_position_mode') {
        lastMessage.value = positionMode.value ? '可拖曳左上角懸浮播放器調整位置' : '懸浮播放器位置已儲存'
      }
    } else if (event.type === 'gamepad:status' && event.message) {
      gamepadStatus.value = event.message
    } else if (event.type === 'gamepad:profileRequired' && event.deviceKey && event.deviceName) {
      pendingGamepadProfile.value = {
        deviceKey: event.deviceKey,
        deviceName: event.deviceName
      }
    } else if (event.type === 'gamepad:inputs' && event.pressed) {
      pressedGamepadButtons.value = event.pressed
      void captureGamepadButton(event.pressed)
    } else if (event.type === 'hotkey:error' && event.message) {
      lastMessage.value = event.message
    } else if (event.type === 'backend:error' && event.message) {
      backendStatus.value = '後端啟動失敗'
      lastMessage.value = event.message
    } else if (event.type === 'backend:exit') {
      backendStatus.value = `後端已停止 (${event.code ?? 'unknown'})`
      if (event.message) {
        lastMessage.value = event.message
      }
    } else if (event.type === 'backend:stderr' && event.message) {
      console.warn('Backend stderr:', event.message)
    } else if (event.message) {
      lastMessage.value = event.message
    }
  })

  removePositionModeListener = window.forzaApi.onPositionMode((event) => {
    positionMode.value = event.enabled
    lastMessage.value = event.enabled ? '可拖曳左上角懸浮播放器調整位置' : '懸浮播放器位置已儲存'
  })

  removeThemeModeListener = window.forzaApi.onThemeMode((event) => {
    themeMode.value = event.themeMode
    document.documentElement.style.setProperty('--accent', visibleAccent.value)
  })

  removePlayerScaleListener = window.forzaApi.onPlayerScale((event) => {
    playerScale.value = normalizePlayerScale(event.scale)
    applyPlayerScale(playerScale.value)
  })

  removePlayerTextScaleListener = window.forzaApi.onPlayerTextScale((event) => {
    playerTextScale.value = normalizePlayerTextScale(event.scale)
    applyPlayerTextScale(playerTextScale.value)
  })

  const tick = () => {
    now.value = Date.now() / 1000
    clock = window.requestAnimationFrame(tick)
  }
  tick()
})

onUnmounted(() => {
  removeListener?.()
  removePositionModeListener?.()
  removeThemeModeListener?.()
  removePlayerScaleListener?.()
  removePlayerTextScaleListener?.()
  clearSpotifyTipTimer()
  activeServiceTween?.kill()
  controlAnimationContext?.revert()
  if (idleTimer) window.clearTimeout(idleTimer)
  if (clock) window.cancelAnimationFrame(clock)
})

watch(activeService, async () => {
  await nextTick()
  refreshActiveServiceAnimation()
})

watch(visibleAccent, (nextAccent) => {
  document.documentElement.style.setProperty('--accent', nextAccent)
})
</script>

<template>
  <main v-if="view === 'control'" ref="controlRoot" class="control-shell" :class="themeClass">
    <LiquidRuptureBackground v-if="themeMode === 'luxury'" :accent="visibleAccent" :theme-mode="themeMode" />

    <aside class="luxury-sidebar" aria-label="Luxury showroom navigation">
      <div class="brand-mark">
        <Gem :size="22" />
      </div>
      <nav>
        <a href="#source">Showroom</a>
        <a href="#now-playing">Signature</a>
        <a href="#controls">Concierge</a>
        <a href="#membership">Private</a>
      </nav>
    </aside>

    <div class="control-content">
      <header class="app-header-row">
        <ControlThemeToolbar
          :theme-mode="themeMode"
          :backend-status="backendStatus"
          :accent="visibleAccent"
          @theme-change="setThemeMode"
        />
      </header>

      <section class="hero-band">
        <div class="hero-copy">
          <div class="brand-title">
            <p class="eyebrow">Gaming Music Overlay</p>
            <h1>音樂<span class="hero-title-accent">懸浮</span>播放器</h1>
          </div>
          <p class="summary">在遊戲中自由掌控音樂，無需切出視窗。透過 Forza 歌曲資訊與播放控制，保持沉浸體驗。</p>
        </div>
        <div class="hero-side">
          <SponsorSupportPanel :sponsor-url="SPONSOR_URL" :qr-src="bmcQr" />
        </div>
      </section>

      <ServiceSourcePanel
        :services="sourceServices"
        :active-service="activeService"
        :show-spotify-tip="showSpotifyTip"
        @open-service="openServiceById"
        @open-spotify-tip="openSpotifyTip"
        @close-spotify-tip="closeSpotifyTip"
      />

      <NowPlayingPanel
        :artwork-key="track.artworkKey"
        :artwork-data-url="track.artworkDataUrl"
        :is-idle="isIdle"
        :source-label="sourceDisplayLabel"
        :status-label="track.status.replaceAll('_', ' ')"
        :title-chars="titleChars"
        :artist-chars="artistChars"
        :track-content-key="trackContentKey"
        :current-time-label="currentTimeLabel"
        :duration-time-label="durationTimeLabel"
        :progress-ratio="progressRatio"
      />

    <section id="controls" class="action-grid">
      <button type="button" @click="command('media:previous')"><ChevronsLeft :size="20" />上一首</button>
      <button type="button" @click="command('media:playPause')"><CirclePlay :size="20" />播放 / 暫停</button>
      <button type="button" @click="command('media:next')"><ChevronsRight :size="20" />下一首</button>
      <button type="button" @click="togglePlayerWindow"><MonitorUp :size="20" />顯示懸浮播放器</button>
      <button :class="{ active: positionMode }" type="button" @click="togglePositionMode">
        <Move :size="20" />調整懸浮位置
      </button>
    </section>

    <section class="panel size-panel">
      <div class="section-title">
        <MonitorUp :size="18" />
        <div>
          <h2>懸浮播放器大小</h2>
          <p>調整左上角播放器縮放與文字大小，會立即套用並記住設定。</p>
        </div>
      </div>
      <div class="scale-control-stack">
        <div class="scale-control-row">
          <span class="scale-control-label">整體大小</span>
          <div class="scale-control">
            <button type="button" aria-label="縮小懸浮播放器" @click="adjustPlayerScale(-PLAYER_SCALE_STEP)">
              <Minus :size="17" />
            </button>
            <label class="scale-slider" for="player-scale">
              <input
                id="player-scale"
                type="range"
                :min="MIN_PLAYER_SCALE"
                :max="MAX_PLAYER_SCALE"
                :step="PLAYER_SCALE_STEP"
                :value="playerScale"
                @input="onPlayerScaleInput"
              />
              <span>{{ playerScalePercent }}%</span>
            </label>
            <button type="button" aria-label="放大懸浮播放器" @click="adjustPlayerScale(PLAYER_SCALE_STEP)">
              <Plus :size="17" />
            </button>
            <button type="button" class="scale-reset" @click="resetPlayerScale">
              <RotateCcw :size="16" />
              重設
            </button>
          </div>
        </div>
        <div class="scale-control-row">
          <span class="scale-control-label">文字大小</span>
          <div class="scale-control">
            <button type="button" aria-label="縮小懸浮播放器文字" @click="adjustPlayerTextScale(-PLAYER_TEXT_SCALE_STEP)">
              <Minus :size="17" />
            </button>
            <label class="scale-slider" for="player-text-scale">
              <input
                id="player-text-scale"
                type="range"
                :min="MIN_PLAYER_TEXT_SCALE"
                :max="MAX_PLAYER_TEXT_SCALE"
                :step="PLAYER_TEXT_SCALE_STEP"
                :value="playerTextScale"
                @input="onPlayerTextScaleInput"
              />
              <span>{{ playerTextScalePercent }}%</span>
            </label>
            <button type="button" aria-label="放大懸浮播放器文字" @click="adjustPlayerTextScale(PLAYER_TEXT_SCALE_STEP)">
              <Plus :size="17" />
            </button>
            <button type="button" class="scale-reset" @click="resetPlayerTextScale">
              <RotateCcw :size="16" />
              重設
            </button>
          </div>
        </div>
      </div>
    </section>

    <section class="panel compact-panel">
      <div class="section-title">
        <Gamepad2 :size="18" />
        <div>
          <h2>遊戲中控制與音量設定</h2>
          <p>{{ gamepadStatus }}</p>
        </div>
      </div>
      <div v-if="pendingGamepadProfile" class="gamepad-profile-prompt">
        <div>
          <b>請選擇副廠手把類型</b>
          <p>無法可靠辨識「{{ pendingGamepadProfile.deviceName }}」，請選擇它使用哪一種按鍵排列。</p>
        </div>
        <button type="button" @click="chooseGamepadProfile('xbox')">類 Xbox 手把</button>
        <button type="button" @click="chooseGamepadProfile('playstation')">類 PlayStation 手把</button>
      </div>
      <div class="volume-mode-row">
        <span>音量控制目標：</span>
        <div class="theme-toggle">
          <button :class="{ selected: volumeMode === 'app' }" type="button" @click="setVolumeMode('app')">
            目前的音樂網頁 / 應用程式
          </button>
          <button :class="{ selected: volumeMode === 'system' }" type="button" @click="setVolumeMode('system')">
            Windows 系統主音量
          </button>
        </div>
      </div>
      <div class="volume-mode-row">
        <span>顯示動態歌詞：</span>
        <div class="theme-toggle">
          <button :class="{ selected: showLyrics }" type="button" @click="setShowLyrics(true)">開啟</button>
          <button :class="{ selected: !showLyrics }" type="button" @click="setShowLyrics(false)">關閉</button>
        </div>
        <span v-if="track && track.title" class="lyrics-status-indicator" :style="lyricsStatusStyle">
          ● {{ lyricsStatus }}
        </span>
      </div>
      <div class="control-guides">
        <div class="guide-column">
          <div class="guide-heading">鍵盤快捷鍵</div>
          <div class="shortcut-grid keyboard-grid">
            <template v-for="shortcut in keyboardShortcuts" :key="shortcut.keys">
              <span class="key-pill">{{ shortcut.keys }}</span>
              <b>{{ shortcut.action }}</b>
            </template>
          </div>
        </div>
        <div class="guide-column">
          <div class="guide-heading">手把組合鍵</div>
          <p class="guide-note">按住 L3（左搖桿按下），再按下對應按鍵執行下列功能。</p>
          <div class="controller-grid">
            <div v-for="(shortcut, shortcutIdx) in controllerShortcuts" :key="shortcut.actionId" class="controller-row">
              <span v-if="shortcut.isCustom" class="custom-controller-combo">{{ shortcut.comboLabel }}</span>
              <span v-else class="controller-combo" :aria-label="shortcut.comboLabel">
                <span
                  v-for="button in shortcut.buttons"
                  :key="button"
                  class="button-wrapper"
                >
                  <img
                    :class="['xbox-button-img', button.toLowerCase(), { active: pressedGamepadButtons.includes(button) }]"
                    :src="button === 'L3' && pressedGamepadButtons.includes('L3') ? controllerButtonAssets['L3_ACTIVE'] : controllerButtonAssets[button]"
                    :alt="button"
                  />
                  <!-- Permanent tooltip on L3 of the first row -->
                  <span v-if="shortcutIdx === 0 && button === 'L3'" class="permanent-tooltip">
                    左蘑菇頭按下
                  </span>
                </span>
              </span>
              <b>{{ shortcut.action }}</b>
              <span class="controller-row-actions">
                <button
                  type="button"
                  class="controller-customize-button"
                  :class="{ listening: listeningGamepadAction === shortcut.actionId }"
                  @click="beginGamepadCapture(shortcut.actionId)"
                >
                  {{ listeningGamepadAction === shortcut.actionId ? '等待按鍵...' : '自訂' }}
                </button>
                <button
                  v-if="shortcut.isCustom"
                  type="button"
                  class="controller-reset-button"
                  @click="resetGamepadBinding(shortcut.actionId)"
                >
                  還原
                </button>
              </span>
            </div>
          </div>
          <p v-if="gamepadBindingError" class="binding-error">{{ gamepadBindingError }}</p>
        </div>
      </div>
      <p v-if="lastMessage" class="notice">{{ lastMessage }}</p>
    </section>

    <section id="membership" class="membership-cta panel">
      <div>
        <p class="eyebrow">Private Listening Suite</p>
        <h2>專屬沉浸模式</h2>
        <p>奢華玻璃主題提供更柔和的視覺深度、精品展示感和遊戲內低干擾辨識度。</p>
      </div>
      <button type="button" @click="togglePlayerWindow">
        <Sparkles :size="18" />
        啟用展示視窗
      </button>
    </section>

    <section class="footer-actions">
      <button type="button" @click="command('media:volumeDown')"><Volume2 :size="18" />音量減</button>
      <button type="button" @click="command('media:volumeUp')"><Volume2 :size="18" />音量加</button>
      <button type="button" @click="command('media:mute')"><VolumeX :size="18" />靜音</button>
      <button type="button" @click="minimizeToTray"><Minimize2 :size="18" />縮小至工作列</button>
      <button class="danger" type="button" @click="command('app:quit')"><Power :size="18" />退出</button>
    </section>

    <footer class="app-footer">
      <span class="footer-item footer-author">
        <span class="footer-label">作者：</span>
        <span class="author-name">Scott Lin</span>
        <span class="visual-signature" aria-hidden="true">
          <span class="signature-mark">SL</span>
          <span class="signature-line"></span>
        </span>
      </span>
      <span class="footer-item">
        <span class="footer-label">贊助我：</span>
        <a :href="SPONSOR_URL" target="_blank" rel="noreferrer">
          https://buymeacoffee.com/scott5497
        </a>
      </span>
      <span class="footer-item">
        <span class="footer-label">聯繫我：</span>
        <a href="mailto:scott5497ify@gmail.com">scott5497ify@gmail.com</a>
      </span>
    </footer>
    </div>
  </main>

  <main 
    v-else 
    class="player-shell" 
    :class="themeClass"
  >
    <!-- Radio (borderless) player -->
    <section
      v-if="themeMode === 'radio'"
      :class="['radio-player', { 'position-mode': positionMode, idle: isIdle }]"
    >
      <div class="radio-pulse" :class="{ playing: !isIdle && track.status.toUpperCase() === 'PLAYING' }"></div>
      <div class="radio-artwork" :class="{ idle: isIdle }">
        <Transition name="art-swap" mode="out-in">
          <img v-if="track.artworkDataUrl" :key="track.artworkKey" :src="track.artworkDataUrl" alt="Album artwork" />
          <div v-else :key="isIdle ? 'idle-radio-artwork' : 'empty-radio-artwork'" class="artwork-placeholder">
            <Radio :size="20" />
          </div>
        </Transition>
      </div>
      <div class="radio-body">
        <div class="radio-freq">
          <span class="radio-dot"></span>
          <span>{{ serviceName }}</span>
        </div>
        <Transition name="text-crossfade" mode="out-in">
          <div :key="trackContentKey" class="radio-track">
            <span class="radio-title">
              <span
                v-for="(char, index) in titleChars"
                :key="index + '-' + char"
                class="char-flow"
                :style="{ animationDelay: `${index * 16}ms` }"
              >{{ char }}</span>
            </span>
            <span class="radio-artist">
              <span
                v-for="(char, index) in artistChars"
                :key="index + '-' + char"
                class="char-flow"
                :style="{ animationDelay: `${index * 10}ms` }"
              >{{ char }}</span>
            </span>
          </div>
        </Transition>
      </div>
      <span class="radio-time">{{ combinedTimeLabel }}</span>
      <div v-if="positionMode" class="drag-chip">拖曳調整位置</div>
      <div class="radio-progress">
        <div :style="{ width: progressPercent }"></div>
      </div>

      <Transition name="fade">
        <div v-if="appVolume !== null" class="player-volume-overlay" :style="{ '--vol-percent': appVolume }">
          <svg class="player-volume-border-svg" viewBox="0 0 548 178" preserveAspectRatio="none">
            <rect class="lightning-border-active" x="2" y="2" width="544" height="174" rx="24" ry="24" pathLength="100" />
          </svg>
          <div class="player-volume-badge">
            <Volume2 :size="14" class="player-volume-badge-icon" />
            <span>{{ Math.round(appVolume * 100) }}%</span>
          </div>
        </div>
      </Transition>
    </section>

    <!-- Standard dark / luxury player -->
    <section v-else :class="[themeMode === 'luxury' ? 'liquid-player' : 'floating-card', { 'position-mode': positionMode, idle: isIdle }]">
      <div class="mini-artwork" :class="{ idle: isIdle }">
        <Transition name="art-swap" mode="out-in">
          <img v-if="track.artworkDataUrl" :key="track.artworkKey" :src="track.artworkDataUrl" alt="Album artwork" />
          <div v-else :key="isIdle ? 'idle-mini-artwork' : 'empty-mini-artwork'" class="artwork-placeholder">
            <Music2 :size="28" />
          </div>
        </Transition>
      </div>
      <div class="floating-copy">
        <div class="floating-meta">
          <span class="source-dot"></span>
          <span>{{ serviceName }}</span>
          <strong>{{ track.status.replaceAll('_', ' ') }}</strong>
        </div>
        <div class="floating-text-frame">
          <Transition name="text-crossfade" mode="out-in">
            <div :key="trackContentKey" class="floating-text-block">
              <h1>
                <span
                  v-for="(char, index) in titleChars"
                  :key="index + '-' + char"
                  class="char-flow"
                  :style="{ animationDelay: `${index * 16}ms` }"
                >{{ char }}</span>
              </h1>
              <p>
                <span
                  v-for="(char, index) in artistChars"
                  :key="index + '-' + char"
                  class="char-flow"
                  :style="{ animationDelay: `${index * 10}ms` }"
                >{{ char }}</span>
              </p>
            </div>
          </Transition>
        </div>
      </div>
      <div v-if="positionMode" class="drag-chip">拖曳調整位置</div>
      <div class="floating-time combined-time">
        {{ combinedTimeLabel }}
      </div>
      <div class="floating-time split-time">
        <span>{{ currentTimeLabel }}</span>
        <span>{{ durationTimeLabel }}</span>
      </div>
      <div class="floating-progress">
        <div :style="{ width: progressPercent }"></div>
        <span class="progress-thumb" :style="{ left: progressPercent }"></span>
      </div>

      <Transition name="fade">
        <div v-if="appVolume !== null" class="player-volume-overlay" :style="{ '--vol-percent': appVolume }">
          <div class="player-volume-border"></div>
          <div class="player-volume-badge">
            <Volume2 :size="14" class="player-volume-badge-icon" />
            <span>{{ Math.round(appVolume * 100) }}%</span>
          </div>
        </div>
      </Transition>
    </section>

    <Transition name="tip-fade">
      <div v-if="showLyrics && currentLyric" class="player-lyrics-external">
        <span
          v-for="(item, index) in currentLyricChars"
          :key="item.key"
          class="char-flow-wrapper"
          :style="{ animationDelay: `${index * 16}ms` }"
        >
          <span 
            class="char-inner"
            :class="{
              'sung': index < activeCharIndex || (index === activeCharIndex && activeCharProgress >= 1),
              'singing': index === activeCharIndex && activeCharProgress < 1 && !currentLyricData.hasEnhancedTiming,
              'singing-enhanced': index === activeCharIndex && activeCharProgress < 1 && currentLyricData.hasEnhancedTiming
            }"
            :style="(index === activeCharIndex) ? { '--lyric-progress': `${activeCharProgress * 100}%`, '--lyric-progress-raw': activeCharProgress } : {}"
          >{{ item.char }}</span>
        </span>
      </div>
    </Transition>

    <!-- SVG Lightning Filter (Performance Optimized) -->
    <svg style="width:0;height:0;position:absolute;pointer-events:none;" aria-hidden="true">
      <filter id="lightning-distortion" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">
        <!-- Single noise source (numOctaves=2 is much faster than 3 or 4) -->
        <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="2" result="noise">
          <animate attributeName="baseFrequency" values="0.04;0.05;0.03;0.045;0.04" dur="0.15s" repeatCount="indefinite" />
        </feTurbulence>
        
        <!-- Medium jagged main path -->
        <feDisplacementMap in="SourceGraphic" in2="noise" scale="12" xChannelSelector="R" yChannelSelector="G" result="main" />
        
        <!-- Wild branches -->
        <feDisplacementMap in="SourceGraphic" in2="noise" scale="35" xChannelSelector="B" yChannelSelector="A" result="branches_raw" />
        
        <!-- Dim branches -->
        <feComponentTransfer in="branches_raw" result="branches">
          <feFuncA type="linear" slope="0.4" />
        </feComponentTransfer>

        <!-- Combine: Branches, Main, and the un-distorted perfect core -->
        <feMerge>
          <feMergeNode in="branches" />
          <feMergeNode in="main" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </svg>
  </main>
</template>
