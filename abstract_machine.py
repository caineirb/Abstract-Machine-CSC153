#!/usr/bin/env python3
"""
Abstract Stack Machine
======================
A simple stack-based virtual machine that executes assembly-like instructions.

Instruction syntax (semicolon-separated):
    PUSH 42          ; push literal
    PUSH M[x]        ; push value from memory address x
    POP  M[x]        ; pop top of stack into memory address x
    ADD / SUB / MUL / DIV
    NOT / OR / AND / NAND / NOR / XOR / XNOR
    EQ / LE / GE / LEQ / GEQ
    J  <label>       ; unconditional jump
    JZ <label>       ; jump if top of stack is zero
    LAB <label>      ; declare a label
    HLT              ; halt
"""
import re
import sys
from typing import Any, Dict, List, Tuple

from instructions import (
    push, pop, add, sub, mul, div,
    bnot, bor, band, bnand, bnor, bxor, bxnor,
    eq, le, ge, leq, geq,
    jump, jumpz, lab, halt,
)

# Opcode table
OPERATIONS: Dict[str, Any] = {
    "PUSH": push, "POP":  pop,
    "ADD":  add,  "SUB":  sub,  "MUL": mul,  "DIV": div,
    "NOT":  bnot, "OR":   bor,  "AND": band,
    "NAND": bnand,"NOR":  bnor, "XOR": bxor, "XNOR": bxnor,
    "EQ":   eq,   "LE":   le,   "GE":  ge,   "LEQ":  leq,  "GEQ": geq,
    "J":    jump, "JZ":   jumpz,
    "LAB":  lab,  "HLT":  halt,
}

# Type alias for a decoded instruction tuple
Instruction = Tuple[Any, ...]


# Parser
def asm_parser(asm_code: str) -> List[Instruction]:
    """
    Parse semicolon-separated assembly source into a list of instruction tuples.

    Each tuple is one of:
        (fn, None)          – no-operand instruction  (e.g. ADD, HLT)
        (fn, int)           – literal integer operand (e.g. PUSH 5)
        (fn, str)           – label operand           (e.g. J loop)
        (fn, 'M', str)      – memory address operand  (e.g. PUSH M[x])
    """
    instructions: List[Instruction] = []
    asm_code = asm_code.strip()     # Strip the code first

    for line_no, raw in enumerate(asm_code.split(";"), start=1):    # Split each statement based on ';' separator
        tokens = raw.split()
        if not tokens:
            continue  # skip blank segments

        mnemonic = tokens[0].upper()

        if mnemonic not in OPERATIONS:  # Check if the operation is supported
            raise ValueError(f"Line {line_no}: unknown instruction '{tokens[0]}'")

        if len(tokens) > 2:             # Since each instruction is at most have 2 val (operation and param)
            raise ValueError(
                f"Line {line_no}: too many tokens — expected at most 2, got {len(tokens)}"
            )

        fn = OPERATIONS[mnemonic]

        if len(tokens) == 1:
            instructions.append((fn, None))
            continue

        operand = tokens[1]

        # Memory address: M[varname]
        mem_match = re.fullmatch(r"M\[([^\]]+)\]", operand)
        if mem_match:
            instructions.append((fn, "M", mem_match.group(1)))
            continue

        # Integer literal
        if re.fullmatch(r"-?\d+", operand):
            instructions.append((fn, int(operand)))
            continue

        # Label reference
        instructions.append((fn, operand))

    return instructions


# Execution engine
def collect_labels(code: List[Instruction]) -> Dict[str, int]:
    """First pass: register every LAB instruction so jumps can resolve them."""
    labels: Dict[str, int] = {}
    for idx, instr in enumerate(code):
        if instr[0] is lab:
            _, label_name = instr
            lab(label_name, labels, idx)
    return labels


def run(code: List[Instruction], *, debug: bool = False) -> Tuple[List[int], Dict[str, int]]:
    """
    Execute *code* and return the final stack.

    Parameters
    ----------
    code  : parsed instruction list from :func:`asm_parser`
    debug : when True, print the machine state before each instruction
    """
    stack: List[int] = []
    memory: Dict[str, int] = {}
    labels = collect_labels(code)
    ip = 0  # instruction pointer
    isRunning = True

    while isRunning:
        instr = code[ip]
        fn = instr[0]

        if debug:
            print(f"  ip={ip:3d}  stack={stack}  mem={memory}")
            print(f"         {instr}")
            print("-" * 40)

        # Prioritize control flow first
        if fn is jump:
            ip = fn(instr[1], labels)
            continue
        if fn is jumpz:
            ip = fn(stack, instr[1], labels, ip)
            continue
        if fn is lab:
            ip += 1
            continue
        if fn is halt:
            isRunning = fn()
            continue

        # Then the I/O operations
        if len(instr) == 3 and instr[1] == "M":
            _, _, addr = instr
            if fn is push:
                fn(stack, None, memory, addr)
            else:
                fn(stack, memory, addr)
            ip += 1
            continue

        # Operations
        if len(instr) == 2:
            _, param = instr
            if param is None:
                fn(stack)
            else:
                fn(stack, param)

        ip += 1

    return (stack, memory)

def main() -> None:
    debug_mode = "--debug" in sys.argv
    asm_code = input()

    try:
        code = asm_parser(asm_code)
        final_stack = run(code, debug=debug_mode)
        print(f"Final state: {final_stack}")
    except (ValueError, KeyError, IndexError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()