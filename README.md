# Abstract Stack Machine - CSC153

A simple stack-based virtual machine simulator that executes assembly-like instructions.

## Overview

This project implements an abstract machine with a stack, memory, and support for arithmetic, logical, comparison, and control flow operations. Programs are written in a custom assembly language with semicolon-separated instructions.

The machine maintains three components:
- **Stack**: A list of integers for computation
- **Memory**: A dictionary mapping variable names to integer values
- **Instruction Pointer**: Tracks the current execution position

## Features

- **Stack-based architecture** with push/pop operations
- **Memory access** via named variables (e.g., `M[x]`, `M[result]`)
- **Arithmetic operations**: ADD, SUB, MUL, DIV
- **Logical operations**: NOT, OR, AND, NAND, NOR, XOR, XNOR
- **Comparisons**: EQ, LE, GE, LEQ, GEQ
- **Control flow**: Labels (LAB), unconditional jump (J), conditional jump (JZ)
- **Execution tracing** with detailed IP, instruction, stack, and memory logging

## Installation

No external dependencies required. Python 3.8+ only.

```bash
git clone <repository-url>
cd Abstract-Machine-CSC153
```

## Quick Start

```bash
# Run the test suite to verify everything works
python3 test_machine.py

# Or use the machine programmatically
python3
>>> from abstract_machine import asm_parser, run, initial_state
>>> code = asm_parser("PUSH 5; PUSH 3; ADD; HLT")
>>> state = initial_state(code)
>>> final_state = run(state)
>>> _, stack, memory = final_state
>>> print(stack)
[8]
```

## Usage

### Running Programs from Python

```python
from abstract_machine import asm_parser, run, initial_state

# Parse assembly code
code = asm_parser("PUSH 5; PUSH 3; ADD; HLT")

# Create initial state
state = initial_state(code)

# Run the machine
final_state = run(state)

# Extract results
code, stack, memory = final_state
print(f"Stack: {stack}")      # [8]
print(f"Memory: {memory}")    # {}
```

### Running .asm Files

Create a file with your assembly code (e.g., `program.asm`):

```asm
PUSH 10; PUSH 20; ADD; HLT
```

Then test it using the test suite (automatically includes all .asm files).

## Instruction Set

### Stack Operations
- `PUSH n` - Push literal integer n onto stack
- `PUSH M[x]` - Push value from memory address x
- `POP M[x]` - Pop stack top into memory address x

### Arithmetic
- `ADD` - Pop two values, push their sum
- `SUB` - Pop two values, push their difference (first - second)
- `MUL` - Pop two values, push their product
- `DIV` - Pop two values, push integer division result (division by zero returns 0)

### Logical Operations
- `NOT` - Pop one value, push logical NOT (0→1, nonzero→0)
- `OR`, `AND`, `NAND`, `NOR`, `XOR`, `XNOR` - Binary logical operations

### Comparisons
- `EQ` - Equal (==)
- `LE` - Less than (<)
- `GE` - Greater than (>)
- `LEQ` - Less than or equal (≤)
- `GEQ` - Greater than or equal (≥)

### Control Flow
- `LAB label` - Define a label
- `J label` - Unconditional jump to label
- `JZ label` - Jump to label if stack top is zero
- `HLT` - Halt execution

## Examples

### Example 1: Factorial of 5 (factorial.asm)

```asm
PUSH 5; POP M[n]; PUSH 1; POP M[result]; LAB loop; PUSH M[n]; PUSH 1; LE; JZ continue; J end; LAB continue; PUSH M[result]; PUSH M[n]; MUL; POP M[result]; PUSH M[n]; PUSH 1; SUB; POP M[n]; J loop; LAB end; HLT
```

**Result:**
- Stack: `[]`
- Memory: `{'n': 0, 'result': 120}`

### Example 2: While Loop (while_loop.asm)

```asm
push 0; pop M[x]; lab 1; push M[x]; push 1; leq; jz 2; push M[x]; push 1; add; pop M[x]; j 1; lab 2; hlt
```

**Result:**
- Stack: `[]`
- Memory: `{'x': 2}`

### Example 3: Sum 1+2+3

```asm
PUSH 3; POP M[i]; PUSH 0; POP M[acc]; LAB loop; PUSH M[acc]; PUSH M[i]; ADD; POP M[acc]; PUSH M[i]; PUSH 1; SUB; POP M[i]; PUSH M[i]; JZ done; J loop; LAB done; PUSH M[acc]; HLT
```

**Result:**
- Stack: `[6]`
- Memory: `{'i': 0, 'acc': 6}`

### Example 4: Simple Arithmetic

```asm
PUSH 10; PUSH 20; ADD; HLT
```

**Result:**
- Stack: `[30]`
- Memory: `{}`

## Testing

Run the comprehensive test suite:

```bash
python3 test_machine.py
```

The test suite includes:
- **40 unit tests** covering all instruction types
  - Stack I/O (4 tests)
  - Arithmetic operations (6 tests)
  - Boolean/Bitwise operations (14 tests)
  - Comparison operations (12 tests)
  - Control flow and loops (4 tests)
- **Automatic .asm file testing** - any `.asm` file in the directory is automatically tested
- **Table-formatted output** showing Status, Test Name, Assembly Code, Stack, and Memory
- **Color-coded results** (PASS/FAIL) for easy visual inspection

**All tests verify both final stack state AND memory state** for comprehensive validation.

### Test Output Format

```
──────────────────────────────────────────────────────────────────────
  Stack I/O
──────────────────────────────────────────────────────────────────────
  Status│ Test Name                     │ Assembly Code                         
  PASS  │ PUSH literal                  │ PUSH 7;HLT                            │ [7]                      │ {}
  PASS  │ PUSH multiple                 │ PUSH 1;PUSH 2;PUSH 3;HLT              │ [1, 2, 3]                │ {}
  PASS  │ POP to memory                 │ PUSH 42;POP M[a];HLT                  │ []                       │ {'a': 42}
```

### Adding Custom Tests

Simply create a `.asm` file in the project directory and run the test suite. The file will be automatically discovered and executed.

For expected output validation, add your file to the `asm_expected_outputs` dictionary in `test_machine.py`:

```python
asm_expected_outputs = {
    'your_program.asm': ([expected_stack], {'expected': 'memory'}),
}
```

## Project Structure

```
.
├── abstract_machine.py   # Main VM implementation (parser, executor, state management)
├── instructions.py       # Instruction implementations (push, pop, add, etc.)
├── test_machine.py       # Comprehensive test suite with 42+ tests
├── factorial.asm         # Example: factorial calculation
├── while_loop.asm        # Example: while loop demonstration
├── asm_test.png          # Test output screenshot
└── README.md            # This file
```

## Implementation Details

### Architecture

The abstract machine uses a **State-based execution model**:

```python
State = Tuple[List[Instruction], List[int], Dict[str, int]]
# State = (code, stack, memory)
```

### Execution Flow

1. **Parse**: `asm_parser(code_string)` → List of instruction tuples
2. **Initialize**: `initial_state(parsed_code)` → (code, [], {})
3. **Execute**: `run(state)` → final_state
4. **Extract**: Unpack stack and memory from final state

### Data Structures

- **Stack**: Python `list` storing integers (LIFO)
- **Memory**: Python `dict` mapping variable names (strings) to integers
- **Labels**: Dictionary mapping label names to instruction indices (built during first pass)
- **Instruction Pointer (IP)**: Integer tracking current execution position

### Instruction Format

Instructions are parsed into tuples:
- `(fn, None)` - No-operand instruction (e.g., ADD, HLT)
- `(fn, int)` - Literal integer operand (e.g., PUSH 5)
- `(fn, str | int)` - Label operand (e.g., J loop or J 1)
- `(fn, 'M', str)` - Memory address operand (e.g., PUSH M[x])

### Execution Tracing

During execution, the machine prints:
```
ip=0 instr=(<function push>, 7) | stack=[] | memory={}
ip=1 instr=(<function halt>, None) | stack=[7] | memory={}
```

This allows full visibility into the execution process for debugging.

### Special Behaviors

- **Division by zero**: Returns 0 instead of raising an error
- **Case insensitive**: Instructions can be written in any case (PUSH, push, Push all work)
- **Flexible labels**: Labels can be numbers or descriptive names (LAB 1, LAB loop)
- **Memory initialization**: Variables are created on first write (POP M[x])
- **Error handling**: Detailed error messages for invalid instructions or syntax

## Course Information

**Course:** CSC153 - Assemblers, Interpreters, and Compilers  
**Activity:** Activity 1 - Abstract Machine Simulation in Python  
**Academic Year:** 4th Year, 2nd Semester

## License

Educational project for CSC153 coursework.