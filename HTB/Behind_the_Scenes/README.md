**Name:** Behind the Scenes

**Category:** Reversing

**Difficulty:** Very Easy

**Link:**  https://app.hackthebox.com/challenges/Behind%2520the%2520Scenes 

## 1. Initial Analysis
Execution shows the binary requires a password as a command-line argument:

```sh
➜  rev_behindthescenes  ./behindthescenes
./challenge <password>
➜  rev_behindthescenes  ./behindthescenes 12345
➜  rev_behindthescenes
```
To understand how the input is processed, we move to static analysis in Ghidra.

## 2. The Decompiler Trap
Upon opening `main` function, the decompilation looks incomplete. We see a signal handler setup followed by an `invalidInstructionException()`.

```c
void main(void)

{
  code *pcVar1;
  long in_FS_OFFSET;
  sigaction local_a8;
  undefined8 local_10;
  
  local_10 = *(undefined8 *)(in_FS_OFFSET + 0x28);
  memset(&local_a8,0,0x98);
  sigemptyset(&local_a8.sa_mask);
  local_a8.__sigaction_handler.sa_handler = segill_sigaction;
  local_a8.sa_flags = 4;
  sigaction(4,&local_a8,(sigaction *)0x0);
                    /* WARNING: Does not return */
  pcVar1 = (code *)invalidInstructionException();
  (*pcVar1)();
}
```

Investigating the assembly reveals the `UD2` instruction:

```asm
001012e6  0f 0b    UD2
```
**The Issue**: `UD2` explicitly generates an invalid opcode. This triggers a SIGILL signal. Ghidra seems to stop disassembling at this point because the UD2 instruction generates an invalid opcode exception, and the saved instruction pointer is the address of the UD2 instruction, rather than the following one. It should not, without careful consideration, proceed to the following instruction.
However, this binary uses a signal handler to redirect execution to the code after the UD2.

## 3. Patching the Binary
To solve the issue and restore the control flow in Ghidra, we need to patch the binary by replacing `UD2` with `NOP` (No-Operation) instructions ($0x90$) allows the decompiler to follow the logic linearly.
I used the following script to automate the patch:

```python
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
```

## 4. Recovery & Flag Extraction
After loading the patched binary back into Ghidra, the `main` function logic becomes clear. The program performs a series of strncmp (string comparisons) against four hardcoded string segments.

```c
  if (param_1 == 2) {
    sVar3 = strlen(*(char **)(param_2 + 8));
    if (sVar3 == 0xc) {
      iVar1 = strncmp(*(char **)(param_2 + 8),"***",3);
      if (iVar1 == 0) {
        iVar1 = strncmp((char *)(*(long *)(param_2 + 8) + 3),"***",3);
        if (iVar1 == 0) {
          iVar1 = strncmp((char *)(*(long *)(param_2 + 8) + 6),"***",3);
          if (iVar1 == 0) {
            iVar1 = strncmp((char *)(*(long *)(param_2 + 8) + 9),"***",3);
            if (iVar1 == 0) {
              printf("> HTB{%s}\n",*(undefined8 *)(param_2 + 8)) ;
              uVar2 = 0;
            }
            else {
              uVar2 = 0;
            }
          }
          else {
            uVar2 = 0;
          }
        }
        else {
          uVar2 = 0;
        }
      }
      else {
        uVar2 = 0;
      }
    }
    else {
      uVar2 = 0;
    }
  }
  else {
    puts("./challenge <password>");
    uVar2 = 1;
  }
```

By concatenating these constants in order, we recover the flag:

```sh
➜  rev_behindthescenes  ./behindthescenes ************
> HTB{************}
```

## Useful Resources
+ [x86 Instruction Set Reference](https://mudongliang.github.io/x86/html/file_module_x86_id_318.html)
+ [ud2 x86 instruction is breaking disassembly process](https://github.com/NationalSecurityAgency/ghidra/issues/4113)
+ [sigaction](https://en.wikipedia.org/wiki/Sigaction)