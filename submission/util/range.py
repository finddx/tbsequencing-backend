import re
from decimal import Decimal
from typing import Optional

from psycopg2.extras import NumericRange

SIGN = {
    ">": "gt",
    ">=": "gte",
    "≥": "gte",
    "<": "lt",
    "<=": "lte",
    "≤": "lte",
    "=": "eq",
    "==": "eq",
}


def to_decimal(raw: str) -> Optional[Decimal]:
    """Transform string-represented decimal/none value into python type."""
    if raw.lower() == "none":
        return None
    try:
        converted = Decimal(raw.replace(",", "."))
    except Exception as exc:
        raise ValueError(f"cannot cast {raw!r} to decimal") from exc

    return converted


def _single_signed_to_range(val: str, sign: str) -> NumericRange:
    """Transform single signed value into numeric range."""
    amount = to_decimal(val)
    sign_decoded = SIGN[sign]

    if sign_decoded == "lt":
        lower, upper, bounds = Decimal(0), amount, "[)"
    elif sign_decoded == "lte":
        lower, upper, bounds = Decimal(0), amount, "[]"
    elif sign_decoded == "gt":
        lower, upper, bounds = amount, None, "(]"
    elif sign_decoded == "gte":
        lower, upper, bounds = amount, None, "[]"
    else:  # eq
        lower, upper, bounds = amount, amount, "[]"

    return NumericRange(lower=lower, upper=upper, bounds=bounds)


def parse_numeric_range(val: str = None) -> Optional[NumericRange]:
    """
    Parse input string into psycopg2's NumericRange object.

    Possible formats
    ----------------
    2 0.42 .42 0,42 ,42      exact number
    >0.42 ≤,42 <=0,42        exact number with compare sign before it (< > = == ≤ ≥ <= >=)
    (0.24, 0,42] [8,None)    range (both numbers required) (str(NumericRange) accepted)
    2.5-5 2.5or5 2.5|5       odd range formats. Bounds as (]
    Only positive numbers expected.
    """
    val = val.replace(" ", "")
    if not val:
        return None

    decimal_r = r"(\d*[.,]?\d*|[.,]\d+)"
    decimal_or_none_r = r"(\d*[.,]?\d*|[.,]\d+|None)"
    bound_l_r = r"([\(\[])"
    bound_r_r = r"([\)\]])"

    nrange = None

    if re.match(rf"^{bound_l_r}\d+,\d+,\d+{bound_r_r}", val):
        # [3,6,4] ambiguous format
        raise ValueError("ambiguous range format")

    if match := re.match(
        rf"^{bound_l_r}{decimal_or_none_r},{decimal_or_none_r}{bound_r_r}$",
        val,
    ):
        # [0.1,0.5) range format
        lbound, lower, upper, rbound = match.groups()
        if upper:
            lower = to_decimal(lower)
            upper = to_decimal(upper)
            nrange = NumericRange(lower=lower, upper=upper, bounds=f"{lbound}{rbound}")
        else:
            nrange = _single_signed_to_range(lower, ">")


    elif match := re.match(rf"^([<>=≤≥]|==|<=|>=){decimal_r}$", val):
        # >0.42 single number with sign format
        sign, amount = match.groups()
        nrange = _single_signed_to_range(amount, sign)

    elif match := re.match(rf"^{decimal_r}$", val):
        # 0.42 single number
        amount = to_decimal(match.group())
        nrange = NumericRange(lower=amount, upper=amount, bounds="[]")

    elif match := re.match(rf"{decimal_r}(?:or|-|/|\|){decimal_r}", val):
        # "2.5-5", "2.5or5", "2.5|5" exotic range format
        lower, upper = match.groups()
        lower = to_decimal(lower)
        upper = to_decimal(upper)
        nrange = NumericRange(lower=Decimal(lower), upper=Decimal(upper), bounds="(]")

    if not nrange:
        raise ValueError("unsupported numeric range format")

    if nrange.lower is None and nrange.upper is None:
        raise ValueError("empty (infinite) range")

    if (
        nrange.lower is not None
        and nrange.upper is not None
        and nrange.upper < nrange.lower
    ):
        raise ValueError("negative range")

    return nrange
