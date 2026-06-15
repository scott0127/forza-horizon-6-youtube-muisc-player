# Agent Rules & Constraints

## 1. 架構與模組化
- 大型 Vue template 不得繼續無限制膨脹。可重用或視覺獨立的 UI 應拆成 `src/renderer/src/components/*.vue`。
- 建議 component 邊界：
  - 重複的 panel header、服務按鈕、狀態工具列、贊助卡、Now Playing 卡片。
  - 涉及 IPC、settings persistence、backend event handling 的狀態管理先留在 `App.vue`，透過 props / emits 傳給 presentational components。
- 新增服務或主題時，優先使用資料驅動陣列，不要複製多段幾乎相同的 template。

## 2. CSS / Tailwind 層級
- `@import "tailwindcss/theme"` 與 `@import "tailwindcss/utilities"` 只作為 token / utility layer。
- App 專用 UI 使用語意 class，例如 `.source-panel`、`.service-button`、`.now-playing`；避免把 Tailwind utility 大量塞進 Vue template 造成難以維護。
- CSS 必須依區塊集中：
  - base primitives
  - shared components
  - dark/radio control layout
  - Liquid Glass control layout
  - player windows
  - responsive overrides
- 不要在檔案底部用零散高 specificity 規則硬蓋；若必須覆蓋，補註解說明覆蓋目標與原因。

## 3. 主題隔離
- `theme-dark` 與 `theme-radio` 的控制頁可共享控制台 layout。
- `theme-luxury` 必須獨立 scoped，修改 dark/radio 時不得影響 Liquid Glass。
- player window 與 control window 必須分開思考；`.player-shell` 的規則不得被 `.control-shell` 需求污染。
- 所有與服務色相關的 UI 應依賴 `--accent` 或服務-specific class，不要寫死在跨主題共用規則中。

## 4. 正確性與副作用
- 全域替換、正則改寫、批次移動檔案前，先確認最終作用範圍。
- 不得移除現有功能路徑，例如 Spotify tip、快捷鍵設定、手把設定、播放器大小設定；若視覺上需要弱化，應保留可操作入口。
- 任何 component 抽離後，事件名稱與 payload 必須明確，並以 TypeScript `defineProps` / `defineEmits` 型別約束。

## 5. 視覺實作標準
- 以使用者提供的參考圖為 source of truth 時，不要重新發明設計方向。
- 先分析畫面結構：視窗節奏、section 順序、type scale、panel radius、品牌卡片比例、背景層次，再動手寫 CSS。
- 不做 cards-inside-cards 的堆疊；每個 panel 必須有明確用途。
- 文字不得溢出按鈕或卡片；固定格式 UI 必須用穩定尺寸、grid/flex constraints 和 responsive overrides。

## 6. 驗證與截圖審視
- UI/UX 變更完成後必須執行：
  - `pnpm --dir electron-app exec vue-tsc --noEmit`
  - 視需要執行 `pnpm --dir electron-app build`
  - 使用本地 dev/preview server 搭配瀏覽器截圖自審
- 截圖至少檢查桌面與窄版。若改的是特定主題，必須檢查該主題；若 dark/radio 共用 layout，兩者都要檢查。
- 若環境限制無法截圖，必須明確告知使用者，不能假設視覺已正確。
