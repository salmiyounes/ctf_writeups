from typing import List
import argparse
import sys
from pathlib import Path
import pefile

XOR_KEY: int = 0x5C
MAIN_START_VA: int = 0x401620
MAIN_END_VA: int = 0x401792


def map_va_to_rva(pe: pefile.PE, va: int) -> int:
    return va - pe.OPTIONAL_HEADER.ImageBase


def map_va_to_offset(pe: pefile.PE, va: int) -> int | None:
    rva = map_va_to_rva(pe, va)
    try:
        return pe.get_offset_from_rva(rva)
    except pefile.PEFormatError:
        return None


def main(argv: List[str]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str)
    parser.add_argument("-o", "--output", type=str)
    args = parser.parse_args(argv[1:])

    if args.file:
        pe = pefile.PE(args.file)

        length = MAIN_END_VA - MAIN_START_VA
        main_offset = map_va_to_offset(pe, MAIN_START_VA)

        data = bytearray(pe.__data__)

        for i in range(length):
            data[main_offset + i] ^= XOR_KEY

        pe.__data__ = data
        output_file = f"{Path(args.file).stem}_patched.exe"
        if args.output:
            output_file = args.output

        pe.write(output_file)
        print(f"[!] Patched {length} bytes.")
        print(f"[!] Write to file {output_file}.")
    return


if __name__ == "__main__":
    main(sys.argv)
