import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('forzaApi', {
  onBackendEvent(callback: (event: unknown) => void) {
    const listener = (_event: Electron.IpcRendererEvent, payload: unknown) => callback(payload)
    ipcRenderer.on('backend:event', listener)
    return () => ipcRenderer.removeListener('backend:event', listener)
  },
  onPositionMode(callback: (event: unknown) => void) {
    const listener = (_event: Electron.IpcRendererEvent, payload: unknown) => callback(payload)
    ipcRenderer.on('ui:position-mode', listener)
    return () => ipcRenderer.removeListener('ui:position-mode', listener)
  },
  onThemeMode(callback: (event: unknown) => void) {
    const listener = (_event: Electron.IpcRendererEvent, payload: unknown) => callback(payload)
    ipcRenderer.on('ui:theme-mode', listener)
    return () => ipcRenderer.removeListener('ui:theme-mode', listener)
  },
  onPlayerScale(callback: (event: unknown) => void) {
    const listener = (_event: Electron.IpcRendererEvent, payload: unknown) => callback(payload)
    ipcRenderer.on('ui:player-scale', listener)
    return () => ipcRenderer.removeListener('ui:player-scale', listener)
  },
  sendBackendCommand(command: Record<string, unknown>) {
    return ipcRenderer.invoke('backend:command', command)
  },
  showControlWindow() {
    return ipcRenderer.invoke('window:show-control')
  },
  togglePlayerWindow() {
    return ipcRenderer.invoke('window:toggle-player')
  },
  togglePositionMode() {
    return ipcRenderer.invoke('window:toggle-position-mode')
  },
  getThemeMode() {
    return ipcRenderer.invoke('theme:get')
  },
  setThemeMode(themeMode: 'dark' | 'luxury' | 'radio') {
    return ipcRenderer.invoke('theme:set', themeMode)
  },
  getPlayerScale() {
    return ipcRenderer.invoke('player-scale:get')
  },
  setPlayerScale(playerScale: number) {
    return ipcRenderer.invoke('player-scale:set', playerScale)
  }
})
