import struct
import math

def main():
    try:
        with open("scratch/captured_packet.bin", "rb") as f:
            data = f.read()
        print(f"File loaded successfully: {len(data)} bytes")
        
        # 1. Dump as float32
        print("\n--- Float32 Dump (Offset: Value) ---")
        for offset in range(0, len(data) - 3, 4):
            val = struct.unpack_from('<f', data, offset)[0]
            # Print if it looks like a reasonable float (not NaN or Inf, and not huge/tiny unless expected)
            if not math.isnan(val) and not math.isinf(val) and abs(val) < 1000000:
                print(f"  Offset {offset:3d} (float32): {val:12.4f}")
            else:
                print(f"  Offset {offset:3d} (float32): [Invalid float: {val}]")
                
        # 2. Dump as int32
        print("\n--- Int32 Dump (Offset: Value) ---")
        for offset in range(0, len(data) - 3, 4):
            val = struct.unpack_from('<i', data, offset)[0]
            print(f"  Offset {offset:3d} (int32): {val:12d}")
            
        # 3. Dump the last 50 bytes as single uint8/int8
        print("\n--- Uint8/Int8 Dump for last 50 bytes ---")
        start_offset = len(data) - 50
        for offset in range(start_offset, len(data)):
            u8 = struct.unpack_from('<B', data, offset)[0]
            s8 = struct.unpack_from('<b', data, offset)[0]
            print(f"  Offset {offset:3d}: uint8={u8:3d} (0x{u8:02X}) | int8={s8:4d}")
            
    except Exception as e:
        print(f"Error analyzing packet: {e}")

if __name__ == "__main__":
    main()
