<script setup lang="ts">
import { Music2 } from '@lucide/vue'
import idleBg from '../assets/img.png'

defineProps<{
  artworkKey: string
  artworkDataUrl: string | null
  isIdle: boolean
  sourceLabel: string
  statusLabel: string
  titleChars: string[]
  artistChars: string[]
  trackContentKey: string
  currentTimeLabel: string
  durationTimeLabel: string
  progressRatio: number
}>()
</script>

<template>
  <section id="now-playing" class="now-playing panel" :class="{ idle: isIdle }">
    <div class="artwork" :class="{ idle: isIdle }">
      <Transition name="art-swap" mode="out-in">
        <img v-if="artworkDataUrl" :key="artworkKey" :src="artworkDataUrl" alt="Album artwork" />
        <div v-else :key="isIdle ? 'idle-artwork' : 'empty-artwork'" class="artwork-placeholder" :class="{ 'idle-mode': isIdle }" :style="isIdle ? { backgroundImage: 'url(' + idleBg + ')' } : {}">
          <template v-if="isIdle">
            <div class="idle-music-note-wrapper">
              <Music2 :size="64" class="idle-music-note" />
            </div>
            <svg class="idle-mountains" viewBox="0 0 200 200" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
              <path class="mist-layer-1" d="M-50,200 L-50,160 Q40,135 100,165 T230,150 L250,200 Z" fill="url(#mist-grad-1)" opacity="0.35" filter="url(#mist-blur)" />
              <path class="mist-layer-2" d="M-50,200 L-50,170 Q40,150 110,175 T230,155 L250,200 Z" fill="url(#mist-grad-2)" opacity="0.3" filter="url(#mist-blur)" />
              <defs>
                <filter id="mist-blur">
                  <feGaussianBlur stdDeviation="8" />
                </filter>
                <linearGradient id="mist-grad-1" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#8b5cf6" />
                  <stop offset="60%" stop-color="#4c2c96" stop-opacity="0.2" />
                  <stop offset="100%" stop-color="transparent" stop-opacity="0" />
                </linearGradient>
                <linearGradient id="mist-grad-2" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#c8b3ff" />
                  <stop offset="50%" stop-color="#6d28d9" stop-opacity="0.2" />
                  <stop offset="100%" stop-color="transparent" stop-opacity="0" />
                </linearGradient>
              </defs>
            </svg>
          </template>
          <template v-else>
            <Music2 :size="64" />
          </template>
        </div>
      </Transition>
    </div>
    <div class="track-copy">
      <div class="track-meta">
        <span class="source-dot"></span>
        <span>{{ sourceLabel }}</span>
        <div v-if="!isIdle" class="playing-equalizer" aria-hidden="true">
          <span></span>
          <span></span>
          <span></span>
          <span></span>
        </div>
        <strong>{{ statusLabel }}</strong>
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
</template>
