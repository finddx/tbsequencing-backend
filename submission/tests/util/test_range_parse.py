from decimal import Decimal

import pytest
from psycopg2.extras import NumericRange

from submission.util.range import parse_numeric_range

r_0_1 = NumericRange(Decimal("0.1"), Decimal("0.1"), "[]")
r_1 = NumericRange(Decimal("1"), Decimal("1"), "[]")
gt_0_1 = NumericRange(Decimal("0.1"), None, "(]")
gte_0_1 = NumericRange(Decimal("0.1"), None, "[]")
lt_0_1 = NumericRange(Decimal(0), Decimal("0.1"), "[)")
lte_0_1 = NumericRange(Decimal(0), Decimal("0.1"), "[]")


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("0.1", r_0_1),
        ("0,1", r_0_1),
        (" 0,1 ", r_0_1),
        (".1", r_0_1),
        (",1", r_0_1),
        (" ,1 ", r_0_1),
        ("1", r_1),
        ("1.", r_1),
        (" 1 , ", r_1),
    ],
)
def test_single_number(raw: str, expected: NumericRange):
    """Assert single-number values parsed into psycopg2's NumericRange."""
    assert parse_numeric_range(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("=0.1", r_0_1),
        ("==0,1", r_0_1),
        ("> 0,1 ", gt_0_1),
        (" > = . 1 ", gte_0_1),
        (" ≥ ,1 ", gte_0_1),
        ("< 0,1 ", lt_0_1),
        (" < = . 1 ", lte_0_1),
        (" ≤ ,1 ", lte_0_1),
    ],
)
def test_single_number_with_sign(raw: str, expected: NumericRange):
    """Assert single-number values with equality sign parsed into psycopg2's NumericRange."""
    assert parse_numeric_range(raw) == expected


r_12_22_oo = NumericRange(Decimal("1.2"), Decimal("2.2"), bounds="[]")
r_12_22_ox = NumericRange(Decimal("1.2"), Decimal("2.2"), bounds="[)")
r_12_22_xo = NumericRange(Decimal("1.2"), Decimal("2.2"), bounds="(]")


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("[1.2,2.2]", r_12_22_oo),
        ("(1,2,2,2] ", r_12_22_xo),
        (" [ 1.2 , 2,2 ) ", r_12_22_ox),
    ],
)
def test_range(raw: str, expected: NumericRange):
    """Assert range values parsed into psycopg2's NumericRange."""
    assert parse_numeric_range(raw) == expected


r_01_22_xo = NumericRange(Decimal("0.1"), Decimal("2.2"), "(]")


@pytest.mark.parametrize(
    "raw,expected",
    [
        (".1 or 2,2", r_01_22_xo),
        (" ,1 - 2.2 ", r_01_22_xo),
        ("0.1 / 2.2", r_01_22_xo),
        ("0,1 | 2,2", r_01_22_xo),
    ],
)
def test_exotic_range(raw: str, expected: NumericRange):
    """Assert exotic range format values parsed into psycopg2's NumericRange."""
    assert parse_numeric_range(raw) == expected
