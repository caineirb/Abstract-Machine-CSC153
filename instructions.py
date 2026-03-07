from typing import List, Optional, Dict

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