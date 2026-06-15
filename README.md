# Gaming Music Overlay

## 中文說明

Gaming Music Overlay是一個 Windows 小工具，可以在玩 Forza 時顯示 YouTube Music、Spotify、Apple Music 或 KKBOX 正在播放的歌曲，並用快捷鍵控制播放、暫停、下一首、上一首與音量。

本程式透過 Windows 目前媒體工作階段讀取歌曲資訊。你只需要在官方音樂服務登入，程式不會要求、保存或讀取你的帳號密碼。

### 安全性、隱私與誤判說明

- 本程式透過 Windows Media Session 讀取目前播放資訊與封面圖，不會讀取或保存你的音樂帳號密碼。
- 歌詞功能會使用歌名與歌手名稱向第三方歌詞來源查詢同步歌詞。
- 程式不接受遠端連線，目前版本不會開啟 Forza telemetry / UDP 封包監聽。
- release ZIP 不包含 `.vbs` 啟動器，也不使用隱藏的 `WScript.Shell.Run` 啟動方式。
- portable release 根目錄只包含 `AppFiles`、`GamingMusicOverlay.exe`、`README.md` 與 `README.txt`。

### 更新紀錄

#### 4.0

- 新增 KKBOX 服務入口與辨識，支援 KKBOX 的 Windows Media Session 播放資訊。
- 新增懸浮播放器文字大小客製化，可在控制台調整並保存設定。
- release 維持 portable-only 結構，降低防毒誤判風險。

### 一般使用者使用

一般使用者不需要安裝 Python 或任何 Python 依賴庫；`GamingMusicOverlay.exe` 已經把需要的 runtime 與套件包在裡面。

1. 解壓縮 `GamingMusicOverlay*.zip`。
2. 打開完整解壓縮後的資料夾。
3. 雙擊 `GamingMusicOverlay.exe`。
4. 第一次使用時，依照程式顯示的音樂服務引導登入並播放歌曲。

這是可攜版程式。請保留 `GamingMusicOverlay.exe` 與 `AppFiles` 資料夾在同一層，不要只移動 EXE。

### 第一次使用與登入引導

如果程式沒有偵測到 YouTube Music、Spotify、Apple Music 或 KKBOX，會強制顯示設定視窗：

1. 點擊想使用的音樂服務按鈕。
2. 在官方網站或桌面版登入。
3. 播放任意一首歌。
4. 回到 Gaming Music Overlay，點擊重新檢查。

登入流程全部在瀏覽器中完成，本程式只讀取 Windows 提供的目前播放資訊。

Spotify 桌面版會自動使用綠色 UI。瀏覽器播放在 Windows 媒體工作階段中通常只會顯示成 Chrome / Edge，所以瀏覽器播放會使用你最近按下的服務按鈕：YouTube Music 紅色、Spotify 綠色、Apple Music 黑色、KKBOX 天空藍。

### 在 Forza 中使用

- 建議將 Forza 設定為 `無邊框視窗` 或 `Borderless Windowed`，懸浮播放器最穩定。
- 如果 Forza 用系統管理員身分啟動，本程式也需要用系統管理員身分啟動。
- `最小化控制台` 只會把控制台縮到工作列，程式仍會繼續執行。
- 如果控制台看不到，可以按 `Ctrl+Alt+H` 叫回來。
- 如果在遊戲中想直接關閉程式，可以按 `Ctrl+Alt+Q`。

### 快捷鍵

| 快捷鍵 | 功能 |
| --- | --- |
| `Ctrl+Alt+Space` | 播放 / 暫停 |
| `Ctrl+Alt+Right` | 下一首 |
| `Ctrl+Alt+Left` | 上一首 |
| `Ctrl+Alt+Up` | 音量增加 |
| `Ctrl+Alt+Down` | 音量降低 |
| `Ctrl+Alt+End` | 靜音 |
| `Ctrl+Alt+Home` | 顯示 / 隱藏懸浮播放器 |
| `Ctrl+Alt+H` | 顯示 / 最小化控制台 |
| `Ctrl+Alt+P` | 切換懸浮播放器位置調整模式 |
| `Ctrl+Alt+Q` | 退出程式 |

### 手把組合鍵（L3 = 左搖桿按下）

手把快捷鍵可在控制台逐列自訂。修飾鍵固定為 `L3`；點擊右側的「自訂」後，直接按下想使用的第二顆手把按鍵即可。每個組合鍵不可重複。除一般按鈕與 D-Pad 外，也可使用 `LT`、`RT` 及左右搖桿方向。以下為預設值：

若程式無法可靠辨識副廠手把，控制台會要求選擇「類 Xbox 手把」或「類 PlayStation 手把」，並記住該裝置設定。

| 組合鍵 | 功能 |
| --- | --- |
| `L3 + A` | 播放 / 暫停 |
| `L3 + B` | 下一首 |
| `L3 + X` | 上一首 |
| `L3 + D-Pad 右` | 音量增加 |
| `L3 + D-Pad 左` | 音量降低 |

### 調整懸浮播放器

1. 點擊 `調整顯示位置`，或按 `Ctrl+Alt+P`。
2. 拖曳左上角懸浮播放器到想要的位置。
3. 點擊 `儲存目前位置`，或再次按 `Ctrl+Alt+P`。
4. 在控制台的 `懸浮播放器大小` 區塊可調整整體大小與文字大小。

位置會保存到 `%LOCALAPPDATA%\GamingMusicOverlay\settings.json`。

### 解除安裝

關閉程式後，直接刪除解壓縮的資料夾即可。

### 常見問題

- 看不到懸浮播放器：請確認 Forza 使用無邊框視窗模式，並確認懸浮播放器沒有被 `Ctrl+Alt+Home` 隱藏。
- 控制台不見：按 `Ctrl+Alt+H`，或點工作列上的 Gaming Music Overlay 圖示。
- 歌曲資訊不更新：確認 YouTube Music、Spotify、Apple Music 或 KKBOX 正在播放，並且 Chrome / Edge 的硬體媒體鍵功能未被停用。
- 快捷鍵無效：可能被其他軟體佔用。請先關閉可能使用相同快捷鍵的程式。

### 開發者使用

1. 安裝 Python 3.12。
2. 執行 `Install-Dependencies.bat` 安裝 Python 套件。
3. 雙擊 `Run-Overlay.bat` 啟動。
4. 執行 `Check-System.bat` 可檢查依賴、快捷鍵與目前媒體資訊。
5. 執行以下指令可重新打包：

```powershell
.\Build-Release.ps1
```

輸出檔案會在 `release\GamingMusicOverlay-release版本號_portable-test.zip`。

### 授權

本專案採用 MIT License。詳情請見 `LICENSE`。

## English Guide

Gaming Music Overlay is a small Windows helper that shows the currently playing YouTube Music, Spotify, Apple Music, or KKBOX track while you play Forza. It also lets you control play, pause, next track, previous track, and volume with global hotkeys.

The app reads the current Windows media session. You sign in through the official music service, and the app never asks for, stores, or reads your account password.

### Security, Privacy, And False Positives

- The app reads the current Windows Media Session metadata and artwork. It does not read or store music-service passwords.
- Lyrics lookup sends the track title and artist name to third-party lyrics providers.
- The app does not accept remote connections. The current version does not open Forza telemetry / UDP packet listeners.
- The release ZIP does not include `.vbs` launchers or hidden `WScript.Shell.Run` launchers.
- The portable release root only contains `AppFiles`, `GamingMusicOverlay.exe`, `README.md`, and `README.txt`.

### Changelog

#### 4.0

- Added KKBOX entry and detection through Windows Media Session metadata.
- Added customizable floating-player text size in the control panel.
- Kept the release package portable-only to reduce antivirus false-positive risk.

### Use For Normal Users

Normal users do not need to install Python or any Python dependencies. `GamingMusicOverlay.exe` already bundles the required runtime and packages.

1. Unzip `GamingMusicOverlay*.zip`.
2. Open the fully extracted folder.
3. Double-click `GamingMusicOverlay.exe`.
4. On first use, follow the music service setup guide shown by the app.

This is a portable app. Keep `GamingMusicOverlay.exe` and the `AppFiles` folder together. Do not move only the EXE.

### First Use And Sign-In Guide

If YouTube Music, Spotify, Apple Music, or KKBOX is not detected, the app will force a setup window:

1. Click the music service you want to use.
2. Sign in through the official website or desktop app.
3. Play any song.
4. Return to Gaming Music Overlay and click the recheck button.

All sign-in steps happen in your browser. This app only reads the current playback information provided by Windows.

The Spotify desktop app is automatically themed green. Browser playback usually appears to Windows as Chrome / Edge, so browser playback uses the most recent service button you clicked: YouTube Music is red, Spotify is green, Apple Music is black, and KKBOX is sky blue.

### Use In Forza

- Use `Borderless Windowed` mode in Forza for the most reliable floating player behavior.
- If Forza is running as administrator, run this app as administrator too.
- The `最小化控制台` button only minimizes the control panel to the taskbar. The app keeps running.
- Press `Ctrl+Alt+H` to bring the control panel back.
- Press `Ctrl+Alt+Q` to quit the app from inside the game.

### Hotkeys

| Hotkey | Action |
| --- | --- |
| `Ctrl+Alt+Space` | Play / pause |
| `Ctrl+Alt+Right` | Next track |
| `Ctrl+Alt+Left` | Previous track |
| `Ctrl+Alt+Up` | Volume up |
| `Ctrl+Alt+Down` | Volume down |
| `Ctrl+Alt+End` | Mute |
| `Ctrl+Alt+Home` | Show / hide floating player |
| `Ctrl+Alt+H` | Show / minimize control panel |
| `Ctrl+Alt+P` | Toggle floating player position mode |
| `Ctrl+Alt+Q` | Quit app |

### Controller Combos (L3 = Left Stick Press)

Controller shortcuts can be customized row by row in the control panel. The modifier is always `L3`; click `自訂`, then press the secondary controller input you want to use. Duplicate assignments are blocked. In addition to buttons and the D-Pad, `LT`, `RT`, and left/right stick directions are supported. Defaults:

If a third-party controller cannot be identified reliably, the control panel asks whether it uses an Xbox-like or PlayStation-like layout and remembers the selected device profile.

| Combo | Action |
| --- | --- |
| `L3 + A` | Play / pause |
| `L3 + B` | Next track |
| `L3 + X` | Previous track |
| `L3 + D-Pad Right` | Volume up |
| `L3 + D-Pad Left` | Volume down |

### Adjust The Floating Player

1. Click `調整顯示位置`, or press `Ctrl+Alt+P`.
2. Drag the top-left floating player to the position you want.
3. Click `儲存目前位置`, or press `Ctrl+Alt+P` again.
4. Use the `懸浮播放器大小` section in the control panel to adjust overall scale and text size.

The position is saved to `%LOCALAPPDATA%\GamingMusicOverlay\settings.json`.

### Uninstall

Close the app and delete the extracted folder.

### Troubleshooting

- Floating player is not visible: use Borderless Windowed mode in Forza and make sure it was not hidden with `Ctrl+Alt+Home`.
- Control panel is missing: press `Ctrl+Alt+H`, or click the Gaming Music Overlay taskbar icon.
- Track information does not update: make sure YouTube Music, Spotify, Apple Music, or KKBOX is playing and Chrome / Edge hardware media key handling is enabled.
- Hotkeys do not work: another app may already be using the same hotkeys.

### Developer Notes

1. Install Python 3.12.
2. Run `Install-Dependencies.bat` to install Python packages.
3. Double-click `Run-Overlay.bat` to start the app.
4. Run `Check-System.bat` to verify dependencies, hotkeys, and current media metadata.
5. Run this command to build the release package:

```powershell
.\Build-Release.ps1
```

The output will be `release\GamingMusicOverlay-releaseVERSION_portable-test.zip`.

### License

This project is licensed under the MIT License. See `LICENSE` for details.

