#!/usr/bin/env python3
"""
Abstract Stack Machine
======================
A simple stack-based virtual machine that executes assembly-like instructions from `COMP-7451-Notes.pdf`.
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

# Parse and clean-up the asm code input
Instruction = Tuple[Any, ...]
def asm_parser(asm_code: str) -> List[Instruction]:
    """
    Parse semicolon-separated assembly source into a list of instruction tuples.

    Each tuple is one of:
        (fn, None)                  – no-operand instruction  (e.g. ADD, HLT)
        (fn, int)                   – literal integer operand (e.g. PUSH 5)
        (fn, str | int)             – label operand           (e.g. J loop)
        (fn, 'M', str)              – memory address operand  (e.g. PUSH M[x])
    """
    instructions: List[Instruction] = []
    asm_code = asm_code.strip()     # Strip the code

    for line_no, statement in enumerate(asm_code.split(";"), start=1):    # Split each statement based on ';' separator
        tokens = statement.split()
        if not tokens:
            continue  # skip blank segments (incase there are extra spaces inside each statement)

        operation = tokens[0].upper()

        if operation not in OPERATIONS:  # Check if the operation is supported
            raise ValueError(f"Statement {line_no}: unknown instruction '{tokens[0]}'")

        if len(tokens) > 2:             # Since each instruction is at most have 2 val (operation and param)
            raise ValueError(
                f"Statement {line_no}: too many tokens — expected at most 2, got {len(tokens)}"
            )

        fn = OPERATIONS[operation]

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
            lab(str(label_name), labels, idx)
    return labels

State = Tuple[List[Instruction], List[int], Dict[str, int]]
def initial_state(asm_code: List[Instruction]):
    code: List[Instruction] = asm_code
    stack: List[int] = []
    memory: Dict[str, int] = {}

    return (code, stack, memory)

def run(state: State) -> State:
    code, stack, memory = state
    labels = collect_labels(code)
    ip = 0  # instruction pointer
    isRunning = True

    while isRunning:
        instr = code[ip]
        fn = instr[0]
        # Prioritize control flow first
        if fn is jump:
            ip = fn(str(instr[1]), labels)
            continue
        if fn is jumpz:
            ip = fn(stack, str(instr[1]), labels, ip)
            continue
        if fn is lab:
            ip += 1
            continue
        if fn is halt:
            isRunning = fn()
            continue

        # Then the I/O operations on memory
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

    return state

def main() -> None:
    try:
        asm_code = input()
        print(f"{asm_code=}")
        code = asm_parser(asm_code)
        state = initial_state(code)
        final_state = run(state=state)

        print(f"Final (stack, memory): {final_state[1:]}")
    except (ValueError, KeyError, IndexError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
