# test_ps_gamepad.py
import vgamepad as vg
import keyboard
import time

print("==================================================")
print("     🎮 虛擬控制器模擬選擇 🎮")
print("==================================================")
print("1. PlayStation 4 (DualShock 4)")
print("2. Xbox 360 (XInput)")
print("3. PlayStation 5 (DualSense) - ⚠️ vgamepad 不支援，將以 PS4 替代")
print("==================================================")

choice = input("請輸入數字選擇要模擬的控制器 (預設為 1): ")

is_xbox = False
if choice == '2':
    print("正在建立虛擬 Xbox 360 控制器...")
    gamepad = vg.VX360Gamepad()
    is_xbox = True
else:
    if choice == '3':
        print("⚠️ 提示: vgamepad 庫底層 (ViGEmBus) 尚不支援直接模擬 PS5 (DualSense) 控制器。")
        print("將降級為模擬 PlayStation 4 (DualShock 4) 控制器。")
    print("正在建立虛擬 PlayStation 4 控制器...")
    gamepad = vg.VDS4Gamepad()

print("虛擬搖桿已啟用！")

print("\n==================================================")
print("     🎮 鍵盤 -> 虛擬手把 實時映射控制工具 🎮")
print("==================================================")
print("  請按住以下鍵盤按鍵來模擬對應的輸入：")
print("  ----------------------------------------------")
print("  按住 [ L ] 鍵 -> 模擬 L3 / LS (左搖桿下壓)")
print("  按住 [ J ] 鍵 -> 模擬 ✕ 鍵 / A 鍵 (播放/暫停)")
print("  按住 [ K ] 鍵 -> 模擬 ◯ 鍵 / B 鍵 (下一首)")
print("  按住 [ I ] 鍵 -> 模擬 ▢ 鍵 / X 鍵 (上一首)")
print("  按住 [ W ] 鍵 -> 模擬 D-Pad 上 (音量增加)")
print("  按住 [ S ] 鍵 -> 模擬 D-Pad 下 (音量減少)")
print("  ----------------------------------------------")
print("  按 [ ESC ] 鍵 -> 退出本程式")
print("==================================================")
print("💡 提示：請確保以「系統管理員身分 (Administrator)」運行此命令提示字元/PowerShell")
print("       這樣程式才能監聽全局鍵盤事件。")
print("==================================================")

active_buttons = set()
dpad_state = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE if not is_xbox else 0 # Xbox D-pad is handled via buttons

try:
    while True:
        if keyboard.is_pressed('esc'):
            print("\n正在退出模擬程式，釋放所有虛擬按鍵...")
            break

        state_changed = False

        if not is_xbox:
            # PS4 按鍵映射
            button_mappings = {
                'l': (vg.DS4_BUTTONS.DS4_BUTTON_THUMB_LEFT, "L3 (左搖桿下壓)"),
                'j': (vg.DS4_BUTTONS.DS4_BUTTON_CROSS, "✕ (手把 A)"),
                'k': (vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE, "◯ (手把 B)"),
                'i': (vg.DS4_BUTTONS.DS4_BUTTON_SQUARE, "▢ (手把 X)"),
            }
        else:
            # Xbox 360 按鍵映射
            button_mappings = {
                'l': (vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB, "LS (左搖桿下壓)"),
                'j': (vg.XUSB_BUTTON.XUSB_GAMEPAD_A, "A 鍵"),
                'k': (vg.XUSB_BUTTON.XUSB_GAMEPAD_B, "B 鍵"),
                'i': (vg.XUSB_BUTTON.XUSB_GAMEPAD_X, "X 鍵"),
                'w': (vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, "D-Pad 上"),
                's': (vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, "D-Pad 下"),
            }

        for key, (btn_code, btn_name) in button_mappings.items():
            # Xbox 的 D-pad W/S 也整合在 button_mappings 中，PS4 另外處理
            if not is_xbox and key in ['w', 's']:
                continue 
                
            is_pressed = keyboard.is_pressed(key)
            if is_pressed and btn_code not in active_buttons:
                gamepad.press_button(button=btn_code)
                active_buttons.add(btn_code)
                state_changed = True
                print(f"[按下] 鍵盤鍵 [{key.upper()}] -> 觸發虛擬手把 {btn_name}")
            elif not is_pressed and btn_code in active_buttons:
                gamepad.release_button(button=btn_code)
                active_buttons.discard(btn_code)
                state_changed = True
                print(f"[釋放] 鍵盤鍵 [{key.upper()}] -> 釋放虛擬手把 {btn_name}")

        # PS4 的 D-pad 處理 (Xbox 已在上方作為一般按鈕處理)
        if not is_xbox:
            is_up = keyboard.is_pressed('w')
            is_down = keyboard.is_pressed('s')

            new_dpad = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE
            if is_up:
                new_dpad = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH
            elif is_down:
                new_dpad = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH

            if new_dpad != dpad_state:
                gamepad.directional_pad(direction=new_dpad)
                dpad_state = new_dpad
                state_changed = True
                if new_dpad == vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH:
                    print("[按下] 鍵盤鍵 [W] -> 觸發虛擬手把 D-Pad [上]")
                elif new_dpad == vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH:
                    print("[按下] 鍵盤鍵 [S] -> 觸發虛擬手把 D-Pad [下]")
                else:
                    print("[釋放] 鍵盤 D-Pad 方向鍵已歸零")

        if state_changed:
            gamepad.update()

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n偵測到中斷，正在退出...")

finally:
    gamepad.reset()
    gamepad.update()
    print("虛擬控制器已重設並卸載。")
