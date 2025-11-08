import os
import json
import struct
import re
from fractions import Fraction


class llll:
    """Python representation of a lisp-like linked list."""

    def __init__(self, *items):
        self._items = []
        for item in items:
            self._items.append(self._to_llll(item))

    def __eq__(self, other):
        if not isinstance(other, llll):
            other = llll(other)

        if self.is_atomic() and other.is_atomic():
            return self._value == other._value

        if self.is_atomic() or other.is_atomic():
            return False

        if len(self._items) != len(other._items):
            return False

        return all(a == b for a, b in zip(self._items, other._items))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, llll):
            other = llll(other)

        if self.is_atomic() and other.is_atomic():
            return self._value < other._value

        if self.is_atomic() or other.is_atomic():
            return False

        if len(self._items) != len(other._items):
            return False

        return all(a < b for a, b in zip(self._items, other._items))

    def __le__(self, other):
        if not isinstance(other, llll):
            other = llll(other)

        if self.is_atomic() and other.is_atomic():
            return self._value <= other._value

        if self.is_atomic() or other.is_atomic():
            return False

        if len(self._items) != len(other._items):
            return False

        return all(a <= b for a, b in zip(self._items, other._items))

    def __gt__(self, other):
        if not isinstance(other, llll):
            other = llll(other)

        if self.is_atomic() and other.is_atomic():
            return self._value > other._value

        if self.is_atomic() or other.is_atomic():
            return False

        if len(self._items) != len(other._items):
            return False

        return all(a > b for a, b in zip(self._items, other._items))

    def __ge__(self, other):
        if not isinstance(other, llll):
            other = llll(other)

        if self.is_atomic() and other.is_atomic():
            return self._value >= other._value

        if self.is_atomic() or other.is_atomic():
            return False

        if len(self._items) != len(other._items):
            return False

        return all(a >= b for a, b in zip(self._items, other._items))

    def _arithmetic_op(self, other, op, op_name):
        if not isinstance(other, llll):
            other = llll(other)

        if self.is_atomic() and other.is_atomic():
            if op_name == 'truediv' and isinstance(self._value, int) and isinstance(other._value, int):
                result = Fraction(self._value, other._value)
            else:
                result = op(self._value, other._value)
            return llll(result)

        if self.is_atomic() and not other.is_atomic():
            if len(other._items) == 1 and other._items[0].is_atomic():
                return self._arithmetic_op(other._items[0], op, op_name)
            new_items = []
            for item in other._items:
                result = self._arithmetic_op(item, op, op_name)
                new_items.append(result)
            return llll(*new_items)

        if not self.is_atomic() and other.is_atomic():
            new_items = []
            for item in self._items:
                result = item._arithmetic_op(other, op, op_name)
                new_items.append(result)
            return llll(*new_items)

        if len(other._items) == 1 and other._items[0].is_atomic():
            return self._arithmetic_op(other._items[0], op, op_name)

        if len(self._items) == 1 and self._items[0].is_atomic():
            return self._items[0]._arithmetic_op(other, op, op_name)

        if len(self._items) != len(other._items):
            raise ValueError(
                f"Cannot perform element-wise operation on lllls of different lengths: {len(self._items)} vs {len(other._items)}")

        new_items = []
        for a, b in zip(self._items, other._items):
            result = a._arithmetic_op(b, op, op_name)
            new_items.append(result)
        return llll(*new_items)

    def __add__(self, other):
        return self._arithmetic_op(other, lambda a, b: a + b, 'add')

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self._arithmetic_op(other, lambda a, b: a - b, 'sub')

    def __rsub__(self, other):
        if not isinstance(other, llll):
            other = llll(other)
        return other.__sub__(self)

    def __mul__(self, other):
        return self._arithmetic_op(other, lambda a, b: a * b, 'mul')

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return self._arithmetic_op(other, lambda a, b: a / b, 'truediv')

    def __rtruediv__(self, other):
        if not isinstance(other, llll):
            other = llll(other)
        return other.__truediv__(self)

    def __pow__(self, other):
        return self._arithmetic_op(other, lambda a, b: a ** b, 'pow')

    def __rpow__(self, other):
        if not isinstance(other, llll):
            other = llll(other)
        return other.__pow__(self)

    def __mod__(self, other):
        return self._arithmetic_op(other, lambda a, b: a % b, 'mod')

    def __rmod__(self, other):
        if not isinstance(other, llll):
            other = llll(other)
        return other.__mod__(self)

    def __len__(self):
        if self.is_atomic():
            return 1
        return len(self._items)

    def __getitem__(self, key):
        if key == 0:
            return llll()

        if self.is_atomic():
            return self.value()

        if isinstance(key, str):
            for x in self.__iter__():
                if x[1][1] == key:
                    return x[1:]
            return llll()

        if isinstance(key, slice):
            start = key.start + 1 if key.start is not None else 1
            stop = key.stop if key.stop is not None else len(self._items) + 1
            step = key.step if key.step is not None else 1

            start_idx = start - \
                1 if start > 0 else (len(self._items) +
                                     start if start < 0 else 0)
            stop_idx = stop - \
                1 if stop > 0 else (len(self._items) +
                                    stop if stop < 0 else len(self._items))

            sliced_items = self._items[start_idx:stop_idx + 1:step]
            return llll(*[item.to_python() for item in sliced_items])

        if isinstance(key, (tuple, list)):
            return self._get_by_address(key)

        idx = key - 1 if key > 0 else key
        if idx < 0:
            idx = len(self._items) + idx

        if not (0 <= idx < len(self._items)):
            raise IndexError(f"Index {key} out of range")

        return self._items[idx]

    def _get_by_address(self, address):
        if not address:
            return self

        first, *rest = address
        element = self[first]

        if rest:
            return element._get_by_address(rest)
        return element

    def __setitem__(self, key, value):
        if self.is_atomic():
            raise IndexError("Cannot set items in atomic llll")

        if isinstance(key, (tuple, list)):
            if len(key) == 1:
                self[key[0]] = value
            else:
                self[key[0]]._set_by_address(key[1:], value)
            return

        idx = key - 1 if key > 0 else key
        if idx < 0:
            idx = len(self._items) + idx

        if not (0 <= idx < len(self._items)):
            raise IndexError(f"Index {key} out of range")

        self._items[idx] = self._to_llll(value)

    def __iter__(self):
        if self.is_atomic():
            return iter([])
        return iter(self._items)

    def __repr__(self):
        if self.is_atomic():
            return repr(self._value)

        items_repr = ' '.join(repr(item) for item in self._items)
        return f"[ {items_repr} ]"

    def __str__(self):
        return self._to_str(top_level=True, indent=-1, min_depth=2)

    def _set_by_address(self, address, value):
        if len(address) == 1:
            self[address[0]] = value
        else:
            self[address[0]]._set_by_address(address[1:], value)

    def _to_llll(self, item):
        if isinstance(item, llll):
            return item
        elif isinstance(item, (list, tuple)):
            return llll(*item)
        else:
            return llll.__new__(llll)._init_atomic(item)

    def wrap(self, n: int = 1):
        for _ in range(n):
            self._items = llll(self._items)
        return self

    def _init_atomic(self, value):
        self._items = None
        self._value = value
        return self

    def is_atomic(self):
        return self._items is None

    def value(self):
        if not self.is_atomic():
            raise ValueError("Cannot get value of non-atomic llll")
        return self._value

    def append(self, item):
        if self.is_atomic():
            raise ValueError("Cannot append to atomic llll")
        self._items.append(self._to_llll(item))

    def extend(self, items):
        if self.is_atomic():
            raise ValueError("Cannot extend atomic llll")
        for item in items:
            self.append(item)

    def depth(self):
        if self.__len__() == 0:
            return 0
        if self.is_atomic():
            return 1
        return 1 + max((item.depth() for item in self._items), default=0)

    def _to_str(self, top_level=False, indent=0, min_depth=2):
        if self.is_atomic():
            return str(self._value)

        if self.__len__() == 0:
            return 'null'

        use_indented = self.depth() >= min_depth

        if use_indented:
            indent_str = '  ' * indent
            next_indent = '  ' * (indent + 1)

            items_str = []
            for item in self._items:
                item_repr = item._to_str(
                    indent=indent + 1, min_depth=min_depth)
                items_str.append(f'\n{next_indent}{item_repr}')

            items_content = ''.join(items_str)

            if top_level:
                return items_content.lstrip()
            return f'[{items_content}\n{indent_str}]'
        else:
            items_str = ' '.join(item._to_str(min_depth=min_depth)
                                 for item in self._items)

            if top_level:
                return items_str
            return f'[ {items_str} ]'

    def to_python(self):
        if self.is_atomic():
            return self._value
        return [item.to_python() for item in self._items]

    @classmethod
    def from_python(cls, obj):
        if isinstance(obj, (list, tuple)):
            return cls(*obj)
        else:
            return cls(obj)

    def map(self, func, mindepth=1, maxdepth=float('inf'), _current_depth=1, _address=()):
        if self.is_atomic():
            if mindepth <= _current_depth <= maxdepth:
                result = func(self._value, _address)
                return llll(result)
            return llll(self._value)

        if len(self._items) == 0:
            return llll()

        new_items = []
        for idx, item in enumerate(self._items):
            current_address = _address + (idx + 1,)

            if item.is_atomic():
                if mindepth <= _current_depth <= maxdepth:
                    result = func(item._value, current_address)
                    new_items.append(result)
                else:
                    new_items.append(item._value)
            else:
                if _current_depth < maxdepth:
                    mapped_item = item.map(
                        func,
                        mindepth=mindepth,
                        maxdepth=maxdepth,
                        _current_depth=_current_depth + 1,
                        _address=current_address
                    )
                    new_items.append(mapped_item)
                else:
                    new_items.append(item)

        return llll(*new_items)

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
            Parser.serialize(self, file)


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
        return struct.unpack('<d', struct.pack('<II', low, high))[0]

    def _convert_from_float(self, value: float):
        low, high = struct.unpack('<II', struct.pack('<d', value))
        return low, high

    def serialize(cls, l: llll, file: str):
        data = []

        def traverse(x):
            for item in x:
                if item.is_atomic():
                    value = item.value()
                    if isinstance(value, float):
                        low, high = cls._convert_from_float(value)
                        data.extend(
                            ["_x_x_x_x_bach_float64_x_x_x_x_", low, high])
                    else:
                        data.append(value)
                else:
                    data.append('[')
                    traverse(item)
                    data.append(']')
        traverse(l)
        data_len = len(data)
        num_chunks = data_len // 4096 + 1
        chunk_size = 4096
        native_data = {}
        for i in range(num_chunks):
            st = i * chunk_size
            end = st + chunk_size
            key = f"data_{i:010}"
            native_data[key] = data[st:end]
        native_data['data_count'] = [num_chunks]
        with open(file, 'w') as f:
            json.dump(obj=native_data, fp=f)

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
                    elif isinstance(item, str):
                        pat = re.compile(pattern=r"[+-]?\d+/\d+")
                        match = pat.search(item)
                        if match:
                            rat = match[0].split('/')
                            item = Fraction(int(rat[0]), int(rat[1]))

                    l.append(item)

        return consume()
