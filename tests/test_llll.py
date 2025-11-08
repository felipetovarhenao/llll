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
        result = l.map(lambda x, addr: int(x > 2))
        assert result[1] == 0
        assert result[2].to_python() == [0, 1]
        assert result[3, 1].to_python() == [1, 1]
        assert result[3, 2] == 1

    def test_map_with_depth_constraint(self):
        """Test mapping only at specific depth (depth 2)."""
        l = llll(1, [2, 3], [[4, 5], 6])
        result = l.map(
            lambda x, addr: x * 10,
            mindepth=2,
            maxdepth=2
        )
        assert result[1] == 1  # depth 1, unchanged
        assert result[2].to_python() == [20, 30]  # depth 2, multiplied
        assert result[3, 1].to_python() == [4, 5]  # depth 3, unchanged
        assert result[3, 2] == 60  # depth 2, multiplied

    def test_map_receives_address(self):
        """Test that mapping function receives address tuple."""
        l = llll(1, 2, 3)
        addresses = []
        l.map(lambda x, addr: addresses.append(addr) or x)
        assert len(addresses) == 3
        assert all(isinstance(addr, tuple) for addr in addresses)


class TestUtilities:
    """Test utility methods."""

    def test_is_atomic_true(self):
        """Test is_atomic() returns True for single values."""
        atomic = llll(42)
        assert not atomic.is_atomic()

    def test_is_atomic_false(self):
        """Test is_atomic() returns False for lists."""
        nested = llll(1, [2, 3])
        assert not nested.is_atomic()

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


class TestFileIO:
    """Test file I/O operations."""

    def test_write_read_txt(self, tmp_path):
        """Test writing and reading text format."""
        filepath = str(tmp_path / "data.txt")
        a = llll(1, 2, [3, 4])
        a.write(filepath)
        b = llll.read(filepath)
        assert a == b

    def test_write_read_native_format(self, tmp_path):
        """Test writing and reading native .llll format."""
        a = llll(1, 2, [3, 4])
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
