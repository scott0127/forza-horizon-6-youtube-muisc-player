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
            
            # Limit console printing to 10Hz (every 0.1s)
            current_time = time.time()
            if current_time - last_print_time >= 0.1:
                if len(data) >= 232: # Sled V1 is at least 232 bytes
                    is_race_on = struct.unpack_from('<i', data, 0)[0]
                    max_rpm = struct.unpack_from('<f', data, 8)[0]
                    rpm = struct.unpack_from('<f', data, 16)[0]
                    
                    # Local Velocities (in car's local frame)
                    vx = struct.unpack_from('<f', data, 32)[0]
                    vy = struct.unpack_from('<f', data, 36)[0]
                    vz = struct.unpack_from('<f', data, 40)[0]
                    
                    # Speed (mps) from velocity vector
                    speed_mps = math.sqrt(vx**2 + vy**2 + vz**2)
                    speed_kph = speed_mps * 3.6
                    
                    # Detect if game sends Dash V2 data (offsets after 232 are not all 0)
                    has_dash_v2 = False
                    if len(data) >= 308:
                        # Check some Dash V2 fields like LapNumber (300) or Gear (307)
                        # or check if the slice data[232:308] has any non-zero bytes
                        if any(b != 0 for b in data[232:308]):
                            has_dash_v2 = True
                            
                    gear = 11  # Default to Neutral
                    gear_source = "Parsed"
                    
                    if has_dash_v2:
                        try:
                            gear = struct.unpack_from('<B', data, 307)[0]
                        except Exception:
                            pass
                    else:
                        # Forza 6 Sled Dynamic Gear Estimator
                        gear_source = "Estimated"
                        if vz < -0.5: # Moving backward
                            gear = 0  # Reverse
                        elif speed_kph < 3.0:
                            gear = 11 # Neutral
                        else:
                            ratio = rpm / speed_kph
                            if ratio >= 135.0:
                                gear = 1
                            elif ratio >= 88.0:
                                gear = 2
                            elif ratio >= 60.0:
                                gear = 3
                            elif ratio >= 43.0:
                                gear = 4
                            elif ratio >= 31.0:
                                gear = 5
                            elif ratio >= 23.0:
                                gear = 6
                            elif ratio >= 16.0:
                                gear = 7
                            else:
                                gear = 8
                                
                    status = "RACING" if is_race_on == 1 else "PAUSED"
                    gear_str = 'R' if gear == 0 else ('N' if gear == 11 else str(gear))
                    
                    print(
                        f"[{packet_count:5d} Pkts] "
                        f"State: {status:6s} | "
                        f"RPM: {rpm:5.0f}/{max_rpm:5.0f} | "
                        f"Speed: {speed_kph:5.1f} km/h | "
                        f"Gear ({gear_source}): {gear_str} | "
                        f"Vz (Local Fwd): {vz:6.2f} m/s",
                        flush=True
                    )
                else:
                    print(f"[{packet_count:5d} Pkts] Received unknown short packet ({len(data)} bytes).", flush=True)
                
                last_print_time = current_time
                
    except KeyboardInterrupt:
        print("\n🛑  Listener stopped by user.")
    except Exception as e:
        print(f"\n❌  Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
