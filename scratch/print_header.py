import struct

def main():
    try:
        with open("scratch/captured_packet.bin", "rb") as f:
            data = f.read()
        print(f"File loaded successfully: {len(data)} bytes")
        
        print("\n--- Header Dump (0 to 32) ---")
        for offset in range(0, 32, 4):
            fval = struct.unpack_from('<f', data, offset)[0]
            ival = struct.unpack_from('<i', data, offset)[0]
            uval = struct.unpack_from('<I', data, offset)[0]
            print(f"  Offset {offset:2d}: float={fval:12.4f} | int32={ival:12d} | uint32={uval:12d}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
