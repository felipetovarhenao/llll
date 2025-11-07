from llll import llll


def test_null_llll():
    l = llll()
    assert isinstance(l, llll)
    assert len(l) == 0
    assert l.depth() == 0
