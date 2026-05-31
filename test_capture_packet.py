import socket
import struct
import math
import sys
import os

UDP_IP = "127.0.0.1"
UDP_PORT = 501

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(10.0) # 10 seconds timeout to catch a packet
    
    # Enable socket reuse
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception:
        pass
        
    try:
        sock.bind((UDP_IP, UDP_PORT))
        print(f"[Telemetry Capture] Capturing a real telemetry packet on {UDP_IP}:{UDP_PORT} ...")
        print("Please start driving in Forza to send packets.")
        
        # Capture a packet
        data, addr = sock.recvfrom(1024)
        print(f"Successfully captured a packet of size {len(data)} bytes from {addr}!")
        
        # Save raw packet
        os.makedirs("scratch", exist_ok=True)
        with open("scratch/captured_packet.bin", "wb") as f:
            f.write(data)
        print("Raw packet saved to scratch/captured_packet.bin")
        print("-" * 60)
        
        # Print diagnostic mapping
        if len(data) >= 308:
            is_race_on = struct.unpack_from('<i', data, 0)[0]
            max_rpm = struct.unpack_from('<f', data, 8)[0]
            idle_rpm = struct.unpack_from('<f', data, 12)[0]
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
            
            print("Parsed Values:")
            print(f"  IsRaceOn:   {is_race_on}")
            print(f"  Max RPM:    {max_rpm:.0f} RPM")
            print(f"  Idle RPM:   {idle_rpm:.0f} RPM")
            print(f"  RPM:        {rpm:.0f} RPM")
            print(f"  Speed:      {speed:.1f} km/h")
            print(f"  Lap Number: {lap}")
            print(f"  Race Pos:   {pos}")
            print(f"  Accel:      {accel}")
            print(f"  Brake:      {brake}")
            print(f"  Clutch:     {clutch}")
            print(f"  Handbrake:  {handbrake}")
            print(f"  Gear (Raw): {gear} -> {('R' if gear == 0 else ('N' if gear == 11 else str(gear)))}")
            print(f"  Steer:      {steer}")
            
            print("-" * 60)
            print("Hex dump around offsets 300-310:")
            hex_slice = data[300:311]
            print("  Offset 300: " + " ".join(f"{b:02X}" for b in hex_slice))
            print("  Label:      [Lap_L] [Lap_H] [Pos] [Acc] [Brk] [Clt] [Hbrk] [Gear] [Str] [Dln] [Abd]")
            
        else:
            print(f"Packet is too short ({len(data)} bytes) to have V2 Dash fields.")
            
    except socket.timeout:
        print("Timeout! No UDP packets received on port 501. Is the game running and configured correctly?")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
