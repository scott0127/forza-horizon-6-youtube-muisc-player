# test_ps_gamepad.py
import vgamepad as vg
import keyboard
import time

print("正在建立虛擬 PlayStation 4 控制器...")
# 建立虛擬 PS 手把 (會被系統識別為 Wireless Controller / DualShock 4)
gamepad = vg.VDS4Gamepad()
print("虛擬搖桿已啟用！")

print("==================================================")
print("     🎮 鍵盤 -> 虛擬 PS 手把 實時映射控制工具 🎮")
print("==================================================")
print("  請按住以下鍵盤按鍵來模擬對應的 PS 手把輸入：")
print("  ----------------------------------------------")
print("  按住 [ L ] 鍵 -> 模擬 L3 (左搖桿下壓，修飾鍵)")
print("  按住 [ J ] 鍵 -> 模擬 ✕ 鍵 (對應 A 鍵：播放/暫停)")
print("  按住 [ K ] 鍵 -> 模擬 ◯ 鍵 (對應 B 鍵：下一首)")
print("  按住 [ I ] 鍵 -> 模擬 ▢ 鍵 (對應 X 鍵：上一首)")
print("  按住 [ W ] 鍵 -> 模擬 D-Pad 上 (對應音量增加)")
print("  按住 [ S ] 鍵 -> 模擬 D-Pad 下 (對應音量減少)")
print("  ----------------------------------------------")
print("  按 [ ESC ] 鍵 -> 退出本程式")
print("==================================================")
print("💡 提示：請確保以「系統管理員身分 (Administrator)」運行此命令提示字元/PowerShell")
print("       這樣程式才能監聽全局鍵盤事件。")
print("==================================================")

# 儲存目前正在按下的按鍵狀態，避免重複發送
active_buttons = set()
dpad_state = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE

try:
    while True:
        # 按下 ESC 鍵退出
        if keyboard.is_pressed('esc'):
            print("\n正在退出模擬程式，釋放所有虛擬按鍵...")
            break

        state_changed = False

        # 1. 處理普通按鍵映射
        button_mappings = {
            'l': (vg.DS4_BUTTONS.DS4_BUTTON_THUMB_LEFT, "L3 (搖桿下壓)"),
            'j': (vg.DS4_BUTTONS.DS4_BUTTON_CROSS, "✕ (手把 A)") ,
            'k': (vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE, "◯ (手把 B)"),
            'i': (vg.DS4_BUTTONS.DS4_BUTTON_SQUARE, "▢ (手把 X)"),
        }

        for key, (ds4_btn, btn_name) in button_mappings.items():
            is_pressed = keyboard.is_pressed(key)
            if is_pressed and ds4_btn not in active_buttons:
                gamepad.press_button(ds4_btn)
                active_buttons.add(ds4_btn)
                state_changed = True
                print(f"[按下] 鍵盤鍵 [{key.upper()}] -> 觸發虛擬手把 {btn_name}")
            elif not is_pressed and ds4_btn in active_buttons:
                gamepad.release_button(ds4_btn)
                active_buttons.discard(ds4_btn)
                state_changed = True
                print(f"[釋放] 鍵盤鍵 [{key.upper()}] -> 釋放虛擬手把 {btn_name}")

        # 2. 處理 D-Pad 方向鍵映射 (W / S)
        is_up = keyboard.is_pressed('w')
        is_down = keyboard.is_pressed('s')

        new_dpad = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE
        if is_up:
            new_dpad = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH
        elif is_down:
            new_dpad = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH

        if new_dpad != dpad_state:
            gamepad.directional_pad(new_dpad)
            dpad_state = new_dpad
            state_changed = True
            if new_dpad == vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH:
                print("[按下] 鍵盤鍵 [W] -> 觸發虛擬手把 D-Pad [上]")
            elif new_dpad == vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH:
                print("[按下] 鍵盤鍵 [S] -> 觸發虛擬手把 D-Pad [下]")
            else:
                print("[釋放] 鍵盤 D-Pad 方向鍵已歸零")

        # 3. 如果有任何按鍵狀態改變，更新虛擬控制器
        if state_changed:
            gamepad.update()

        # 微小延遲避免 CPU 佔用率過高
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n偵測到中斷，正在退出...")

finally:
    # 確保退出時完全釋放所有虛擬按鍵，避免卡死
    gamepad.reset()
    gamepad.update()
    print("虛擬控制器已重設並卸載。")
