from __future__ import annotations

from apgorm import LazyList


def test_lazy_list():
    initial = range(0, 500)
    ll = LazyList(initial, str)

    assert len(initial) == len(ll)
    assert list(ll[0:5]) == [str(v) for v in initial[0:5]]
    assert ll[6] == str(initial[6])
    assert list(ll) == [str(v) for v in initial]

    assert repr(ll)  # essentially make sure it doesn't crash

    sll = LazyList([0, 1], str)
    assert repr(sll)

    mll = LazyList([0, 1, 2, 3, 4], str)
    assert repr(mll)
