import socket
import struct
import math
import sys
import os

UDP_IP = "127.0.0.1"
UDP_PORT = 501

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(30.0) # 30 seconds timeout to catch a moving packet
    
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception:
        pass
        
    try:
        sock.bind((UDP_IP, UDP_PORT))
        print("📡 Listening for an ACTIVE telemetry packet (RPM > 2000)...")
        print("🏎️  PLEASE GO DRIVE YOUR CAR AND REVISE THE ENGINE NOW!")
        
        captured = False
        while not captured:
            data, addr = sock.recvfrom(1024)
            if len(data) >= 44:
                rpm = struct.unpack_from('<f', data, 16)[0]
                if rpm > 2000.0:
                    print(f"✅ Caught active packet! RPM is {rpm:.0f}. Saving to scratch/moving_packet.bin...")
                    with open("scratch/moving_packet.bin", "wb") as f:
                        f.write(data)
                    captured = True
                    
                    # Run quick diagnostic analysis
                    print("-" * 60)
                    print(f"Packet Length: {len(data)} bytes")
                    
                    # Print standard V1 fields (offsets 0-232)
                    is_race_on = struct.unpack_from('<i', data, 0)[0]
                    max_rpm = struct.unpack_from('<f', data, 8)[0]
                    idle_rpm = struct.unpack_from('<f', data, 12)[0]
                    vx = struct.unpack_from('<f', data, 32)[0]
                    vy = struct.unpack_from('<f', data, 36)[0]
                    vz = struct.unpack_from('<f', data, 40)[0]
                    calc_speed = math.sqrt(vx**2 + vy**2 + vz**2) * 3.6
                    
                    print(f"  IsRaceOn: {is_race_on}")
                    print(f"  RPM: {rpm:.0f} / Max: {max_rpm:.0f} (Idle: {idle_rpm:.0f})")
                    print(f"  Calculated Speed (from velocity vector): {calc_speed:.1f} km/h")
                    
                    # Search for the real Gear value in the last 100 bytes!
                    # A real gear is usually 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 or 11 (Neutral), or 0 (Reverse).
                    # Since we are driving actively (RPM > 2000), gear should be 1, 2, 3, 4, etc.
                    # Let's inspect all bytes from offset 200 to 324!
                    print("\n--- Inspecting Bytes for Gear (looking for 1-10 while driving) ---")
                    for offset in range(200, len(data)):
                        val = data[offset]
                        # If a byte has a value of 1-10, it could be the gear!
                        # Let's print all bytes in this range to see their indices.
                        print(f"  Offset {offset:3d}: {val:3d} (0x{val:02X})")
                        
                    # Let's also print all Float32 values from offset 200 to 320 to see where Speed is!
                    print("\n--- Inspecting Float32 from Offset 200 to 320 (looking for Speed ~ {:.1f}) ---".format(calc_speed / 3.6))
                    for offset in range(200, len(data) - 3, 4):
                        fval = struct.unpack_from('<f', data, offset)[0]
                        print(f"  Offset {offset:3d} (float32): {fval:12.4f}")
                        
        if not captured:
            print("❌ Did not capture an active packet.")
            
    except socket.timeout:
        print("❌ Timeout! No UDP packets received. Please make sure the game is running and sending data on port 501.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
