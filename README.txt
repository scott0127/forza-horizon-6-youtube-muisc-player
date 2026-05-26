Forza 音樂懸浮播放器
====================

中文說明
--------

Forza 音樂懸浮播放器是一個 Windows 小工具，可以在玩 Forza 時顯示 YouTube Music 或 Spotify 正在播放的歌曲，並用快捷鍵控制播放、暫停、下一首、上一首與音量。

本程式透過 Windows 目前媒體工作階段讀取歌曲資訊。你只需要在官方 YouTube Music 或 Spotify 登入，程式不會要求、保存或讀取你的帳號密碼。

一般使用者安裝
--------------

一般使用者不需要安裝 Python 或任何 Python 依賴庫；ForzaMusicOverlay.exe 已經把需要的 runtime 與套件包在裡面。

1. 解壓縮 ForzaMusicOverlay*.zip。
2. 打開資料夾 ForzaMusicOverlay。
3. 雙擊 Install-App.bat。
4. 安裝完成後，從桌面捷徑或開始功能表啟動 Forza 音樂懸浮播放器。
5. 第一次使用時，依照程式顯示的音樂服務引導登入並播放歌曲。

也可以參考同資料夾內的 Install-Guide.png 安裝教學圖片。

第一次使用與登入引導
--------------------

如果程式沒有偵測到 YouTube Music 或 Spotify，會強制顯示設定視窗：

1. 點擊「開啟 YouTube Music」或「開啟 Spotify」。
2. 在瀏覽器或 Spotify 桌面版登入。
3. 播放任意一首歌。
4. 回到 Forza 音樂懸浮播放器，點擊重新檢查。

登入流程全部在瀏覽器中完成，本程式只讀取 Windows 提供的目前播放資訊。

Spotify 桌面版會自動使用綠色 UI。Spotify Web 和 YouTube Music 在 Windows 媒體工作階段中通常只會顯示成 Chrome / Edge，所以瀏覽器播放會使用你最近按下的服務按鈕：按「開啟 Spotify」使用綠色，按「開啟 YouTube Music」使用紅色。

在 Forza 中使用
---------------

- 建議將 Forza 設定為「無邊框視窗」或 Borderless Windowed，懸浮播放器最穩定。
- 如果 Forza 用系統管理員身分啟動，本程式也需要用系統管理員身分啟動。
- 「最小化控制台」只會把控制台縮到工作列，程式仍會繼續執行。
- 如果控制台看不到，可以按 Ctrl+Alt+H 叫回來。
- 如果在遊戲中想直接關閉程式，可以按 Ctrl+Alt+Q。

快捷鍵
------

Ctrl+Alt+Space    播放 / 暫停
Ctrl+Alt+Right    下一首
Ctrl+Alt+Left     上一首
Ctrl+Alt+Up       音量增加
Ctrl+Alt+Down     音量降低
Ctrl+Alt+End      靜音
Ctrl+Alt+Home     顯示 / 隱藏懸浮播放器
Ctrl+Alt+H        顯示 / 最小化控制台
Ctrl+Alt+P        切換懸浮播放器位置調整模式
Ctrl+Alt+Q        退出程式

手把組合鍵
----------

LB + A            播放 / 暫停
LB + B            下一首
LB + X            上一首

調整懸浮播放器位置
------------------

1. 點擊「調整顯示位置」，或按 Ctrl+Alt+P。
2. 拖曳左上角懸浮播放器到想要的位置。
3. 點擊「儲存目前位置」，或再次按 Ctrl+Alt+P。

位置會保存到 %LOCALAPPDATA%\ForzaMusicOverlay\settings.json。

解除安裝
--------

在安裝資料夾中雙擊 Uninstall-App.bat，即可移除桌面捷徑與開始功能表捷徑。

常見問題
--------

- 看不到懸浮播放器：請確認 Forza 使用無邊框視窗模式，並確認懸浮播放器沒有被 Ctrl+Alt+Home 隱藏。
- 控制台不見：按 Ctrl+Alt+H，或點工作列上的 Forza 音樂懸浮播放器圖示。
- 歌曲資訊不更新：確認 YouTube Music 或 Spotify 正在播放，並且 Chrome / Edge 的硬體媒體鍵功能未被停用。
- 快捷鍵無效：可能被其他軟體佔用。請先關閉可能使用相同快捷鍵的程式。

開發者使用
----------

1. 安裝 Python 3.12。
2. 執行 Install-Dependencies.bat 安裝 Python 套件。
3. 雙擊 Run-Overlay.vbs 啟動。
4. 執行 Check-System.bat 可檢查依賴、快捷鍵與目前媒體資訊。
5. 執行 .\Build-Release.ps1 可重新打包。

輸出檔案會在 release\ForzaMusicOverlay-v版本號.zip。

授權
----

本專案採用 MIT License。詳情請見 LICENSE。


English Guide
-------------

Forza Music Floating Player is a small Windows helper that shows the currently playing YouTube Music or Spotify track while you play Forza. It also lets you control play, pause, next track, previous track, and volume with global hotkeys.

The app reads the current Windows media session. You sign in through the official YouTube Music or Spotify service, and the app never asks for, stores, or reads your account password.

Install For Normal Users
------------------------

Normal users do not need to install Python or any Python dependencies. ForzaMusicOverlay.exe already bundles the required runtime and packages.

1. Unzip ForzaMusicOverlay*.zip.
2. Open the ForzaMusicOverlay folder.
3. Double-click Install-App.bat.
4. Launch Forza 音樂懸浮播放器 from the desktop shortcut or Start Menu.
5. On first use, follow the music service setup guide shown by the app.

You can also check Install-Guide.png in the same folder for a visual installation guide.

First Use And Sign-In Guide
---------------------------

If YouTube Music or Spotify is not detected, the app will force a setup window:

1. Click Open YouTube Music or Open Spotify.
2. Sign in through the browser or Spotify desktop app.
3. Play any song.
4. Return to Forza Music Floating Player and click the recheck button.

All sign-in steps happen in your browser. This app only reads the current playback information provided by Windows.

The Spotify desktop app is automatically themed green. Spotify Web and YouTube Music usually appear to Windows as Chrome / Edge, so browser playback uses the most recent service button you clicked: Open Spotify sets green, and Open YouTube Music sets red.

Use In Forza
------------

- Use Borderless Windowed mode in Forza for the most reliable floating player behavior.
- If Forza is running as administrator, run this app as administrator too.
- The 最小化控制台 button only minimizes the control panel to the taskbar. The app keeps running.
- Press Ctrl+Alt+H to bring the control panel back.
- Press Ctrl+Alt+Q to quit the app from inside the game.

Hotkeys
-------

Ctrl+Alt+Space    Play / pause
Ctrl+Alt+Right    Next track
Ctrl+Alt+Left     Previous track
Ctrl+Alt+Up       Volume up
Ctrl+Alt+Down     Volume down
Ctrl+Alt+End      Mute
Ctrl+Alt+Home     Show / hide floating player
Ctrl+Alt+H        Show / minimize control panel
Ctrl+Alt+P        Toggle floating player position mode
Ctrl+Alt+Q        Quit app

Controller Combos
-----------------

LB + A            Play / pause
LB + B            Next track
LB + X            Previous track

Move The Floating Player
------------------------

1. Click 調整顯示位置, or press Ctrl+Alt+P.
2. Drag the top-left floating player to the position you want.
3. Click 儲存目前位置, or press Ctrl+Alt+P again.

The position is saved to %LOCALAPPDATA%\ForzaMusicOverlay\settings.json.

Uninstall
---------

Double-click Uninstall-App.bat in the installed folder to remove the desktop and Start Menu shortcuts.

Troubleshooting
---------------

- Floating player is not visible: use Borderless Windowed mode in Forza and make sure it was not hidden with Ctrl+Alt+Home.
- Control panel is missing: press Ctrl+Alt+H, or click the Forza Music Floating Player taskbar icon.
- Track information does not update: make sure YouTube Music or Spotify is playing and Chrome / Edge hardware media key handling is enabled.
- Hotkeys do not work: another app may already be using the same hotkeys.

Developer Notes
---------------

1. Install Python 3.12.
2. Run Install-Dependencies.bat to install Python packages.
3. Double-click Run-Overlay.vbs to start the app.
4. Run Check-System.bat to verify dependencies, hotkeys, and current media metadata.
5. Run .\Build-Release.ps1 to build the release package.

The output will be release\ForzaMusicOverlay-vVERSION.zip.

License
-------

This project is licensed under the MIT License. See LICENSE for details.
