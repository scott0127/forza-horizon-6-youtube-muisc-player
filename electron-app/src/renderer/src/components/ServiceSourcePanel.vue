<script setup lang="ts">
import { onUnmounted } from 'vue'
import { ExternalLink, Lightbulb, Music2 } from '@lucide/vue'
import type { MusicService } from '../types'

type SourceService = Exclude<MusicService, 'windows'>

defineProps<{
  services: Array<{
    id: SourceService
    label: string
    iconSrc: string
    iconClass?: string
  }>
  activeService: SourceService
  showSpotifyTip: boolean
}>()

defineEmits<{
  'open-service': [service: SourceService]
  'open-spotify-tip': []
  'close-spotify-tip': []
}>()



interface ButtonState {
  element: HTMLElement
  rect: DOMRect
  x: number
  y: number
  targetX: number
  targetY: number
  tiltX: number
  tiltY: number
  btnY: number
  targetBtnY: number
  isHovered: boolean
  rafId: number | null
}

const buttonStates = new WeakMap<HTMLElement, ButtonState>()

function startLerpLoop(state: ButtonState) {
  if (state.rafId !== null) return

  const tick = () => {
    // 實時計算平滑跟隨 (lerp)，設定為 0.12
    const dx = state.targetX - state.x
    const dy = state.targetY - state.y

    state.x += dx * 0.12
    state.y += dy * 0.12

    // 計算目標傾斜 3D tilt
    let targetRotateX = 0
    let targetRotateY = 0

    if (state.isHovered) {
      // 由於 state.targetX / Y 是百分比 (0 ~ 100)，按鈕中心正好為 50
      const normalizedX = (state.targetX - 50) / 50
      const normalizedY = (state.targetY - 50) / 50
      targetRotateX = -normalizedY * 4  // 最大 ±4deg
      targetRotateY = normalizedX * 5   // 最大 ±5deg
    }

    state.tiltX += (targetRotateX - state.tiltX) * 0.12
    state.tiltY += (targetRotateY - state.tiltY) * 0.12
    state.btnY += (state.targetBtnY - state.btnY) * 0.12

    state.element.style.setProperty('--light-x', `${state.x}%`)
    state.element.style.setProperty('--light-y', `${state.y}%`)
    state.element.style.setProperty('--tilt-x', `${state.tiltX}deg`)
    state.element.style.setProperty('--tilt-y', `${state.tiltY}deg`)
    state.element.style.setProperty('--btn-y', `${state.btnY}px`)

    const distanceSq = dx * dx + dy * dy
    const isTiltSettled = Math.abs(state.tiltX) < 0.05 && Math.abs(state.tiltY) < 0.05 && Math.abs(state.btnY) < 0.05

    // 當滑鼠已離開且光源、傾斜度已安全移回靜態原點，即可停止動畫
    if (!state.isHovered && distanceSq < 0.05 && isTiltSettled) {
      state.rafId = null
      state.element.style.removeProperty('--light-x')
      state.element.style.removeProperty('--light-y')
      state.element.style.removeProperty('--tilt-x')
      state.element.style.removeProperty('--tilt-y')
      state.element.style.removeProperty('--btn-y')
      buttonStates.delete(state.element)
    } else {
      state.rafId = requestAnimationFrame(tick)
    }
  }

  state.rafId = requestAnimationFrame(tick)
}

function handleMouseMove(e: MouseEvent): void {
  const button = e.currentTarget as HTMLElement
  if (!button) return

  let state = buttonStates.get(button)
  const rect = button.getBoundingClientRect()
  
  // 計算滑鼠位置在按鈕中的百分比 (0 ~ 100)
  const pctX = (e.clientX - rect.left) / rect.width * 100
  const pctY = (e.clientY - rect.top) / rect.height * 100

  if (!state) {
    state = {
      element: button,
      rect,
      // 預設固定光源位置：x: 22%, y: 38%
      x: 22,
      y: 38,
      targetX: pctX,
      targetY: pctY,
      tiltX: 0,
      tiltY: 0,
      btnY: 0,
      targetBtnY: -2,
      isHovered: true,
      rafId: null
    }
    buttonStates.set(button, state)
    
    // 設定初始 css 變數，避免第一訊框跳動
    button.style.setProperty('--light-x', `22%`)
    button.style.setProperty('--light-y', `38%`)
    button.style.setProperty('--tilt-x', `0deg`)
    button.style.setProperty('--tilt-y', `0deg`)
    button.style.setProperty('--btn-y', `0px`)
  } else {
    state.rect = rect
    state.isHovered = true
    state.targetX = pctX
    state.targetY = pctY
    state.targetBtnY = -2
  }

  startLerpLoop(state)
}

function handleMouseLeave(e: MouseEvent): void {
  const button = e.currentTarget as HTMLElement
  if (!button) return

  const state = buttonStates.get(button)
  if (state) {
    state.isHovered = false
    // 滑鼠離開時，將 target 設為固定光源的中心 (22%, 38%)，讓它平滑地游回原點
    state.targetX = 22
    state.targetY = 38
    state.targetBtnY = 0
  }
}

onUnmounted(() => {
  // 元件銷毀時由瀏覽器垃圾回收 buttonStates 的 DOM 參照
})
</script>

<template>
  <section id="source" class="panel source-panel">
    <div class="section-title">
      <Music2 :size="18" />
      <div>
        <h2>選擇音樂來源</h2>
        <p>按下服務後會開啟對應網站，並自動套用紅色、綠色、黑色或天空藍主題。</p>
      </div>
    </div>
    <div class="service-grid">
      <template v-for="service in services" :key="service.id">
        <div v-if="service.id === 'spotify'" class="service-button-wrapper">
          <button
            class="service-button spotify"
            :class="{ 'active-service': activeService === 'spotify' }"
            type="button"
            @click="$emit('open-service', 'spotify')"
            @mousemove="handleMouseMove"
            @mouseleave="handleMouseLeave"
          >
            <img class="service-brand-image" :src="service.iconSrc" alt="" aria-hidden="true" />
            <span class="service-label">{{ service.label }}</span>
            <span class="service-external" aria-hidden="true">
              <ExternalLink :size="19" :stroke-width="2.25" />
            </span>
          </button>
          <Transition name="tip-fade">
            <div v-if="showSpotifyTip" class="spotify-tip-box">
              <div class="tip-header">
                <span class="tip-badge">
                  <Lightbulb :size="13" />
                  Spotify Premium 遙控功能
                </span>
                <button class="tip-close-btn" type="button" aria-label="關閉提示" @click.stop="$emit('close-spotify-tip')">
                  &times;
                </button>
              </div>
              <p class="tip-text">提醒您！有 Spotify Premium 即可在任何裝置同步遙控控制此電台</p>
            </div>
          </Transition>
          <Transition name="tip-fade">
            <button
              v-if="!showSpotifyTip"
              class="spotify-tip-trigger"
              type="button"
              aria-label="展開 Spotify Premium 提示"
              title="Spotify Premium 遙控提示"
              @click.stop="$emit('open-spotify-tip')"
            >
              <Lightbulb :size="19" :stroke-width="2.25" />
            </button>
          </Transition>
        </div>
        <button
          v-else
          class="service-button"
          :class="[service.id, { 'active-service': activeService === service.id }]"
          type="button"
          @click="$emit('open-service', service.id)"
          @mousemove="handleMouseMove"
          @mouseleave="handleMouseLeave"
        >
          <img :class="['service-brand-image', service.iconClass]" :src="service.iconSrc" alt="" aria-hidden="true" />
          <span class="service-label">{{ service.label }}</span>
          <span class="service-external" aria-hidden="true">
            <ExternalLink :size="19" :stroke-width="2.25" />
          </span>
        </button>
      </template>
    </div>
  </section>
</template>
