import socket
import struct
import math
import time

# 設定接收的 IP 與 Port，必須和你在遊戲內設定的完全一樣
UDP_IP = "127.0.0.1"
UDP_PORT = 501

def main():
    # 建立 UDP Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind((UDP_IP, UDP_PORT))
        print(f"🏎️ 成功啟動遙測接收器！")
        print(f"📡 正在監聽 {UDP_IP}:{UDP_PORT} ...")
        print("💡 請確保遊戲內的 Data Out 已開啟，且設定為相同的 IP 與 Port。")
        print("-" * 50)
        
        last_print_time = time.time()
        packet_count = 0
        
        while True:
            # 接收資料 (Forza 封包大小通常為 324 bytes 或 232 bytes)
            data, addr = sock.recvfrom(1024)
            packet_count += 1
            
            # 我們限制每秒鐘只印出兩次 (0.5秒一次)，以免終端機被洗版 (因為遊戲是 60Hz 狂送)
            current_time = time.time()
            if current_time - last_print_time >= 0.5:
                # 簡單防護：確保收到的封包夠大
                if len(data) >= 44: 
                    # 根據微軟官方的 UDP 封包格式解析 (Little-endian)
                    # Offset 0 (4 bytes): IsRaceOn (int32)
                    # Offset 16 (4 bytes): CurrentEngineRpm (float)
                    # Offset 32, 36, 40 (4 bytes each): Velocity X, Y, Z (float)
                    
                    is_race_on = struct.unpack_from('<i', data, 0)[0]
                    rpm = struct.unpack_from('<f', data, 16)[0]
                    
                    vx = struct.unpack_from('<f', data, 32)[0]
                    vy = struct.unpack_from('<f', data, 36)[0]
                    vz = struct.unpack_from('<f', data, 40)[0]
                    
                    # 計算總時速 (公尺/秒 轉換為 公里/小時)
                    speed_mps = math.sqrt(vx**2 + vy**2 + vz**2)
                    speed_kmh = speed_mps * 3.6
                    
                    # 印出結果
                    status = "✅ 駕駛中" if is_race_on == 1 else "⏸️ 暫停或選單"
                    print(f"[{packet_count} 封包] 狀態: {status} | 引擎轉速: {rpm:5.0f} RPM | 當前時速: {speed_kmh:5.1f} km/h")
                    
                else:
                    print(f"⚠️ 收到未知長度的封包：{len(data)} bytes")
                    
                last_print_time = current_time

    except KeyboardInterrupt:
        print("\n🛑 測試程式已手動關閉。")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
