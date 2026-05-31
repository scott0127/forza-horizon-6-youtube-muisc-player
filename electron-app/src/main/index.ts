import { app, BrowserWindow, ipcMain, shell, Tray, Menu } from 'electron'
import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

let controlWindow: BrowserWindow | null = null
let playerWindow: BrowserWindow | null = null
let backend: ChildProcessWithoutNullStreams | null = null
let positionMode = false
let isQuitting = false
let tray: Tray | null = null

const isDev = !app.isPackaged
const startOverlayOnly = process.argv.includes('--overlay-only')

interface AppSettings {
  themeMode?: 'dark' | 'luxury' | 'radio'
  playerScale?: number
  playerBounds?: {
    x: number
    y: number
    width: number
    height: number
  }
}

const PLAYER_SIZE = {
  width: 580,
  height: 230
}

const PLAYER_SCALE = {
  default: 0.8,
  min: 0.6,
  max: 1
}

function normalizeThemeMode(value: unknown): 'dark' | 'luxury' | 'radio' {
  if (value === 'luxury') return 'luxury'
  if (value === 'radio') return 'radio'
  return 'dark'
}

function normalizePlayerScale(value: unknown): number {
  const scale = Number(value)
  if (!Number.isFinite(scale)) return PLAYER_SCALE.default

  const clamped = Math.min(Math.max(scale, PLAYER_SCALE.min), PLAYER_SCALE.max)
  return Math.round(clamped * 100) / 100
}

function scaledPlayerSize(scale = getPlayerScale()): { width: number; height: number } {
  return {
    width: Math.ceil(PLAYER_SIZE.width * scale),
    height: Math.ceil(PLAYER_SIZE.height * scale)
  }
}

function rendererUrl(view: 'control' | 'player'): string {
  if (isDev && process.env.ELECTRON_RENDERER_URL) {
    return `${process.env.ELECTRON_RENDERER_URL}?view=${view}`
  }

  return `file://${path.join(__dirname, '../renderer/index.html')}?view=${view}`
}

function backendScriptPath(): string {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'backend', 'forza_music_overlay.py')
  }

  return path.resolve(__dirname, '../../../forza_music_overlay.py')
}

function packagedBackendExecutablePath(): string {
  return path.join(process.resourcesPath, 'backend', 'ForzaMusicOverlayBackend.exe')
}

function appIconPath(): string {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'app-assets', 'logo.ico')
  }

  return path.resolve(__dirname, '../../build/logo.ico')
}

function settingsPath(): string {
  return path.join(app.getPath('userData'), 'settings.json')
}

function readSettings(): AppSettings {
  try {
    return JSON.parse(fs.readFileSync(settingsPath(), 'utf8')) as AppSettings
  } catch {
    return {}
  }
}

function writeSettings(settings: AppSettings): void {
  fs.mkdirSync(path.dirname(settingsPath()), { recursive: true })
  fs.writeFileSync(settingsPath(), JSON.stringify(settings, null, 2), 'utf8')
}

function savePlayerBounds(): void {
  if (!playerWindow || playerWindow.isDestroyed()) return

  const settings = readSettings()
  settings.playerBounds = playerWindow.getBounds()
  writeSettings(settings)
}

function refreshPlayerWindow(): void {
  if (!playerWindow || playerWindow.isDestroyed()) return

  const playerSize = scaledPlayerSize()
  playerWindow.setBackgroundColor('#00000000')
  playerWindow.setAlwaysOnTop(true, 'screen-saver')
  playerWindow.setIgnoreMouseEvents(!positionMode)
  playerWindow.setContentSize(playerSize.width, playerSize.height)

  playerWindow.webContents.invalidate()

  // Windows 透明視窗失焦後偶爾會留下 compositor artifact，
  // 這裡用極短 opacity reset 逼 DWM 重新合成。
  if (process.platform === 'win32') {
    playerWindow.setOpacity(0.99)
    setTimeout(() => {
      if (!playerWindow || playerWindow.isDestroyed()) return
      playerWindow.setOpacity(1)
      playerWindow.webContents.invalidate()
    }, 30)
  }
}

function getThemeMode(): 'dark' | 'luxury' | 'radio' {
  return normalizeThemeMode(readSettings().themeMode)
}

function getPlayerScale(settings = readSettings()): number {
  return normalizePlayerScale(settings.playerScale)
}

function setThemeMode(themeMode: 'dark' | 'luxury' | 'radio'): 'dark' | 'luxury' | 'radio' {
  const settings = readSettings()
  settings.themeMode = normalizeThemeMode(themeMode)
  writeSettings(settings)
  sendToRenderers('ui:theme-mode', { themeMode: settings.themeMode })
  return settings.themeMode
}

function setPlayerScale(playerScale: number): number {
  const settings = readSettings()
  settings.playerScale = normalizePlayerScale(playerScale)
  writeSettings(settings)

  if (playerWindow && !playerWindow.isDestroyed()) {
    const playerSize = scaledPlayerSize(settings.playerScale)
    playerWindow.setContentSize(playerSize.width, playerSize.height)
    playerWindow.webContents.invalidate()
  }

  sendToRenderers('ui:player-scale', { scale: settings.playerScale })
  return settings.playerScale
}

function sendToRenderers(channel: string, payload: unknown): void {
  for (const win of [controlWindow, playerWindow]) {
    if (win && !win.isDestroyed()) {
      win.webContents.send(channel, payload)
    }
  }
}

function startBackend(): void {
  if (backend) return

  const script = backendScriptPath()
  const packagedBackend = packagedBackendExecutablePath()
  const usePackagedBackend = app.isPackaged && fs.existsSync(packagedBackend)
  
  let python = process.env.FORZA_PYTHON || 'python'
  if (!app.isPackaged) {
    const localVenvPython = path.resolve(__dirname, '../../../.venv/Scripts/python.exe')
    if (fs.existsSync(localVenvPython)) {
      python = localVenvPython
    }
  }

  backend = spawn(usePackagedBackend ? packagedBackend : python, usePackagedBackend ? ['--stdio-backend'] : [script, '--stdio-backend'], {
    cwd: usePackagedBackend ? path.dirname(packagedBackend) : path.dirname(script),
    stdio: ['pipe', 'pipe', 'pipe'],
    windowsHide: true
  })

  let buffer = ''

  backend.stdout.on('data', (chunk: Buffer) => {
    buffer += chunk.toString('utf8')
    const lines = buffer.split(/\r?\n/)
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      if (!line.trim()) continue

      try {
        const event = JSON.parse(line)
        handleBackendEvent(event)
        sendToRenderers('backend:event', event)
      } catch (error) {
        if (line.startsWith('pygame ') || line.startsWith('Hello from the pygame community.')) {
          continue
        }

        sendToRenderers('backend:event', {
          type: 'protocol:error',
          message: `Backend JSON parse failed: ${String(error)}`
        })
      }
    }
  })

  backend.stderr.on('data', (chunk: Buffer) => {
    sendToRenderers('backend:event', {
      type: 'backend:stderr',
      message: chunk.toString('utf8')
    })
  })

  backend.on('exit', (code) => {
    sendToRenderers('backend:event', {
      type: 'backend:exit',
      code
    })
    backend = null
  })
}

function handleBackendEvent(event: { type?: string; command?: string }): void {
  if (event.type !== 'command') return

  if (event.command === 'toggle_position_mode') {
    setPositionMode(!positionMode)
  } else if (event.command === 'toggle_overlay') {
    togglePlayerWindow()
  } else if (event.command === 'toggle_control') {
    toggleControlWindow()
  } else if (event.command === 'quit') {
    quitApplication()
  }
}

function sendBackendCommand(command: Record<string, unknown>): void {
  if (!backend || backend.stdin.destroyed) {
    startBackend()
  }

  backend?.stdin.write(`${JSON.stringify(command)}\n`)
}

function sendExistingBackendCommand(command: Record<string, unknown>): void {
  if (!backend || backend.stdin.destroyed) return
  backend.stdin.write(`${JSON.stringify(command)}\n`)
}

function quitApplication(): void {
  if (isQuitting) return
  isQuitting = true

  sendExistingBackendCommand({ type: 'app:quit' })

  if (tray) {
    tray.destroy()
    tray = null
  }

  for (const win of [playerWindow, controlWindow]) {
    if (win && !win.isDestroyed()) {
      win.destroy()
    }
  }

  setTimeout(() => {
    if (backend && !backend.killed) {
      backend.kill()
    }
    app.exit(0)
  }, 80)
}

function showControlWindow(): void {
  if (!controlWindow || controlWindow.isDestroyed()) return

  if (!controlWindow.isVisible()) {
    controlWindow.show()
  }
  if (controlWindow.isMinimized()) {
    controlWindow.restore()
  }
  controlWindow.focus()
}

function updateTrayMenu(): void {
  if (!tray) return

  const contextMenu = Menu.buildFromTemplate([
    {
      label: '顯示控制面板 / Show Control Panel',
      click: (): void => {
        showControlWindow()
      }
    },
    {
      label: '顯示/隱藏懸浮播放器 / Toggle Overlay',
      click: (): void => {
        togglePlayerWindow()
      }
    },
    {
      label: '調整懸浮播放器位置 / Adjust Overlay Position',
      type: 'checkbox',
      checked: positionMode,
      click: (): void => {
        setPositionMode(!positionMode)
      }
    },
    { type: 'separator' },
    {
      label: '結束程式 / Quit',
      click: (): void => {
        quitApplication()
      }
    }
  ])

  tray.setContextMenu(contextMenu)
}

function createTray(): void {
  if (tray) return

  tray = new Tray(appIconPath())
  tray.setToolTip('Forza Music Floating Player')

  tray.on('click', () => {
    showControlWindow()
  })

  tray.on('double-click', () => {
    showControlWindow()
  })

  updateTrayMenu()
}

async function createWindows(): Promise<void> {
  const settings = readSettings()
  const savedBounds = settings.playerBounds
  const playerScale = getPlayerScale(settings)
  const playerSize = scaledPlayerSize(playerScale)
  const playerBounds = {
    x: savedBounds?.x ?? 24,
    y: savedBounds?.y ?? 24,
    width: playerSize.width,
    height: playerSize.height
  }

  controlWindow = new BrowserWindow({
    width: 980,
    height: 760,
    minWidth: 860,
    minHeight: 620,
    title: 'Forza Music Floating Player',
    icon: appIconPath(),
    show: !startOverlayOnly,
    backgroundColor: '#0c111b',
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      sandbox: false,
      backgroundThrottling: false
    }
  })

  playerWindow = new BrowserWindow({
    width: playerBounds.width,
    height: playerBounds.height,
    x: playerBounds.x,
    y: playerBounds.y,
    title: '',
    icon: appIconPath(),
    frame: false,
    transparent: true,
    resizable: false,
    useContentSize: true,
    thickFrame: false,
    fullscreenable: false,
    alwaysOnTop: true,
    hasShadow: false,
    skipTaskbar: true,
    focusable: true,
    backgroundColor: '#00000000',
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      sandbox: false
    }
  })

  playerWindow.setAlwaysOnTop(true, 'screen-saver')
  playerWindow.setContentSize(playerSize.width, playerSize.height)
  playerWindow.setIgnoreMouseEvents(true)
  playerWindow.on('page-title-updated', (event) => {
    event.preventDefault()
    playerWindow?.setTitle('')
  })
  playerWindow.on('moved', savePlayerBounds)
  playerWindow.on('resized', savePlayerBounds)

  controlWindow.on('close', (event) => {
    if (isQuitting) return

    event.preventDefault()
    controlWindow?.hide()
  })

  controlWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  await Promise.all([controlWindow.loadURL(rendererUrl('control')), playerWindow.loadURL(rendererUrl('player'))])

  if (startOverlayOnly) {
    controlWindow.hide()
  }
}

function toggleControlWindow(): void {
  if (!controlWindow) return

  if (controlWindow.isVisible()) {
    controlWindow.hide()
  } else {
    showControlWindow()
  }
}

function togglePlayerWindow(): void {
  if (!playerWindow) return

  if (playerWindow.isVisible()) {
    playerWindow.hide()
  } else {
    playerWindow.showInactive()
  }
}

function setPositionMode(enabled: boolean): void {
  positionMode = enabled

  if (playerWindow && !playerWindow.isDestroyed()) {
    if (enabled) {
      playerWindow.show()
    }

    playerWindow.setFocusable(false)
    playerWindow.setIgnoreMouseEvents(!enabled)
    playerWindow.setAlwaysOnTop(true, 'screen-saver')
    playerWindow.setTitle('')
  }

  sendToRenderers('ui:position-mode', { enabled })
  updateTrayMenu()

  if (!enabled) {
    savePlayerBounds()
  }
}

const gotTheLock = app.requestSingleInstanceLock()

if (!gotTheLock) {
  app.quit()
  process.exit(0)
}

app.on('second-instance', () => {
  showControlWindow()
})

app.whenReady().then(async () => {
  app.setAppUserModelId('tw.scott.forza-music-floating-player')
  await createWindows()
  createTray()
  startBackend()

  setTimeout(refreshPlayerWindow, 0)
})

app.on('browser-window-blur', () => {
  if (isQuitting) return
  setTimeout(refreshPlayerWindow, 0)
})

app.on('browser-window-focus', () => {
  if (isQuitting) return
  setTimeout(refreshPlayerWindow, 0)
})

app.on('activate', () => {
  if (isQuitting) return
  setTimeout(refreshPlayerWindow, 0)
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    quitApplication()
  }
})

app.on('before-quit', () => {
  isQuitting = true
  sendExistingBackendCommand({ type: 'app:quit' })
  backend?.kill()
})

ipcMain.handle('backend:command', (_event, command: Record<string, unknown>) => {
  if (command.type === 'app:quit') {
    quitApplication()
    return
  }

  sendBackendCommand(command)
})

ipcMain.handle('window:show-control', () => {
  showControlWindow()
})

ipcMain.handle('window:hide-control', () => {
  controlWindow?.hide()
})

ipcMain.handle('window:toggle-player', () => {
  togglePlayerWindow()
})

ipcMain.handle('window:toggle-position-mode', () => {
  setPositionMode(!positionMode)
  return positionMode
})

ipcMain.handle('theme:get', () => {
  return getThemeMode()
})

ipcMain.handle('theme:set', (_event, themeMode: 'dark' | 'luxury' | 'radio') => {
  return setThemeMode(themeMode)
})

ipcMain.handle('player-scale:get', () => {
  return getPlayerScale()
})

ipcMain.handle('player-scale:set', (_event, playerScale: number) => {
  return setPlayerScale(playerScale)
})
