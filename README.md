# Abstract Stack Machine - CSC153

A simple stack-based virtual machine simulator that executes assembly-like instructions.

## Overview

This project implements an abstract machine with a stack, memory, and support for arithmetic, logical, comparison, and control flow operations. Programs are written in a custom assembly language with semicolon-separated instructions.

## Features

- **Stack-based architecture** with push/pop operations
- **Memory access** via named variables (e.g., `M[x]`)
- **Arithmetic operations**: ADD, SUB, MUL, DIV
- **Logical operations**: NOT, OR, AND, NAND, NOR, XOR, XNOR
- **Comparisons**: EQ, LE, GE, LEQ, GEQ
- **Control flow**: Labels (LAB), unconditional jump (J), conditional jump (JZ)
- **Debug mode** to trace execution step-by-step

## Installation

No external dependencies required. Just Python 3.8+.

```bash
git clone <repository-url>
cd Activity_1_Abstract_Machine_Simulation_in_Python
chmod +x abstract_machine.py
```

## Usage

### Basic Execution

```bash
echo "PUSH 5; PUSH 3; ADD; HLT" | ./abstract_machine.py
```

### Debug Mode

```bash
echo "PUSH 5; PUSH 3; ADD; HLT" | ./abstract_machine.py --debug
```

### Interactive Mode

```bash
./abstract_machine.py
# Enter your program (one line, semicolon-separated)
PUSH 10; PUSH 2; MUL; HLT
```

## Instruction Set

### Stack Operations
- `PUSH n` - Push literal integer n onto stack
- `PUSH M[x]` - Push value from memory address x
- `POP M[x]` - Pop stack top into memory address x

### Arithmetic
- `ADD` - Pop two values, push their sum
- `SUB` - Pop two values, push their difference
- `MUL` - Pop two values, push their product
- `DIV` - Pop two values, push integer division result

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

### Factorial of 5

```
PUSH 5; POP M[n]; PUSH 1; POP M[result]; LAB loop; PUSH M[n]; PUSH 1; LE; JZ continue; J end; LAB continue; PUSH M[result]; PUSH M[n]; MUL; POP M[result]; PUSH M[n]; PUSH 1; SUB; POP M[n]; J loop; LAB end; HLT
```

**Output:** `memory={'n': 1, 'result': 120}`

### Sum 1+2+3

```
PUSH 3; POP M[i]; PUSH 0; POP M[acc]; LAB loop; PUSH M[acc]; PUSH M[i]; ADD; POP M[acc]; PUSH M[i]; PUSH 1; SUB; POP M[i]; PUSH M[i]; JZ done; J loop; LAB done; PUSH M[acc]; HLT
```

**Output:** `stack=[6]`

### Count to 3

```
PUSH 0; POP M[i]; LAB loop; PUSH M[i]; PUSH 1; ADD; POP M[i]; PUSH M[i]; PUSH 3; GE; JZ loop; PUSH M[i]; HLT
```

**Output:** `stack=[3]`

## Testing

Run the test suite:

```bash
python test_machine.py
```

## Project Structure

```
.
├── abstract_machine.py   # Main VM implementation
├── instructions.py       # Instruction definitions
├── test_machine.py       # Test suite
└── README.md            # This file
```

## Implementation Details

- **Stack**: Python list storing integers
- **Memory**: Dictionary mapping variable names to integers
- **Labels**: Dictionary mapping label names to instruction indices
- **Instruction Pointer**: Tracks current execution position

## Course Information

**Course:** CSC153 - Assemblers, Interpreters, and Compilers  
**Activity:** Activity 1 - Abstract Machine Simulation in Python  
**Academic Year:** 4th Year, 2nd Semester

## License

Educational project for CSC153 coursework.