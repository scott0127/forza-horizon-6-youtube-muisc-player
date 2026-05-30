import pygame
import vgamepad as vg
import time
import os

# 確保輸出編碼正確 (如果在 cmd 下)
import sys
sys.stdout.reconfigure(encoding='utf-8')

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.joystick.init()

print("初始化虛擬 PS4 控制器 (vgamepad)...")
gamepad = vg.VDS4Gamepad()

# 等待系統掛載虛擬控制器
time.sleep(2)

joysticks = []
count = pygame.joystick.get_count()
print(f"Pygame 偵測到 {count} 個搖桿")
for i in range(count):
    joy = pygame.joystick.Joystick(i)
    joy.init()
    joysticks.append(joy)
    print(f"[{i}] 綁定搖桿: {joy.get_name()} (GUID: {joy.get_guid()})")

print("\n模擬按下 L3 (DS4_BUTTON_THUMB_LEFT)...")
gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_THUMB_LEFT)
gamepad.update()

# 等待事件並讀取
found = False
for _ in range(20):
    time.sleep(0.1)
    pygame.event.pump()
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            print(f"✅ Pygame 偵測到按鈕按下！來自搖桿 {event.joy}，對應編號 (Button ID) 是: {event.button}")
            found = True
    if found:
        break
        
if not found:
    print("沒有偵測到任何按鈕事件。")

print("釋放按鈕...")
gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_THUMB_LEFT)
gamepad.update()

gamepad.reset()
gamepad.update()
pygame.quit()
