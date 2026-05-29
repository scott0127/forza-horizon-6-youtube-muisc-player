<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import {
  ChevronsLeft,
  ChevronsRight,
  CirclePlay,
  ExternalLink,
  Gamepad2,
  Gem,
  MonitorUp,
  Moon,
  Move,
  Music2,
  Minus,
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
import xboxDown from './assets/xbox-down.png'
import xboxL3 from './assets/xbox-l3.png'
import xboxL3Active from './assets/xbox-l3-active.png'
import xboxUp from './assets/xbox-up.png'
import xboxX from './assets/xbox-x.svg'
import psCross from './assets/ps-cross.svg'
import psCircle from './assets/ps-circle.svg'
import psSquare from './assets/ps-square.svg'
import type { BackendEvent, ThemeMode, TrackState } from './types'

const IDLE_ACCENT = '#8b5cf6'
const IDLE_GRACE_MS = 2200
const SPONSOR_URL = 'https://buymeacoffee.com/scott5497'
const DEFAULT_PLAYER_SCALE = 0.8
const MIN_PLAYER_SCALE = 0.6
const MAX_PLAYER_SCALE = 1
const PLAYER_SCALE_STEP = 0.05
type ControllerButton = 'L3' | 'L3_ACTIVE' | 'A' | 'B' | 'X' | 'UP' | 'DOWN'
const view = new URLSearchParams(window.location.search).get('view') === 'player' ? 'player' : 'control'
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
const pressedGamepadButtons = ref<string[]>([])
const showSpotifyTip = ref(localStorage.getItem('forza:show-spotify-tip') !== 'false')
function closeSpotifyTip(): void {
  showSpotifyTip.value = false
  localStorage.setItem('forza:show-spotify-tip', 'false')
}

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

const isIdle = computed(() => track.value.isEmpty || track.value.status === 'NO_SESSION' || track.value.status === 'NO_MEDIA')
const accent = computed(() => (isIdle.value ? IDLE_ACCENT : track.value.accent || '#ff0033'))
const visibleAccent = computed(() => {
  const nextAccent = accent.value.toLowerCase()
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
  if (track.value.service === 'spotify') return 'Spotify'
  if (track.value.service === 'youtube') return 'YouTube Music'
  return 'Windows Media'
})

const displayTitle = computed(() => {
  if (track.value.error) return '讀取媒體資訊失敗'
  if (track.value.isEmpty || !track.value.title) return '等待音樂播放'
  return track.value.title
})

const displayArtist = computed(() => {
  if (track.value.error) return track.value.error
  if (track.value.isEmpty) return '請先登入並播放 YouTube Music、Spotify 或 Apple Music'
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
const controllerShortcuts: Array<{ buttons: ControllerButton[]; action: string }> = [
  { buttons: ['L3', 'A'], action: '播放 / 暫停' },
  { buttons: ['L3', 'B'], action: '下一首' },
  { buttons: ['L3', 'X'], action: '上一首' },
  { buttons: ['L3', 'UP'], action: '調高音量' },
  { buttons: ['L3', 'DOWN'], action: '調低音量' }
]
const controllerButtonAssets = computed<Record<ControllerButton, string>>(() => {
  const isPs = isPlayStation.value
  return {
    L3: xboxL3,
    L3_ACTIVE: xboxL3Active,
    A: isPs ? psCross : xboxA,
    B: isPs ? psCircle : xboxB,
    X: isPs ? psSquare : xboxX,
    UP: xboxUp,
    DOWN: xboxDown
  }
})

function formatTime(seconds: number): string {
  const total = Math.max(0, Math.floor(seconds))
  const minutes = Math.floor(total / 60)
  const remaining = total % 60
  return `${minutes}:${remaining.toString().padStart(2, '0')}`
}

function command(type: string): void {
  window.forzaApi.sendBackendCommand({ type })
}

function openService(type: 'open:youtube' | 'open:spotify' | 'open:apple'): void {
  command(type)
}

function togglePlayerWindow(): void {
  window.forzaApi.togglePlayerWindow()
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

async function setPlayerScale(nextScale: number): Promise<void> {
  const normalizedScale = normalizePlayerScale(nextScale)
  playerScale.value = normalizedScale
  applyPlayerScale(normalizedScale)
  playerScale.value = await window.forzaApi.setPlayerScale(normalizedScale)
  applyPlayerScale(playerScale.value)
}

function onPlayerScaleInput(event: Event): void {
  const target = event.target as HTMLInputElement
  void setPlayerScale(Number(target.value))
}

function adjustPlayerScale(delta: number): void {
  void setPlayerScale(playerScale.value + delta)
}

function resetPlayerScale(): void {
  void setPlayerScale(DEFAULT_PLAYER_SCALE)
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

function isIdleTrack(nextTrack: TrackState): boolean {
  return nextTrack.isEmpty || nextTrack.status === 'NO_SESSION' || nextTrack.status === 'NO_MEDIA'
}

function setTrack(nextTrack: TrackState): void {
  track.value = nextTrack
  applyAccent(nextTrack)

  if (!isIdleTrack(nextTrack)) {
    lastPlayableTrack.value = nextTrack
    lastPlayableAt.value = Date.now()
  }
}



let idleColorTimer: any = undefined

function applyAccent(nextTrack: TrackState): void {
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
let clock: number | undefined
let idleTimer: number | undefined

onMounted(async () => {
  themeMode.value = await window.forzaApi.getThemeMode()
  playerScale.value = await window.forzaApi.getPlayerScale()
  document.documentElement.style.setProperty('--accent', visibleAccent.value)
  applyPlayerScale(playerScale.value)

  removeListener = window.forzaApi.onBackendEvent((event: BackendEvent) => {
    if (event.type === 'backend:ready') {
      backendStatus.value = `v${event.version ?? ''}`
    } else if (event.type === 'track:update' && event.track) {
      const nextTrack = mergeTrackArtwork(event.track)
      setTrack(nextTrack)
    } else if (event.type === 'gamepad:status' && event.message) {
      gamepadStatus.value = event.message
    } else if (event.type === 'gamepad:inputs' && event.pressed) {
      pressedGamepadButtons.value = event.pressed
    } else if (event.type === 'hotkey:error' && event.message) {
      lastMessage.value = event.message
    } else if (event.type === 'backend:exit') {
      backendStatus.value = `後端已停止 (${event.code ?? 'unknown'})`
    } else if (event.type === 'command' && event.command === 'toggle_position_mode') {
      lastMessage.value = positionMode.value ? '可拖曳左上角懸浮播放器調整位置' : '懸浮播放器位置已儲存'
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

  clock = window.setInterval(() => {
    now.value = Date.now() / 1000
  }, 250)
})

onUnmounted(() => {
  removeListener?.()
  removePositionModeListener?.()
  removeThemeModeListener?.()
  removePlayerScaleListener?.()
  if (idleTimer) window.clearTimeout(idleTimer)
  if (clock) window.clearInterval(clock)
})
</script>

<template>
  <main v-if="view === 'control'" class="control-shell" :class="themeClass">
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
      <section class="hero-band">
        <div>
          <p class="eyebrow">Forza Music</p>
          <h1>音樂懸浮播放器</h1>
          <p class="summary">啟動音樂服務後進入 Forza，歌曲資訊與控制會留在遊戲內，不需要切出視窗。</p>
        </div>
        <div class="toolbar-cluster">
          <div class="theme-toggle" aria-label="主題切換">
            <button :class="{ selected: themeMode === 'dark' }" type="button" @click="setThemeMode('dark')">
              <Moon :size="15" />
              暗黑
            </button>
            <button :class="{ selected: themeMode === 'luxury' }" type="button" @click="setThemeMode('luxury')">
              <Sparkles :size="15" />
              Liquid Glass
            </button>
            <button :class="{ selected: themeMode === 'radio' }" type="button" @click="setThemeMode('radio')">
              <Radio :size="15" />
              無邊框電台
            </button>
          </div>
          <div class="status-pill" :style="{ borderColor: visibleAccent, color: visibleAccent }">
            <Radio :size="16" />
            {{ backendStatus }}
          </div>
        </div>
      </section>

      <section class="sponsor-panel panel">
        <div class="sponsor-copy">
          <p class="eyebrow">贊助支持</p>
          <h2>支持 Forza Music 持續更新</h2>
          <p>這個工具是免費的。如果想支持我，或是工具有幫到你，可以請還在讀碩士的我喝杯咖啡<br> QR Code 可掃描，按鈕會開啟贊助頁。</p>
        </div>
        <div class="sponsor-actions">
          <img class="sponsor-qr" :src="bmcQr" alt="Buy Me a Coffee QR Code" />
          <a class="sponsor-button" :href="SPONSOR_URL" target="_blank" rel="noreferrer">
            贊助我
          </a>
        </div>
      </section>

    <section id="source" class="panel source-panel">
      <div class="section-title">
        <Music2 :size="18" />
        <div>
          <h2>選擇音樂來源</h2>
          <p>按下服務後會開啟對應網站，並自動套用紅色、綠色或黑色主題。</p>
        </div>
      </div>
      <div class="service-grid">
        <button class="service-button youtube" type="button" @click="openService('open:youtube')">
          <ExternalLink :size="19" />
          開啟 YouTube Music
        </button>
        <button class="service-button spotify" type="button" @click="openService('open:spotify')">
          <ExternalLink :size="19" />
          開啟 Spotify
        </button>
        <div class="service-button-wrapper">
          <button class="service-button apple" type="button" @click="openService('open:apple')">
            <ExternalLink :size="19" />
            開啟 Apple Music
          </button>
          
          <Transition name="tip-fade">
            <div v-if="showSpotifyTip" class="spotify-tip-box">
              <div class="tip-header">
                <span class="tip-badge">💡 Spotify Premium 遙控功能</span>
                <button class="tip-close-btn" type="button" aria-label="關閉提示" @click.stop="closeSpotifyTip">
                  &times;
                </button>
              </div>
              <p class="tip-text">提醒您！有 Spotify Premium 即可在任何裝置同步遙控控制此電台</p>
            </div>
          </Transition>

          <!-- Ultra-sleek technical dashed curved line with glowing pulse dot -->
          <Transition name="tip-fade">
            <svg v-if="showSpotifyTip" class="spotify-tip-arrow" viewBox="0 0 160 50" preserveAspectRatio="none">
              <defs>
                <linearGradient id="lineGrad" x1="0%" y1="100%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#1ed760" stop-opacity="1" />
                  <stop offset="100%" stop-color="#1ed760" stop-opacity="0.4" />
                </linearGradient>
                <marker id="tip-arrowhead-small" markerWidth="4" markerHeight="4" refX="1" refY="2" orient="auto">
                  <polygon points="0 0, 4 2, 0 4" fill="#1ed760" />
                </marker>
              </defs>
              <!-- Dashed curved connector from Spotify (left side) to Tip Box bottom (right side) -->
              <path d="M -80 44 C -40 25, 0 12, 40 8" fill="none" stroke="url(#lineGrad)" stroke-width="1.2" stroke-dasharray="3 3" marker-end="url(#tip-arrowhead-small)" />
              <!-- Pulsing source node at the Spotify end -->
              <circle cx="-80" cy="44" r="3.5" fill="#1ed760" />
              <circle class="pulse-node" cx="-80" cy="44" r="7" fill="none" stroke="#1ed760" stroke-width="1" />
            </svg>
          </Transition>
        </div>
      </div>
    </section>

    <section id="now-playing" class="now-playing panel">
      <div class="artwork" :class="{ idle: isIdle }">
        <Transition name="art-swap" mode="out-in">
          <img v-if="track.artworkDataUrl" :key="track.artworkKey" :src="track.artworkDataUrl" alt="Album artwork" />
          <div v-else :key="isIdle ? 'idle-artwork' : 'empty-artwork'" class="artwork-placeholder">
            <Music2 :size="34" />
          </div>
        </Transition>
      </div>
      <div class="track-copy">
        <div class="track-meta">
          <span class="source-dot"></span>
          <span>{{ sourceDisplayLabel }}</span>
          <strong>{{ track.status.replaceAll('_', ' ') }}</strong>
        </div>
        <div class="track-text-frame">
          <Transition name="text-crossfade" mode="out-in">
            <div :key="trackContentKey" class="track-text-block">
              <h2>
                <span
                  v-for="(char, index) in titleChars"
                  :key="index + '-' + char"
                  class="char-flow"
                  :style="{ animationDelay: `${index * 16}ms` }"
                >{{ char }}</span>
              </h2>
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
        <div class="progress-row">
          <span>{{ currentTimeLabel }}</span>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${progressRatio * 100}%` }"></div>
          </div>
          <span>{{ durationTimeLabel }}</span>
        </div>
      </div>
    </section>

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
          <p>調整左上角播放器縮放，會立即套用並記住設定。</p>
        </div>
      </div>
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
    </section>

    <section class="panel compact-panel">
      <div class="section-title">
        <Gamepad2 :size="18" />
        <div>
          <h2>遊戲中控制</h2>
          <p>{{ gamepadStatus }}</p>
        </div>
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
            <div v-for="(shortcut, shortcutIdx) in controllerShortcuts" :key="shortcut.buttons.join('+')" class="controller-row">
              <span class="controller-combo" :aria-label="shortcut.buttons.join(' + ')">
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
            </div>
          </div>
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
      <button class="danger" type="button" @click="command('app:quit')"><Power :size="18" />退出</button>
    </section>

    <footer class="app-footer">
      <span>作者：Scott Lin</span>
      <span>
        贊助我：
        <a :href="SPONSOR_URL" target="_blank" rel="noreferrer">
          https://buymeacoffee.com/scott5497
        </a>
      </span>
      <span>聯繫我：<a href="mailto:scott5497ify@gmail.com">scott5497ify@gmail.com</a></span>
    </footer>
    </div>
  </main>

  <main v-else class="player-shell" :class="themeClass">
    <!-- Radio (borderless) player -->
    <section v-if="themeMode === 'radio'" :class="['radio-player', { 'position-mode': positionMode, idle: isIdle }]">
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
    </section>
  </main>
</template>
