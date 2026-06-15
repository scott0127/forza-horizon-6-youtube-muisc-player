<script setup lang="ts">
import { ChevronsRight, Heart } from '@lucide/vue'

defineProps<{
  sponsorUrl: string
  qrSrc: string
}>()
</script>

<template>
  <section class="sponsor-panel panel">
    <div class="sponsor-copy">
      <p class="eyebrow">
        <Heart :size="18" />
        贊助支持
      </p>
      <h2>支持 Gaming Music 持續更新</h2>
      <p>這個工具是免費的。如果想支持我，或是工具有幫到你，可以請還在讀碩士的我喝杯咖啡☕</p>
    </div>
    <div class="sponsor-actions">
      <img class="sponsor-qr" :src="qrSrc" alt="Buy Me a Coffee QR Code" />
      <a class="sponsor-button" :href="sponsorUrl" target="_blank" rel="noreferrer">
        贊助我
        <ChevronsRight :size="18" />
      </a>
    </div>
  </section>
</template>
