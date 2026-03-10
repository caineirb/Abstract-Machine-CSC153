#!/usr/bin/env python3
"""
Abstract Stack Machine
======================
A simple stack-based virtual machine that executes assembly-like instructions from `COMP-7451-Notes.pdf`.
"""
import re
import sys
from typing import Any, Dict, List, Tuple, Optional

# Function helpers
def _pop2(S: List[int]) -> tuple[int, int]:
    """Pop two values and return them as (val1, val2) — val2 was pushed last."""
    if len(S) < 2:
        raise IndexError(f"Stack underflow: need 2 operands, got {len(S)}")
    val2 = S.pop()
    val1 = S.pop()
    return val1, val2

def _pop1(S: List[int]) -> int:
    if not S:
        raise IndexError("Stack underflow: stack is empty")
    return S.pop()

# Memory / stack I/O
def push(S: List[int], N: Optional[int] = None,
         M: Optional[Dict[str, int]] = None, x: Optional[str] = None) -> None:
    """Push a literal integer N, or the value stored at memory address x."""
    if N is not None:
        S.append(N)
    elif M is not None and x is not None:
        if x not in M:
            raise KeyError(f"Undefined memory address: '{x}'")
        S.append(M[x])
    else:
        raise ValueError("PUSH requires either a literal value or a memory address")

def pop(S: List[int], M: Dict[str, int], x: str) -> None:
    """Pop the top of the stack into memory address x."""
    M[x] = _pop1(S)

# Arithmetic Operations
def add(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(a + b)

def sub(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(a - b)

def mul(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(a * b)

def div(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(0 if b == 0 else a // b)   # Default to 0 if division by 0

# Boolean / bitwise
def bnot(S: List[int]) -> None:
    S.append(0 if _pop1(S) else 1)

def bor(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(1 if a or b else 0)

def band(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(1 if a and b else 0)

def bnand(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(0 if a and b else 1)

def bnor(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(0 if a or b else 1)

def bxor(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(0 if a == b else 1)

def bxnor(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(1 if a == b else 0)

# Comparisons
def eq(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(1 if a == b else 0)

def le(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(1 if a < b else 0)

def ge(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(1 if a > b else 0)

def leq(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(1 if a <= b else 0)

def geq(S: List[int]) -> None:
    a, b = _pop2(S)
    S.append(1 if a >= b else 0)

# Control flow
def jump(label: str, labels: Dict[str, int]) -> int:
    if label not in labels:
        raise KeyError(f"Undefined label: '{label}'")
    return labels[label]

def jumpz(S: List[int], label: str, labels: Dict[str, int], insPoint: int) -> int:
    """Jump to label if top of stack is zero, otherwise advance."""
    return jump(label, labels) if _pop1(S) == 0 else insPoint + 1

def lab(label: str, labels: Dict[str, int], insPoint: int) -> None:
    """Register a label pointing to the instruction after itself."""
    labels[label] = insPoint + 1

def halt() -> bool:
    return False

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
def assemble(asm_code: str) -> List[Instruction]:
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
def initstate(asm_code: List[Instruction]) -> State:
    code: List[Instruction] = asm_code
    stack: List[int] = []
    memory: Dict[str, int] = {}

    return (code, stack, memory)

def meval(state: State) -> State:
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

def readcode() -> str:
    codestr = sys.stdin.read()

    return codestr

def main() -> None:
    try:
        codestr = readcode()
        code = assemble(codestr)
        initialstate = initstate(code)
        finalstate = meval(initialstate)
        _, stack, memory = finalstate

        print(f"Final (stack, memory): ({stack}, {memory})")
    except (ValueError, KeyError, IndexError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
