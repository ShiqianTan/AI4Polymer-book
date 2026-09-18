"""Keep base units explicit; no rounding is used in stored byte counts."""
import math

KiB = 2**10
MiB = 2**20
GiB = 2**30
GB = 10**9
TB = 10**12


def positive_int(value: int, name: str, *, allow_zero: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if value < (0 if allow_zero else 1):
        raise ValueError(f"{name} must be {'nonnegative' if allow_zero else 'positive'}")
    return value


def positive_number(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or (isinstance(value, float) and not math.isfinite(value)) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def fraction(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or (isinstance(value, float) and not math.isfinite(value)):
        raise ValueError(f"{name} must be finite")
    if not 0 < value <= 1:
        raise ValueError(f"{name} must lie in (0, 1]")
    return float(value)


def ceil_div(numerator: int, denominator: int) -> int:
    positive_int(numerator, "numerator", allow_zero=True)
    positive_int(denominator, "denominator")
    return (numerator + denominator - 1) // denominator


def log10_big_int(value: int) -> float:
    """log10 of an arbitrary-precision positive integer without double overflow."""
    positive_int(value, "value")
    if value.bit_length() <= 1023:
        return math.log10(value)
    shift = value.bit_length() - 53
    top = value >> shift
    return (value.bit_length() + math.log2(top / 2**53)) * math.log10(2)
