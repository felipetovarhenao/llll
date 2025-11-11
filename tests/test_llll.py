from fractions import Fraction
from llll import llll


class TestCreation:
    """Test llll creation methods."""

    def test_atomic_integer(self):
        """Test creating atomic integer value."""
        x = llll(42)
        assert x[1] == 42

    def test_atomic_string(self):
        """Test creating atomic string value."""
        y = llll("hello")
        assert y[1] == "hello"

    def test_nested_lists(self):
        """Test creating nested lists: 1 2 [ 3 4 ] 5"""
        z = llll(1, 2, [3, 4], 5)
        assert z[1] == 1
        assert z[2] == 2
        assert z[3].to_python() == [3, 4]
        assert z[4] == 5

    def test_from_python(self):
        """Test creating llll from Python list."""
        data = llll.from_python([1, [2, 3], 4])
        assert data[1] == 1
        assert data[2].to_python() == [2, 3]
        assert data[3] == 4


class TestIndexing:
    """Test 1-based indexing and slicing."""

    def test_one_based_indexing(self):
        """Test that indexing starts at 1, not 0."""
        l = llll(10, 20, 30)
        assert l[1] == 10
        assert l[2] == 20
        assert l[3] == 30

    def test_negative_indexing(self):
        """Test negative indices count from end."""
        l = llll(10, 20, 30, 40)
        assert l[-1] == 40
        assert l[-2] == 30

    def test_nested_access(self):
        """Test accessing nested sublists."""
        l = llll(10, 20, [30, 40], 50)
        nested = l[3]
        assert nested.to_python() == [30, 40]
        assert nested[1] == 30
        assert nested[2] == 40

    def test_address_based_access(self):
        """Test address-based access with tuple notation."""
        l = llll(10, 20, [30, 40], 50)
        assert l[3, 1] == 30
        assert l[3, 2] == 40

    def test_slicing_inclusive(self):
        """Test 1-based inclusive slicing."""
        l = llll(10, 20, [30, 40], 50)
        sliced = l[2:3]
        assert sliced[1] == 20
        assert sliced[2].to_python() == [30, 40]

    def test_full_range_slice(self):
        """Test slicing entire range."""
        l = llll(10, 20, 30)
        sliced = l[1:3]
        assert sliced.to_python() == [10, 20, 30]


class TestArithmetic:
    """Test element-wise arithmetic operations."""

    def test_scalar_addition(self):
        """Test adding scalar to all elements."""
        l = llll(1, 2, 3)
        result = l + 10
        assert result.to_python() == [11, 12, 13]

    def test_elementwise_multiplication(self):
        """Test element-wise multiplication of two lllls."""
        l = llll(1, 2, 3)
        result = l * llll(2, 3, 4)
        assert result.to_python() == [2, 6, 12]

    def test_division_returns_fractions(self):
        """Test that integer division returns Fraction objects."""
        l = llll(1, 2, 3)
        result = l / 2
        assert result[1] == Fraction(1, 2)
        assert result[2] == Fraction(2, 2)
        assert result[3] == Fraction(3, 2)

    def test_nested_arithmetic(self):
        """Test arithmetic on nested structures."""
        nested = llll([1, 2], [3, 4])
        result = nested + 10
        assert result[1].to_python() == [11, 12]
        assert result[2].to_python() == [13, 14]

    def test_scalar_subtraction(self):
        """Test subtracting scalar from all elements."""
        l = llll(10, 20, 30)
        result = l - 5
        assert result.to_python() == [5, 15, 25]


class TestMapping:
    """Test mapping functions with depth control."""

    def test_map_boolean_comparison(self):
        """Test mapping with boolean comparison (x > 2)."""
        l = llll(1, [2, 3], [[4, 5], 6])
        result = l.map(func=lambda x, _: int(x > 2))
        assert result[1] == 0
        assert result[2].to_python() == [0, 1]
        assert result[3, 1].to_python() == [1, 1]
        assert result[3, 2] == 1

    def test_map_with_depth_constraint(self):
        """Test mapping only at specific depth (depth 2)."""
        l = llll(1, [2, 3], [[4, 5], 6])
        def func(x, _): return x * 10
        result = l.map(
            func=func,
            mindepth=2,
            maxdepth=2
        )
        assert result[1] == 1
        assert result[2].to_python() == [20, 30]
        assert result[3, 1].to_python() == [4, 5]
        assert result[3, 2] == 60

    def test_map_receives_address(self):
        """Test that mapping function receives address tuple."""
        l = llll(1, 2, 3)
        addresses = []
        l.map(lambda x, addr: addresses.append(addr) or x)
        assert len(addresses) == 3
        assert all(isinstance(addr, tuple) for addr in addresses)


class TestUtilities:
    """Test utility methods."""

    def test_is_atom_true(self):
        """Test _is_atom() returns True for single values."""
        atomic = llll(42)
        assert not atomic._is_atom()

    def test_is_atom_false(self):
        """Test _is_atom() returns False for lists."""
        nested = llll(1, [2, 3])
        assert not nested._is_atom()

    def test_depth_simple(self):
        """Test depth() on simple nested structure."""
        l = llll(1, [2, 3])
        assert l.depth() == 2

    def test_depth_deeply_nested(self):
        """Test depth() on deeply nested structure."""
        l = llll(1, [2, [3, [4]]])
        assert l.depth() == 4

    def test_to_python(self):
        """Test conversion to Python list."""
        l = llll(1, [2, 3])
        assert l.to_python() == [1, [2, 3]]

    def test_append(self):
        """Test appending elements."""
        l = llll(1, [2, 3])
        l.append([4, 5])
        assert l[-1].to_python() == [4, 5]
        assert len(l.to_python()) == 3

    def test_extend(self):
        """Test extending elements."""
        l = llll(1, [2, 3])
        l.extend([4, 5])
        assert l[-1] == 5
        assert len(l.to_python()) == 4

    def test_nested_append(self):
        """Test appending nested elements."""
        l = llll(1, [2, 3])
        l[2].append(4)
        assert l.to_python() == [1, [2, 3, 4]]
        assert len(l[2]) == 3

    def test_nested_append(self):
        """Test extending nested elements."""
        l = llll(1, [2, 3])
        l[2].extend([4, 5])
        assert l.to_python() == [1, [2, 3, 4, 5]]
        assert len(l[2]) == 4


class TestKeys:

    def test_key_access(self):
        l = llll(["name", "Alice"], ["age", 33], ["parents", "Bob", "Chloe"])

        assert l["name"] == 'Alice'
        assert l["age"] == 33
        assert l["parents"].to_python() == ['Bob', "Chloe"]

    def test_key_assign(self):
        l = llll(["name", "Alice"], ["age", 33], ["parents", "Bob", "Chloe"])
        l['name'] = "Ada"
        l['age'] = 40
        l['parents'] = ["Alice", "John"]
        assert l["name"] == 'Ada'
        assert l["age"] == 40
        assert l["parents"].to_python() == ['Alice', "John"]

    def test_mixed_access(self):
        l = llll(['foo', ['one', 2, 3], ['two', 5, 6]], [
                 'bar', ['one', 8, 9], ['two', 11, 12]])
        a = l['bar', 2, 3]
        b = l['bar', 'two', 2]
        assert a == b == 12
        assert l['foo', 'one'].to_python() == [2, 3]

    def test_mixed_assign(self):
        l = llll(['foo', ['one', 2, 3], ['two', 5, 6]], [
                 'bar', ['one', 8, 9], ['two', 11, 12]])
        l['foo', 1, 2] *= 10
        l['foo', 'two', 1] *= 100
        assert l['foo', 1, 2] == 20
        assert l['foo', 'two', 1] == 500


class TestFileIO:
    """Test file I/O operations."""

    def test_write_read_txt(self, tmp_path):
        """Test writing and reading text format."""
        filepath = str(tmp_path / "data.txt")
        a = llll(1, 2, [2.312, -11/7], ['foo', '12.234', 'tic toc'])
        a.write(filepath)
        b = llll.read(filepath)
        assert a == b

    def test_write_read_native_format(self, tmp_path):
        """Test writing and reading native .llll format."""
        a = llll(1, 2, [2.312, -11/7], ['foo', '12.234', 'tic toc'])
        filepath = str(tmp_path / "data.llll")
        a.write(filepath)
        b = llll.read(filepath)
        assert a == b

    def test_roundtrip_complex_structure(self, tmp_path):
        """Test roundtrip with complex nested structure."""
        a = llll(1, [2, [-3, '"hello"']], [['foo', 5], 6], 7.24, [
                 Fraction(-40, 23)], 33/23, 'hi there')
        filepath = str(tmp_path / "complex.llll")
        a.write(filepath)
        b = llll.read(filepath)
        assert a == b


class TestNull:
    """Test expected bahavior with null values"""

    def test_null_lllls(self):
        x = llll()
        assert x.to_python() == []
        assert len(x) == 0
        for _ in range(4):
            x.append(llll())
        assert x.to_python() == []
        assert len(x) == 0
        for _ in range(4):
            x.extend(llll())
        assert x.to_python() == []
        assert len(x) == 0
        x = llll()
        for _ in range(4):
            x.append(llll().wrap(1))
        assert x.to_python() == [[[]], [[]], [[]], [[]]]
        assert len(x) == 4


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_nested_list(self):
        """Test handling of empty nested lists."""
        l = llll(1, [], 2)
        assert l[2].to_python() == []

    def test_single_element(self):
        """Test llll with single element."""
        l = llll(42)
        assert l[1] == 42
        assert l.to_python() == [42]

    def test_deeply_nested_access(self):
        """Test accessing deeply nested elements."""
        l = llll([[[1, 2]]])
        assert l[1, 1, 1, 1] == 1
        assert l[1, 1, 1, 2] == 2
