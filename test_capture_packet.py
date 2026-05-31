import socket
import struct
import math
import sys
import time
import os

UDP_IP = "127.0.0.1"
UDP_PORT = 501

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Enable socket reuse
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception:
        pass
        
    try:
        sock.bind((UDP_IP, UDP_PORT))
        print("============================================================")
        print(f"📡  Continuous Telemetry Listener started on {UDP_IP}:{UDP_PORT}")
        print("💡  Press Ctrl+C to stop the listener.")
        print("💡  Please start driving in Forza to stream telemetry data.")
        print("============================================================")
        
        last_print_time = time.time()
        packet_count = 0
        
        while True:
            data, addr = sock.recvfrom(1024)
            packet_count += 1
            
            # Limit console printing to 10Hz (every 0.1s) to be readable but responsive
            current_time = time.time()
            if current_time - last_print_time >= 0.1:
                if len(data) >= 308:
                    is_race_on = struct.unpack_from('<i', data, 0)[0]
                    max_rpm = struct.unpack_from('<f', data, 8)[0]
                    rpm = struct.unpack_from('<f', data, 16)[0]
                    speed = struct.unpack_from('<f', data, 244)[0] * 3.6 # m/s to km/h
                    
                    lap = struct.unpack_from('<H', data, 300)[0]
                    pos = struct.unpack_from('<B', data, 302)[0]
                    accel = struct.unpack_from('<B', data, 303)[0]
                    brake = struct.unpack_from('<B', data, 304)[0]
                    clutch = struct.unpack_from('<B', data, 305)[0]
                    handbrake = struct.unpack_from('<B', data, 306)[0]
                    gear = struct.unpack_from('<B', data, 307)[0]
                    steer = struct.unpack_from('<b', data, 308)[0]
                    
                    status = "RACING" if is_race_on == 1 else "PAUSED"
                    gear_str = 'R' if gear == 0 else ('N' if gear == 11 else str(gear))
                    
                    print(
                        f"[{packet_count:5d} Pkts] "
                        f"State: {status:6s} | "
                        f"RPM: {rpm:5.0f}/{max_rpm:5.0f} | "
                        f"Speed: {speed:5.1f} km/h | "
                        f"Gear: {gear_str} (Raw: {gear:2d}) | "
                        f"Inputs: Acc:{accel:3d} Brk:{brake:3d} Hbrk:{handbrake:3d} | "
                        f"Steer: {steer:4d}",
                        flush=True
                    )
                else:
                    print(f"[{packet_count:5d} Pkts] Received V1 Sled packet ({len(data)} bytes) - No Gear data available.", flush=True)
                
                last_print_time = current_time
                
    except KeyboardInterrupt:
        print("\n🛑  Listener stopped by user.")
    except Exception as e:
        print(f"\n❌  Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
