import sys

UD2_OPCODE = b'\x0f\x0b'
NOP_OPCODE = b'\x90\x90'

if __name__ == "__main__":
    target_file: str = sys.argv[1]

    with open(target_file, "rb") as f:
        data = f.read()

    new_data = data.replace(UD2_OPCODE, NOP_OPCODE)
    
    with open(target_file + "_patched", "wb") as f:
        f.write(new_data)    