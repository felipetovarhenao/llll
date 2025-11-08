# llll

Python support for lisp-like linked lists (_llll_).

## Installation

```bash
pip3 install llll
```

## Basic Usage

### Creating lllls

```python
from llll import llll

# Atomic values
x = llll(42)
y = llll("hello")

# Nested lists
z = llll(1, 2, [3, 4], 5)  # 1 2 [ 3 4 ] 5

# From Python objects
data = llll.from_python([1, [2, 3], 4]) # 1 [ 2 3 ] 4
```

### Indexing

llll uses 1-based indexing by convention:

```python
l = llll(10, 20, [30, 40], 50)

l[1]      # 10
l[-1]     # 50
l[3]      # 30 40
l[3, 2]   # 40 (address-based access)

# Slicing (1-based, inclusive)
l[2:3]    # 20 [ 30 40 ]
```

### Arithmetic Operations

Element-wise operations with broadcasting:

```python
l = llll(1, 2, 3)

l + 10              # 11 12 13
l * llll(2, 3, 4)   # 2 6 12
l / 2               # 1/2 1 3/2 (returns Fractions for int division)

# Nested operations
nested = llll([1, 2], [3, 4])
nested + 10      # [ 11 12 ] [ 13 14 ]
```

### Mapping

Apply functions at specific depths:

```python
l = llll(1, [2, 3], [[4, 5], 6])

# Boolean comparison
l.map(lambda x, addr: int(x > 2))
# 0 [ 0 1 ] [ [ 1 1 ] 1 ]

# Apply only at depth 2
l.map(lambda x, addr: x * 10,
      mindepth=2,
      maxdepth=2)
# 1 [ 20 30 ] [ [ 4 5 ] 60 ]
```

The mapping function receives both the value and its address (tuple of indices).

### File I/O

```python
# Save to file
l = llll(1, 2, [3, 4])
l.write("data.txt")      # Human-readable format
l.write("data.llll")     # Native llll format

# Load from file
from_txt = llll.read("data.txt")
from_llll = llll.read("data.llll")
```

### Utility Methods

```python
l = llll(1, [2, 3])

l.is_atomic()     # False
l.depth()         # 2
l.to_python()     # [1, [2, 3]]

l.append([4, 5])  # 1 [ 2 3 ] [ 4 5 ]
```

## Key Features

- **1-based indexing** following Max/MSP bach library conventions
- **Element-wise arithmetic** with automatic broadcasting
- **Flexible mapping** with depth control
- **Address-based access** using tuple notation
- **Fraction support** for exact rational arithmetic
- **File persistence** in both text and binary formats

## License

MIT License - Copyright (c) 2025 Felipe Tovar-Henao
