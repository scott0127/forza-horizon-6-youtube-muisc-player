<script setup lang="ts">
import { Moon, Radio, Droplet } from '@lucide/vue'
import type { ThemeMode } from '../types'

defineProps<{
  themeMode: ThemeMode
  backendStatus: string
  accent: string
}>()

defineEmits<{
  'theme-change': [themeMode: ThemeMode]
}>()
</script>

<template>
  <div class="toolbar-cluster">
    <div class="theme-toggle" aria-label="主題切換">
      <button :class="{ selected: themeMode === 'dark' }" type="button" @click="$emit('theme-change', 'dark')">
        <Moon :size="15" />
        暗黑
      </button>
      <button :class="{ selected: themeMode === 'luxury' }" type="button" @click="$emit('theme-change', 'luxury')">
        <Droplet :size="15" />
        Liquid Glass
      </button>
      <button :class="{ selected: themeMode === 'radio' }" type="button" @click="$emit('theme-change', 'radio')">
        <Radio :size="15" />
        無邊框電台
      </button>
    </div>
    <div class="status-pill" :style="{ borderColor: accent, color: accent }">
      <Radio :size="16" />
      <span>{{ backendStatus }}</span>
      <span class="status-dot" :style="{ background: accent }"></span>
    </div>
  </div>
</template>
