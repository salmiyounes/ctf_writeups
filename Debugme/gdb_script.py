#!/usr/bin/python
from typing import List, Self
import gdb

def lookup_type(_type: str) -> "gdb.Type":
    return gdb.lookup_type(_type)

def lookup_uint8():
    return gdb.lookup_type("uint8_t")

def uint8_array(_size: int) -> "gdb.Type":
    uint8_ptr = lookup_type("uint8_t").pointer()
    return uint8_ptr.array(_size).pointer()

def to_str(s: str | bytes) -> str:
    if isinstance(s, str):
        return s
    return bytes(s).decode()


def dereference(addr: gdb.Value) -> gdb.Value | None:
    try:
        uint8_t_array = uint8_array(8)
        res = addr.cast(uint8_t_array).dereference()
        res.fetch_lazy()
        return res
    except gdb.MemoryError:
        return None

class BypassCheckBreakpoint(gdb.Breakpoint):
    def __init__(self, addr: str) -> None:
        super().__init__(f"*{addr}", type=gdb.BP_BREAKPOINT)

    def stop(self) -> bool:
        gdb.execute("set $eax = 0")
        return False


class FlagExtractorBreakpoint(BypassCheckBreakpoint):

    ADDRESS = "0x401790"

    def __init__(self) -> None:
        super().__init__(self.ADDRESS)

    def stop(self) -> bool:
        addr = gdb.parse_and_eval("$edx")
        flag = dereference(addr)
        if flag:
            flag = to_str(flag.bytes)
            print("\t[*] Found the Flag: HTB{%s}" % (flag, ))
        return True


class BreakpointInit:
    def __init__(self, break_points: List[str]) -> None:
        self._break_points = break_points
        self._init_br()

    def __iter__(self):
        return iter(self._break_points)

    def _init_br(self) -> None:
        for br in self:
            BypassCheckBreakpoint(br)

    @classmethod
    def from_list(cls, break_points: List[str]) -> Self:
        return cls(break_points)
    
def manage_breakpoints(break_points: List[str]) -> None:
    for br in break_points:
        BypassCheckBreakpoint(br)
    FlagExtractorBreakpoint()

class Start(gdb.Command):
    def __init__(self):
        super().__init__("get-the-flag", gdb.COMMAND_USER, gdb.COMPLETE_NONE, True)

    def invoke(self, args, from_tty) -> None:  # type: ignore
        gdb.execute(f"set $eip = 0x401620")
        # set breakpoints
        manage_breakpoints(
            [
                "0x401632",  # cmp    al,0x0
                "0x40164A",  # cmp    al,0x0
                "0x401674",  # cmp    eax,0x3e8
            ]
        )
        gdb.execute("continue")
        return

# ---> Register
Start()
