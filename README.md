# llll

A simple Python implementation of lisp-like linked lists.

## Features

- **Nested list structures** with intuitive syntax
- **Element-wise arithmetic** with automatic broadcasting
- **1-based indexing** for mathematical convenience
- **Powerful mapping** with depth control
- **Fraction support** for exact rational arithmetic
- **File I/O** for persistence

## Installation

```bash
pip3 install llll
```

Or install from source:

```bash
git clone https://github.com/yourusername/llll.git
cd llll
pip3 install -e .
```

## Quick Start

```python
from llll import llll

# Create nested structures
data = llll(1, 2, [3, 4], [[5, 6]])
print(data)
# 1 2 [ 3 4 ] [ [ 5 6 ] ]

# Element-wise arithmetic
a = llll(1, 2, 3)
b = llll(10, 20, 30)
print(a + b)        # 11 22 33
print(a * 2)        # 2 4 6

# Nested indexing (1-based)
nested = llll(1, [2, 3, [4, 5]], 6)
print(nested[2])       # 2 3 [ 4 5 ]
print(nested[2, 3])    # 4 5
print(nested[2, 3, 1]) # 4

# Map operations
result = llll(1, [2, 3], 4).map(lambda x, addr: x ** 2)
print(result)  # 1 [ 4 9 ] 16
```

## Usage Guide

### Creating lllls

```python
# Empty llll (null)
null = llll()

# Single values (atomic)
num = llll(42)
symbol = llll("hello")

# Lists
flat_list = llll(1, 2, 3, 4)

# Nested structures
nested = llll(1, [2, 3], [[4, 5], 6])

# From Python lists
from_list = llll.from_python([1, [2, 3], 4]) # 1 [2 3] 4
```

### Indexing and Slicing

**Note: llll uses 1-based indexing** (index 0 returns an null llll)

```python
l = llll(10, 20, 30, 40)

# Access elements (1-based)
l[1]     # 10
l[2]     # 20
l[-1]    # 40 (last element)

# Nested access with tuples
l = llll(1, [2, [3, 4]], 5)
l[2]        # 2 [ 3 4 ]
l[2, 2]     # 3 4
l[2, 2, 1]  # 3

# Slicing (1-based, left-exclusive)
l = llll(1, 2, 3, 4, 5)
l[2:4]      # [ 3 4 ]
l[1:3]      # [ 2 3 ]

# Key-based lookup
data = llll(["name", "Alice"], ["age", 30], ["city", "NYC"])
data["name"]  # "Alice"
data["age"]  # 30
data["city"]  # "NYC"
```

### Modification

```python
l = llll(1, 2, 3)

# Set elements
l[1] = 10
l[2] = [20, 21]

# Nested modification
l = llll(1, [2, 3], 4)
l[2, 1] = 99  # Modifies nested element

# Append and extend
l.append(5)
l.extend([6, 7, 8])
```

### Arithmetic Operations

Element-wise operations with automatic broadcasting:

```python
# Basic arithmetic
llll(1, 2, 3) + llll(10, 20, 30)    # [ 11 22 33 ]
llll(2, 4, 6) - llll(1, 1, 1)       # [ 1 3 5 ]
llll(2, 3, 4) * 5                   # [ 10 15 20 ]
llll(10, 20, 30) / 2                # [ 5 10 15 ]

# Power and modulo
llll(2, 3, 4) ** 2                  # [ 4 9 16 ]
llll(10, 20, 30) % 7                # [ 3 6 2 ]

# Broadcasting with nested structures
llll(1, 2, 3) + llll([10])          # [ 11 12 13 ]
llll([1, 2], [3, 4]) * 2            # [ [ 2 4 ] [ 6 8 ] ]

# Integer division uses Fraction for precision
llll(1, 2) / llll(3, 5)             # [ 1/3 2/5 ]
```

### Mapping with Depth Control

```python
l = llll(1, [2, 3], [[4, 5]])

# Map at specific depth
l.map(lambda x, addr: x * 10, mindepth=2, maxdepth=2)
# [ 1 [ 20 30 ] [ [ 4 5 ] ] ]

# Map at all depths
l.map(lambda x, addr: x + 100)
# [ 101 [ 102 103 ] [ [ 104 105 ] ] ]

# Use address information
l.map(lambda x, addr: f"{x}@{addr}")
# [ "1@(1,)" [ "2@(2,1)" "3@(2,2)" ] [ [ "4@(3,1,1)" "5@(3,1,2)" ] ] ]

# Apply conditional logic
l.map(lambda x, addr: x * 2 if x % 2 == 0 else x)
```

### Type Checking and Conversion

```python
# Check if atomic (single value)
llll(42).is_atomic()        # True
llll(1, 2, 3).is_atomic()   # False

# Get atomic value
llll(42).value()            # 42

# Get depth
llll(1, 2, 3).depth()                # 1
llll(1, [2, [3, 4]]).depth()         # 3

# Convert to Python types
l = llll(1, [2, 3], 4)
l.to_python()  # [1, [2, 3], 4]

# Length
len(llll(1, 2, 3))  # 3
len(llll())         # 0
```

### Comparisons

```python
# Equality
llll(1, 2, 3) == llll(1, 2, 3)  # True
llll(1, 2) == llll(1, 3)        # False

# Atomic comparisons
llll(5) < llll(10)              # True
llll(10) >= llll(10)            # True

# Element-wise comparisons (all elements must satisfy)
llll(1, 2, 3) < llll(2, 3, 4)   # True
llll(1, 5, 3) < llll(2, 3, 4)   # False
```

### File I/O

```python
# Save to text file
data = llll(1, [2, 3], [[4, 5]])
data.to_file("data.txt")

# Load from native .llll format
loaded = llll.from_file("data.llll")
```

## Advanced Examples

### Data Processing Pipeline

```python
# Process nested numerical data
data = llll(
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
)

# Normalize each sublist
normalized = data.map(
    lambda x, addr: x / 10,
    mindepth=2,
    maxdepth=2
)

# Apply transformations
result = (data * 2 + 10) / 5
```

### Structured Data

```python
# Key-value pairs
person = llll(
    ["name", "Alice"],
    ["age", 30],
    ["scores", [85, 90, 78]]
)

# Access by key
name = person["name"]           # [ "name" "Alice" ]
scores = person["scores"][2:]   # [ [ 85 90 78 ] ]

# Modify nested data
person["scores"][2, 1] = 95
```

### Mathematical Operations

```python
# Vector operations
v1 = llll(1, 2, 3)
v2 = llll(4, 5, 6)

dot_components = v1 * v2        # [ 4 10 18 ]
magnitude_sq = (v1 ** 2).to_python()  # [1, 4, 9]

# Matrix-like operations
matrix = llll(
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
)

scaled = matrix * 2
transposed_op = matrix.map(lambda x, addr: x + addr[1], mindepth=2)
```

## API Reference

### Core Methods

- `llll(*items)` - Constructor
- `is_atomic()` - Check if contains single value
- `value()` - Get atomic value
- `depth()` - Get maximum nesting depth
- `append(item)` - Add element
- `extend(items)` - Add multiple elements
- `map(func, mindepth=1, maxdepth=inf)` - Apply function to elements

### Conversion

- `to_python()` - Convert to native Python list
- `from_python(obj)` - Create from Python list
- `to_file(path)` - Save to file
- `from_file(path)` - Load from file

### Operators

Supports: `+`, `-`, `*`, `/`, `**`, `%`, `==`, `!=`, `<`, `<=`, `>`, `>=`

## License

MIT License

## Contributing

Contributions welcome! Please submit issues and pull requests on GitHub.

## Links

- Documentation: https://llll.readthedocs.io
- Repository: https://github.com/yourusername/llll
- PyPI: https://pypi.org/project/llll
