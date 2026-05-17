from typing import List, Any

XOR_IDX: List[int] = [
    2, 4, 6, 8, 11, 13
]

PERM: List[int] = [
    9, 12, 2, 10, 4, 1, 6, 3, 8, 5, 7, 11, 0, 13
]

# Compute inverse permutation once
INV_PERM = [0] * 14
for i, p in enumerate(PERM):
    INV_PERM[p] = i

def reverse_scramble_and_xor(string: List[str], key: int) -> str:
    assert len(string) == 14

    # XOR is self inverted, know your math
    for i in XOR_IDX:
        string[i] = chr(ord(string[i]) ^ key)

    # Step 2: undo permutation (8 rounds)
    for _ in range(8):
        temp: List[Any] = [None] * 14
        for i in range(14):
            temp[i] = string[INV_PERM[i]]
        string = temp

    return "".join(string)

def swap_pos(s: List[str], i: int, j: int):
    s[i], s[j] = s[j], s[i]

def swap_multiple(s: str) -> str:
    assert len(s) == 28

    chars = list(s)

    swap_pos(chars, 0, 12)
    swap_pos(chars, 14, 26)
    swap_pos(chars, 4, 8)
    swap_pos(chars, 20, 23)

    return "".join(chars)

if __name__ == "__main__":
    raw_output = "RV{r15]_vcP3o]L_tazmfSTaa3s0"
    
    # 1. Split into encrypted halves
    mid = len(raw_output) // 2
    p1, p2 = list(raw_output[:mid]), list(raw_output[mid:])

    # 2. Reverse the scramble and XOR (Key 2 for P1, Key 3 for P2)
    decrypted_str = reverse_scramble_and_xor(p1, 2) + reverse_scramble_and_xor(p2, 3)

    # 3. Undo the final positioning swaps
    flag = swap_multiple(decrypted_str)
    print("[+] Flag Recovered: HTB{%s}" % (flag, ))