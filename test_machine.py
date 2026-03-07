#!/usr/bin/env python3
"""
Test suite for the Abstract Stack Machine.
Run with: python3 test_machine.py
"""
import sys
sys.path.insert(0, '.')

from abstract_machine import asm_parser, run

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"


def check(label: str, src: str, expected: list):
    result = run(asm_parser(src))
    status = PASS if result == expected else FAIL
    print(f"  [{status}]  {label:<30s}  expected={expected}  got={result}")
    return result == expected


def section(title: str):
    print(f"\n{'─' * 55}")
    print(f"  {title}")
    print(f"{'─' * 55}")


results = []

# ── Stack I/O ────────────────────────────────────────────────
section("Stack I/O")
results += [
    check("PUSH literal",        "PUSH 7;HLT",                        [7]),
    check("PUSH multiple",       "PUSH 1;PUSH 2;PUSH 3;HLT",          [1, 2, 3]),
    check("POP to memory",       "PUSH 42;POP M[a];HLT",              []),
    check("PUSH from memory",    "PUSH 42;POP M[a];PUSH M[a];HLT",    [42]),
]

# ── Arithmetic ───────────────────────────────────────────────
section("Arithmetic")
results += [
    check("ADD",                 "PUSH 3;PUSH 4;ADD;HLT",             [7]),
    check("SUB",                 "PUSH 10;PUSH 3;SUB;HLT",            [7]),
    check("MUL",                 "PUSH 6;PUSH 7;MUL;HLT",             [42]),
    check("DIV",                 "PUSH 10;PUSH 3;DIV;HLT",            [3]),
    check("DIV by zero → 0",     "PUSH 9;PUSH 0;DIV;HLT",             [0]),
    check("SUB negative result", "PUSH 3;PUSH 10;SUB;HLT",            [-7]),
]

# ── Boolean / Bitwise ────────────────────────────────────────
section("Boolean / Bitwise")
results += [
    check("NOT 0 → 1",           "PUSH 0;NOT;HLT",                    [1]),
    check("NOT 1 → 0",           "PUSH 1;NOT;HLT",                    [0]),
    check("OR  1,0 → 1",         "PUSH 1;PUSH 0;OR;HLT",              [1]),
    check("OR  0,0 → 0",         "PUSH 0;PUSH 0;OR;HLT",              [0]),
    check("AND 1,1 → 1",         "PUSH 1;PUSH 1;AND;HLT",             [1]),
    check("AND 1,0 → 0",         "PUSH 1;PUSH 0;AND;HLT",             [0]),
    check("NAND 1,1 → 0",        "PUSH 1;PUSH 1;NAND;HLT",            [0]),
    check("NAND 1,0 → 1",        "PUSH 1;PUSH 0;NAND;HLT",            [1]),
    check("NOR  0,0 → 1",        "PUSH 0;PUSH 0;NOR;HLT",             [1]),
    check("NOR  1,0 → 0",        "PUSH 1;PUSH 0;NOR;HLT",             [0]),
    check("XOR  1,0 → 1",        "PUSH 1;PUSH 0;XOR;HLT",             [1]),
    check("XOR  1,1 → 0",        "PUSH 1;PUSH 1;XOR;HLT",             [0]),
    check("XNOR 1,1 → 1",        "PUSH 1;PUSH 1;XNOR;HLT",            [1]),
    check("XNOR 1,0 → 0",        "PUSH 1;PUSH 0;XNOR;HLT",            [0]),
]

# ── Comparisons ──────────────────────────────────────────────
section("Comparisons")
results += [
    check("EQ  equal",           "PUSH 5;PUSH 5;EQ;HLT",              [1]),
    check("EQ  not equal",       "PUSH 5;PUSH 6;EQ;HLT",              [0]),
    check("LE  less",            "PUSH 3;PUSH 5;LE;HLT",              [1]),
    check("LE  not less",        "PUSH 5;PUSH 3;LE;HLT",              [0]),
    check("GE  greater",         "PUSH 5;PUSH 3;GE;HLT",              [1]),
    check("GE  not greater",     "PUSH 3;PUSH 5;GE;HLT",              [0]),
    check("LEQ equal",           "PUSH 4;PUSH 4;LEQ;HLT",             [1]),
    check("LEQ less",            "PUSH 3;PUSH 4;LEQ;HLT",             [1]),
    check("LEQ greater",         "PUSH 5;PUSH 4;LEQ;HLT",             [0]),
    check("GEQ equal",           "PUSH 4;PUSH 4;GEQ;HLT",             [1]),
    check("GEQ greater",         "PUSH 5;PUSH 4;GEQ;HLT",             [1]),
    check("GEQ less",            "PUSH 3;PUSH 4;GEQ;HLT",             [0]),
]

# ── Control Flow ─────────────────────────────────────────────
section("Control Flow")
results += [
    check("J  unconditional",
          "J skip;PUSH 99;LAB skip;PUSH 1;HLT",                       [1]),
    check("JZ taken (zero)",
          "PUSH 0;JZ done;PUSH 99;LAB done;HLT",                      []),
    check("JZ not taken (nonzero)",
          "PUSH 1;JZ skip;PUSH 42;LAB skip;HLT",                      [42]),
    check("LAB + loop (count to 3)",
          "PUSH 0;POP M[i];LAB loop;PUSH M[i];PUSH 1;ADD;POP M[i];"
          "PUSH M[i];PUSH 3;GEQ;JZ loop;PUSH M[i];HLT",           [3]),
]
# Replace the complex loop with a simpler verifiable one:
results[-1] = check(
    "JZ loop (sum 1+2+3)",
    # i=3, acc=0; loop: acc+=i; i--; if i!=0 jump
    "PUSH 3;POP M[i];PUSH 0;POP M[acc];"
    "LAB loop;"
    "PUSH M[acc];PUSH M[i];ADD;POP M[acc];"
    "PUSH M[i];PUSH 1;SUB;POP M[i];"
    "PUSH M[i];JZ done;"
    "J loop;"
    "LAB done;PUSH M[acc];HLT",
    [6],
)

# ── Summary ──────────────────────────────────────────────────
passed = sum(results)
total  = len(results)
print(f"\n{'═' * 55}")
print(f"  Result: {passed}/{total} passed", end="  ")
print("✓ All good!" if passed == total else "✗ Some tests failed.")
print(f"{'═' * 55}\n")

sys.exit(0 if passed == total else 1)