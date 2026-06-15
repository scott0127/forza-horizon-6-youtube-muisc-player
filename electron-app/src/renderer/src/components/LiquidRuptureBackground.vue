<template>
<div ref="hostRef" class="liquid-rupture-bg" :class="{ 'is-dark': themeMode !== 'luxury' }" aria-hidden="true">
  <div v-if="themeMode !== 'luxury'" class="interfaceMask"></div>
</div>
</template>

<script setup lang="ts">
/*
 * Adapted from "Unified Rupture" © 2023-04-15 by Zaron Chen.
 * Original license: CC BY-NC-SA 3.0.
 *
 * Electron adaptation notes:
 * - No CDN imports.
 * - No p5.flex dependency.
 * - Shox helper functions are replaced with compact local GLSL equivalents.
 * - Canvas is full-window responsive through ResizeObserver.
 */
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    accent?: string
    themeMode?: string
  }>(),
  {
    accent: '#8b5cf6'
  }
)

const hostRef = ref<HTMLDivElement | null>(null)

let p5Instance: any = null
let resizeObserver: ResizeObserver | null = null
let removePointerListener: (() => void) | null = null
let removeScrollListener: (() => void) | null = null
let restoreFetch: (() => void) | null = null
let disposed = false
let accentRgb = parseHexColor(props.accent)

const vert = `
precision mediump float;

attribute vec3 aPosition;
attribute vec2 aTexCoord;

varying vec2 vTexCoord;

void main() {
  vTexCoord = aTexCoord;

  vec4 positionVec4 = vec4(aPosition, 1.0);
  positionVec4.xy = positionVec4.xy * 2.0 - 1.0;

  gl_Position = positionVec4;
}
`

const frag = `
precision highp float;

uniform vec2 canvasSize;
uniform vec2 mouse;
uniform float time;
uniform vec3 accentColor;
uniform float scrollProgress;

varying vec2 vTexCoord;

float mod289(float x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 permute(vec4 x) { return mod289(((x * 34.0) + 10.0) * x); }
vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

float snoise(vec3 v) {
  const vec2 C = vec2(1.0 / 6.0, 1.0 / 3.0);
  const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);

  vec3 i = floor(v + dot(v, C.yyy));
  vec3 x0 = v - i + dot(i, C.xxx);

  vec3 g = step(x0.yzx, x0.xyz);
  vec3 l = 1.0 - g;
  vec3 i1 = min(g.xyz, l.zxy);
  vec3 i2 = max(g.xyz, l.zxy);

  vec3 x1 = x0 - i1 + C.xxx;
  vec3 x2 = x0 - i2 + C.yyy;
  vec3 x3 = x0 - D.yyy;

  i = mod289(i);
  vec4 p = permute(
    permute(
      permute(i.z + vec4(0.0, i1.z, i2.z, 1.0))
      + i.y + vec4(0.0, i1.y, i2.y, 1.0)
    )
    + i.x + vec4(0.0, i1.x, i2.x, 1.0)
  );

  float n_ = 0.142857142857;
  vec3 ns = n_ * D.wyz - D.xzx;

  vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
  vec4 x_ = floor(j * ns.z);
  vec4 y_ = floor(j - 7.0 * x_);

  vec4 x = x_ * ns.x + ns.yyyy;
  vec4 y = y_ * ns.x + ns.yyyy;
  vec4 h = 1.0 - abs(x) - abs(y);

  vec4 b0 = vec4(x.xy, y.xy);
  vec4 b1 = vec4(x.zw, y.zw);

  vec4 s0 = floor(b0) * 2.0 + 1.0;
  vec4 s1 = floor(b1) * 2.0 + 1.0;
  vec4 sh = -step(h, vec4(0.0));

  vec4 a0 = b0.xzyw + s0.xzyw * sh.xxyy;
  vec4 a1 = b1.xzyw + s1.xzyw * sh.zzww;

  vec3 p0 = vec3(a0.xy, h.x);
  vec3 p1 = vec3(a0.zw, h.y);
  vec3 p2 = vec3(a1.xy, h.z);
  vec3 p3 = vec3(a1.zw, h.w);

  vec4 norm = taylorInvSqrt(vec4(dot(p0, p0), dot(p1, p1), dot(p2, p2), dot(p3, p3)));
  p0 *= norm.x;
  p1 *= norm.y;
  p2 *= norm.z;
  p3 *= norm.w;

  vec4 m = max(0.5 - vec4(dot(x0, x0), dot(x1, x1), dot(x2, x2), dot(x3, x3)), 0.0);
  m = m * m;
  return 105.0 * dot(m * m, vec4(dot(p0, x0), dot(p1, x1), dot(p2, x2), dot(p3, x3)));
}

vec4 snoise3DImage(vec2 uv, float scal, float gain, float ofst, float expo, vec3 move) {
  uv *= scal;
  float R = snoise(vec3(uv, 100.0) + move);
  float G = snoise(vec3(uv, 300.0) + move);
  float B = snoise(vec3(uv, 500.0) + move);
  vec3 col;
  col.r = pow(abs(R), expo) * (step(0.0, R) * 2.0 - 1.0);
  col.g = pow(abs(G), expo) * (step(0.0, G) * 2.0 - 1.0);
  col.b = pow(abs(B), expo) * (step(0.0, B) * 2.0 - 1.0);
  return vec4(ofst + gain * col, 1.0);
}

float smoo3(float x) { return x * x * (3.0 - 2.0 * x); }
vec2 smoo3(vec2 x) { return x * x * (3.0 - 2.0 * x); }
vec3 smoo3(vec3 x) { return x * x * (3.0 - 2.0 * x); }
vec4 smoo3(vec4 x) { return x * x * (3.0 - 2.0 * x); }

vec2 mirror(vec2 uv, float num) {
  uv *= num;
  vec2 iuv = floor(uv);
  uv *= 1.0 - 2.0 * mod(iuv, 2.0);
  return fract(uv);
}

vec2 displace(vec2 uv, vec2 duv, float off, float wei) {
  duv -= off;
  return uv - duv * wei;
}

vec2 conical(vec2 uv, vec2 pos, float tile, float ofst) {
  uv -= pos;
  vec2 radialUv = vec2(atan(uv.y, uv.x) / 6.283185307179586 + 0.5, length(uv));
  radialUv = radialUv * tile - fract(ofst);
  return fract(radialUv);
}

float pulse(float start, float end) {
  return step(0.0, start) * step(end, 0.0);
}

vec4 grad(float area, vec4 startCol, vec4 endCol, float startPos, float endPos) {
  float u = pulse(area - startPos, area - endPos);
  return mix(startCol, endCol, (area - startPos) / (endPos - startPos)) * u;
}

vec4 palette5(float t, vec4 c0, vec4 c1, vec4 c2, vec4 c3, vec4 c4) {
  vec4 color = vec4(0.0);
  color += grad(t, c0, c1, 0.00, 0.26);
  color += grad(t, c1, c2, 0.26, 0.52);
  color += grad(t, c2, c3, 0.52, 0.76);
  color += grad(t, c3, c4, 0.76, 1.00);
  return color;
}

float vignette(vec2 uv) {
  float d = distance(uv, vec2(0.5));
  return smoothstep(0.78, 0.18, d);
}



void main() {
  vec2 rawUv = vTexCoord;
  vec2 uv = rawUv;
  vec2 mo = clamp(mouse, vec2(0.0), vec2(1.0));
  float scroll = clamp(scrollProgress, 0.0, 1.0);

  uv -= 0.5;
  uv.x *= canvasSize.x / max(canvasSize.y, 1.0);

  vec2 muv = smoo3(mirror(uv, 1.0));

  float scal = 2.35;
  float gain = mix(10.0, 28.0, mo.y);
  float ofst = 0.48;
  float expo = mix(0.72, 1.65, mo.x);

  vec3 move = vec3(
    sin(time * 0.00022 + scroll * 0.9) * 0.12,
    cos(time * 0.00018 + scroll * 0.7) * 0.12,
    time * 0.00115 + scroll * 0.22
  );

  vec4 dimg = snoise3DImage(uv, scal, gain, ofst, expo, move);

  float wei = 0.085;
  vec2 duv = smoo3(displace(muv, dimg.rg, ofst, wei));
  vec2 puv = smoo3(conical(duv, vec2(0.5), 4.0, time * 0.00046 + scroll * 0.08));

  vec3 base = vec3(0.006, 0.012, 0.032);
  vec3 c0 = vec3(0.010, 0.018, 0.050);
  vec3 c1 = vec3(0.028, 0.080, 0.180);
  vec3 c2 = vec3(0.180, 0.180, 0.520);
  vec3 c3 = vec3(0.520, 0.360, 0.960);
  vec3 c4 = vec3(0.090, 0.740, 0.960);

  vec4 rupture = smoo3(palette5(
    puv.x + scroll * 0.035,
    vec4(c0, 1.0),
    vec4(c1, 1.0),
    vec4(c2, 1.0),
    vec4(c3, 1.0),
    vec4(c4, 1.0)
  ));

  float lineA = smoothstep(
    0.470,
    0.505,
    abs(fract(puv.x * 3.0 + time * 0.00022 + scroll * 0.04) - 0.5)
  );
  float lineB = smoothstep(
    0.492,
    0.500,
    abs(fract(puv.y * 2.2 - time * 0.00018 - scroll * 0.035) - 0.5)
  );
  float caustic = (1.0 - lineA) * 0.050 + (1.0 - lineB) * 0.034;

  vec3 color = mix(base, rupture.rgb, 0.50);
  color += vec3(0.45, 0.58, 1.0) * caustic;



  float vig = vignette(rawUv);
  color *= mix(0.50, 1.10, vig);

  vec2 p = rawUv - 0.5;
  float glow1 = exp(-dot(p - vec2(-0.30 + scroll * 0.03, -0.20), p - vec2(-0.30 + scroll * 0.03, -0.20)) * 4.2);
  float glow2 = exp(-dot(p - vec2(0.32 - scroll * 0.03, 0.28), p - vec2(0.32 - scroll * 0.03, 0.28)) * 4.0);
  color += vec3(0.05, 0.20, 0.34) * glow1 * 0.32;
  color += vec3(0.30, 0.12, 0.48) * glow2 * 0.34;

  gl_FragColor = vec4(smoo3(color), 1.0);
}
`

function parseHexColor(value: string): [number, number, number] {
  const normalized = value.trim().replace('#', '')
  if (!/^[0-9a-f]{6}$/i.test(normalized)) return [0.545, 0.361, 0.965]

  return [
    Number.parseInt(normalized.slice(0, 2), 16) / 255,
    Number.parseInt(normalized.slice(2, 4), 16) / 255,
    Number.parseInt(normalized.slice(4, 6), 16) / 255
  ]
}

function installP5TranslationFetchGuard(): () => void {
  const originalFetch = window.fetch.bind(window)

  window.fetch = ((input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === 'string' ? input : input instanceof Request ? input.url : input.toString()
    if (url.includes('cdn.jsdelivr.net/npm/p5') && url.includes('/translations/')) {
      return Promise.resolve(new Response('{}', { headers: { 'Content-Type': 'application/json' } }))
    }

    return originalFetch(input, init)
  }) as typeof window.fetch

  return () => {
    window.fetch = originalFetch
  }
}

function sizeForHost(host: HTMLDivElement): { width: number; height: number } {
  const rect = host.getBoundingClientRect()
  return {
    width: Math.max(1, Math.round(rect.width || window.innerWidth)),
    height: Math.max(1, Math.round(rect.height || window.innerHeight))
  }
}

function getScrollProgress(): number {
  const documentElement = document.documentElement
  const scrollTop = window.scrollY || documentElement.scrollTop || document.body.scrollTop || 0
  const maxScroll = Math.max(1, documentElement.scrollHeight - window.innerHeight)
  return Math.min(Math.max(scrollTop / maxScroll, 0), 1)
}

watch(
  () => props.accent,
  (nextAccent) => {
    accentRgb = parseHexColor(nextAccent)
  }
)

onMounted(async () => {
  const host = hostRef.value
  if (!host) return

  window.localStorage.setItem('i18nextLng', 'en')
  restoreFetch = installP5TranslationFetchGuard()

  const p5Module = await import('p5')
  const P5 = p5Module.default
  P5.disableFriendlyErrors = true

  if (disposed) return

  let targetMouseX = 0.5
  let targetMouseY = 0.5
  let smoothMouseX = 0.5
  let smoothMouseY = 0.5
  let targetScrollProgress = getScrollProgress()
  let smoothScrollProgress = targetScrollProgress

  const handlePointerMove = (event: PointerEvent) => {
    const rect = host.getBoundingClientRect()

    targetMouseX = Math.min(Math.max((event.clientX - rect.left) / Math.max(rect.width, 1), 0), 1)
    targetMouseY = Math.min(Math.max((event.clientY - rect.top) / Math.max(rect.height, 1), 0), 1)
  }

  window.addEventListener('pointermove', handlePointerMove, { passive: true })

  removePointerListener = () => {
    window.removeEventListener('pointermove', handlePointerMove)
  }

  const handleScroll = () => {
    targetScrollProgress = getScrollProgress()
  }

  window.addEventListener('scroll', handleScroll, { passive: true })

  removeScrollListener = () => {
    window.removeEventListener('scroll', handleScroll)
  }

  p5Instance = new P5((p: any) => {
    let shaderProgram: any
    let reduceMotion = false

    const resize = () => {
      const { width, height } = sizeForHost(host)
      p.resizeCanvas(width, height)
      targetScrollProgress = getScrollProgress()
    }

    p.setup = () => {
      const { width, height } = sizeForHost(host)
      const canvas = p.createCanvas(width, height, p.WEBGL)
      canvas.parent(host)

      p.pixelDensity(Math.min(window.devicePixelRatio || 1, 1.35))
      p.noStroke()

      reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
      shaderProgram = p.createShader(vert, frag)

      resizeObserver = new ResizeObserver(resize)
      resizeObserver.observe(host)
    }

    p.draw = () => {
      if (!shaderProgram) return

      smoothMouseX = p.lerp(smoothMouseX, targetMouseX, 0.045)
      smoothMouseY = p.lerp(smoothMouseY, targetMouseY, 0.045)
      smoothScrollProgress = p.lerp(smoothScrollProgress, targetScrollProgress, 0.08)

      p.shader(shaderProgram)

      shaderProgram.setUniform('canvasSize', [p.width, p.height])
      shaderProgram.setUniform('mouse', [smoothMouseX, smoothMouseY])
      shaderProgram.setUniform('time', reduceMotion ? 0 : p.frameCount)
      shaderProgram.setUniform('accentColor', accentRgb)
      shaderProgram.setUniform('scrollProgress', reduceMotion ? targetScrollProgress : smoothScrollProgress)

      p.quad(-1, 1, 1, 1, 1, -1, -1, -1)
    }

    p.windowResized = resize
  }, host)
})

onBeforeUnmount(() => {
  disposed = true
  removePointerListener?.()
  removePointerListener = null
  removeScrollListener?.()
  removeScrollListener = null

  resizeObserver?.disconnect()
  resizeObserver = null

  p5Instance?.remove()
  p5Instance = null

  restoreFetch?.()
  restoreFetch = null
})
</script>

<style scoped>
.liquid-rupture-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  width: 100vw;
  height: 100vh;
  min-width: 100vw;
  min-height: 100vh;
  overflow: hidden;
  pointer-events: none;
  background:
    radial-gradient(circle at 16% 18%, rgba(139, 92, 246, 0.12), transparent 34%),
    radial-gradient(circle at 82% 78%, rgba(56, 189, 248, 0.1), transparent 36%),
    linear-gradient(135deg, #071126 0%, #02040b 48%, #081326 100%);
}

.liquid-rupture-bg :deep(canvas) {
  display: block;
  width: 100% !important;
  height: 100% !important;
}

.liquid-rupture-bg.is-dark::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(circle at 50% 50%, transparent 0%, #03050d 85%);
  z-index: 1;
}

.interfaceMask {
  position: absolute;
  inset: 0;
  background: rgba(3, 5, 13, 0.45);
  pointer-events: none;
  z-index: 2;
}
</style>
