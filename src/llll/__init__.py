import os
import json
import struct


class llll:
    """lisp-like linked list."""

    def __init__(self, *items):
        """Initialize llll with variable number of items.

        Args:
            *items: Elements to store. Can be primitives, lllls, or nested iterables.
        """
        self._items = []
        for item in items:
            self._items.append(self._wrap(item))

    def _wrap(self, item):
        """Wrap item as llll if not already one."""
        if isinstance(item, llll):
            return item
        elif isinstance(item, (list, tuple)):
            return llll(*item)
        else:
            # Atomic elements are wrapped in llll
            return llll.__new__(llll)._init_atomic(item)

    def wrap(self, n: int = 1):
        for _ in range(n):
            self._items = llll(self._items)
        return self

    def _init_atomic(self, value):
        """Internal method to create atomic llll."""
        self._items = None
        self._value = value
        return self

    def is_atomic(self):
        """Check if this llll is atomic (contains a primitive value)."""
        return self._items is None

    def value(self):
        """Get the atomic value. Raises ValueError if not atomic."""
        if not self.is_atomic():
            raise ValueError("Cannot get value of non-atomic llll")
        return self._value

    def __len__(self):
        """Return number of elements."""
        if self.is_atomic():
            return 1
        return len(self._items)

    def __getitem__(self, key):
        """Access elements by index (1-based), address, or slice.

        Args:
            key: int for single index, tuple/list for address path, or slice for range

        Returns:
            llll at the specified location, or new llll containing slice results
        """
        if key == 0:
            return

        if self.is_atomic():
            return self.value()

        if isinstance(key, str):
            for x in self.__iter__():
                if x[1][1] == key:
                    return x[1:]
            return None

        # Handle slice notation
        if isinstance(key, slice):
            start = key.start + 1 if key.start is not None else 1
            stop = key.stop if key.stop is not None else len(self._items) + 1
            step = key.step if key.step is not None else 1

            # Convert to 0-based indices
            start_idx = start - \
                1 if start > 0 else (len(self._items) +
                                     start if start < 0 else 0)
            stop_idx = stop - \
                1 if stop > 0 else (len(self._items) +
                                    stop if stop < 0 else len(self._items))

            # Get slice and return as new llll
            sliced_items = self._items[start_idx:stop_idx + 1:step]
            return llll(*[item.to_python() for item in sliced_items])

        if isinstance(key, (tuple, list)):
            # Address-based access
            return self._get_by_address(key)

        # Single index access (1-based)
        idx = key - 1 if key > 0 else key
        if idx < 0:
            idx = len(self._items) + idx

        if not (0 <= idx < len(self._items)):
            raise IndexError(f"Index {key} out of range")

        return self._items[idx]

    def _get_by_address(self, address):
        """Access element by address path."""
        if not address:
            return self

        first, *rest = address
        element = self[first]

        if rest:
            return element._get_by_address(rest)
        return element

    def __setitem__(self, key, value):
        """Set element at index (1-based) or address."""
        if self.is_atomic():
            raise IndexError("Cannot set items in atomic llll")

        if isinstance(key, (tuple, list)):
            # Address-based setting
            if len(key) == 1:
                self[key[0]] = value
            else:
                self[key[0]]._set_by_address(key[1:], value)
            return

        # Single index setting (1-based)
        idx = key - 1 if key > 0 else key
        if idx < 0:
            idx = len(self._items) + idx

        if not (0 <= idx < len(self._items)):
            raise IndexError(f"Index {key} out of range")

        self._items[idx] = self._wrap(value)

    def _set_by_address(self, address, value):
        """Set element by address path."""
        if len(address) == 1:
            self[address[0]] = value
        else:
            self[address[0]]._set_by_address(address[1:], value)

    def append(self, item):
        """Append item to the list."""
        if self.is_atomic():
            raise ValueError("Cannot append to atomic llll")
        self._items.append(self._wrap(item))

    def extend(self, items):
        """Extend list with multiple items."""
        if self.is_atomic():
            raise ValueError("Cannot extend atomic llll")
        for item in items:
            self.append(item)

    def __iter__(self):
        """Iterate over elements."""
        if self.is_atomic():
            return iter([])
        return iter(self._items)

    def __repr__(self):
        """String representation."""
        if self.is_atomic():
            return repr(self._value)

        items_repr = ' '.join(repr(item) for item in self._items)
        return f"[ {items_repr} ]"

    def depth(self):
        """Compute the maximum depth of nested lllls."""
        if self.is_atomic():
            return 0
        if not self._items:
            return 1
        return 1 + max((item.depth() for item in self._items), default=0)

    def __str__(self):
        """User-friendly string representation."""
        return self._to_str(top_level=True, indent=-1, min_depth=2)

    def _to_str(self, top_level=False, indent=0, min_depth=2):
        """Internal string conversion with top-level handling.

        Args:
            top_level: Whether this is the top-level call
            indent: Current indentation level
            min_depth: Minimum depth required to use indented formatting (default: 2)
        """
        if self.is_atomic():
            return str(self._value)

        # Check if we should use indented format
        use_indented = self.depth() >= min_depth

        if use_indented:
            # Build indented representation
            indent_str = '  ' * indent
            next_indent = '  ' * (indent + 1)

            items_str = []
            for item in self._items:
                item_repr = item._to_str(
                    indent=indent + 1, min_depth=min_depth)
                items_str.append(f'\n{next_indent}{item_repr}')

            items_content = ''.join(items_str)

            # Top level doesn't need brackets
            if top_level:
                return items_content.lstrip()
            return f'[{items_content}\n{indent_str}]'
        else:
            # Use compact single-line format
            items_str = ' '.join(item._to_str(min_depth=min_depth)
                                 for item in self._items)

            if top_level:
                return items_str
            return f'[ {items_str} ]'

    def to_python(self):
        """Convert to native Python list/value structure."""
        if self.is_atomic():
            return self._value
        return [item.to_python() for item in self._items]

    @classmethod
    def from_python(cls, obj):
        """Create llll from Python list/value structure."""
        if isinstance(obj, (list, tuple)):
            return cls(*obj)
        else:
            return cls(obj)

    @classmethod
    def from_file(cls, file: str):
        p = Parser(file=file)
        return p._data

    def to_file(self, file: str):
        ext = os.path.splitext(file)[1]
        if ext not in ['.txt', '.llll']:
            raise ValueError(f'Invalid extension: {ext}')
        if ext == '.txt':
            with open(file, 'w') as f:
                f.write(self.__str__())
        else:
            raise SystemError('.llll files are not yet supported.')


class Parser:
    def __init__(self, file: str):

        ext = os.path.splitext(file)[1]
        if ext not in ['.txt', '.llll']:
            raise ImportError(
                f'Invalid extension: {ext}\nFile must be .txt or .llll')
        with open(file, 'r') as f:
            data = f.read()

        if ext == '.llll':
            self._data = self._parse_native(data)
        else:
            raise TypeError('.txt not supported yet.')

    def _convert_to_float(self, low: int, high: int):
        """
        Converts two 32-bit integers into a single double-precision (64-bit) floating-point value.

        Parameters:
            low (int): Lower 32 bits of the encoded float.
            high (int): Higher 32 bits of the encoded float.

        Returns:
            float: The decoded floating-point number.
        """
        return struct.unpack('<d', struct.pack('<II', low, high))[0]

    def _convert_from_float(self, value: float):
        """
        Converts a single double-precision (64-bit) floating-point value into two 32-bit integers.

        Parameters:
            value (float): The floating-point number to encode.

        Returns:
            tuple: A tuple (low, high) where low is the lower 32 bits and high is the higher 32 bits.
        """
        low, high = struct.unpack('<II', struct.pack('<d', value))
        return low, high

    def _parse_native(self, data: str):

        obj = json.loads(s=data)
        data_count = obj['data_count'][0]
        items = []
        for i in range(data_count):
            items.extend(obj[f"data_{i:010}"])

        items = iter(items)

        def consume() -> llll:
            l = llll()
            while True:
                item = next(items, None)
                if item in [None, ']']:
                    return l
                elif item == '[':
                    l.append(consume())
                else:
                    if item == "_x_x_x_x_bach_float64_x_x_x_x_":
                        low, high = (next(items) for _ in range(2))
                        item = self._convert_to_float(low=low, high=high)
                    l.append(item)

        return consume()


if __name__ == '__main__':
    l = llll.from_file(
        '/Users/felipetovarhenao/Documents/llll_files/nums.llll')
    print(l)
