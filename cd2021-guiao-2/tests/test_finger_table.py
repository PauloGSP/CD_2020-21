"""Tests finger table."""
import pytest
from DHTNode import FingerTable


def test_finger_table():
    f = FingerTable(10, ("localhost", 5000), 4)

    assert f.getIdxFromId(11) == 1
    assert f.getIdxFromId(12) == 2
    assert f.getIdxFromId(14) == 3
    assert f.getIdxFromId(2) == 4

    f.fill(11, ("localhost", 5001))

    assert f.find(11) == ("localhost", 5001)
    assert f.find(12) == ("localhost", 5001)

    f.update(2, 12, ("localhost", 5002))
    f.update(3, 13, ("localhost", 5003))
    f.update(4, 15, ("localhost", 5004))

    assert f.as_list == [
        (11, ("localhost", 5001)),
        (12, ("localhost", 5002)),
        (13, ("localhost", 5003)),
        (15, ("localhost", 5004)),
    ]

    assert f.find(13) == ("localhost", 5002)

    assert f.refresh() == [
        (1, 11, ("localhost", 5001)),
        (2, 12, ("localhost", 5002)),
        (3, 14, ("localhost", 5003)),
        (4, 2, ("localhost", 5004)),
    ]
