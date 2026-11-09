"""Measurements and independent uncertainty propagation."""

from dataclasses import dataclass
from typing import Any, Literal, Optional, Union

import numpy as np

Numeric = Union[float, np.ndarray]

_SI_PREFIXES = {
    "quecto": ("q", -30), "q": ("q", -30),
    "ronto": ("r", -27), "r": ("r", -27),
    "yocto": ("y", -24), "y": ("y", -24),
    "zepto": ("z", -21), "z": ("z", -21),
    "atto": ("a", -18), "a": ("a", -18),
    "femto": ("f", -15), "f": ("f", -15),
    "pico": ("p", -12), "p": ("p", -12),
    "nano": ("n", -9), "n": ("n", -9),
    "micro": ("µ", -6), "µ": ("µ", -6), "μ": ("µ", -6), "u": ("µ", -6),
    "milli": ("m", -3), "m": ("m", -3),
    "centi": ("c", -2), "c": ("c", -2),
    "deci": ("d", -1), "d": ("d", -1),
    "deca": ("da", 1), "da": ("da", 1),
    "hecto": ("h", 2), "h": ("h", 2),
    "kilo": ("k", 3), "k": ("k", 3),
    "mega": ("M", 6), "M": ("M", 6),
    "giga": ("G", 9), "G": ("G", 9),
    "tera": ("T", 12), "T": ("T", 12),
    "peta": ("P", 15), "P": ("P", 15),
    "exa": ("E", 18), "E": ("E", 18),
    "zetta": ("Z", 21), "Z": ("Z", 21),
    "yotta": ("Y", 24), "Y": ("Y", 24),
    "ronna": ("R", 27), "R": ("R", 27),
    "quetta": ("Q", 30), "Q": ("Q", 30),
}


def _numeric(value: Any, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain only finite numbers")
    return result


@dataclass(frozen=True, eq=False)
class Measurement:
    """Scalar or array of values and their absolute standard uncertainties.

    An absent uncertainty is represented by None, rather than a zero error bar.
    Arithmetic combines supplied uncertainties in quadrature, assuming operands
    are independent; absent contributions are not included.
    """

    value: Any
    uncertainty: Optional[Any] = None
    unit: Optional[str] = None
    prefix: Optional[str] = None

    def __post_init__(self) -> None:
        value = _numeric(self.value, "value").copy()
        value.setflags(write=False)
        object.__setattr__(self, "value", value)
        if self.uncertainty is not None:
            uncertainty = _numeric(self.uncertainty, "uncertainty")
            try:
                uncertainty = np.broadcast_to(uncertainty, value.shape).copy()
            except ValueError as exc:
                raise ValueError("uncertainty must be broadcastable to the value shape") from exc
            if np.any(uncertainty < 0):
                raise ValueError("uncertainty must be non-negative")
            uncertainty.setflags(write=False)
            object.__setattr__(self, "uncertainty", uncertainty)
        if self.unit is not None:
            if not isinstance(self.unit, str) or not self.unit.strip():
                raise ValueError("unit must be a non-empty string")
            object.__setattr__(self, "unit", self.unit.strip())
        if self.prefix is not None:
            if self.unit is None:
                raise ValueError("prefix requires a unit")
            if not isinstance(self.prefix, str) or self.prefix not in _SI_PREFIXES:
                raise ValueError(f"unsupported SI prefix: {self.prefix}")

    @classmethod
    def from_pm(
        cls, value: Any, uncertainty: Optional[Any] = None, *,
        relative: Optional[Any] = None, granularity: Optional[Any] = None,
    ) -> "Measurement":
        """Combine absolute, fractional relative, and granularity uncertainties."""
        values = _numeric(value, "value")
        terms = []
        for name, term in (("uncertainty", uncertainty), ("relative", relative),
                           ("granularity", granularity)):
            if term is None:
                continue
            numbers = _numeric(term, name)
            if np.any(numbers < 0):
                raise ValueError(f"{name} must be non-negative")
            try:
                numbers = np.broadcast_to(numbers, values.shape)
            except ValueError as exc:
                raise ValueError(f"{name} must be broadcastable to the value shape") from exc
            terms.append(numbers * np.abs(values) if name == "relative" else numbers)
        combined = np.sqrt(sum(term**2 for term in terms)) if terms else None
        return cls(values, combined)

    @classmethod
    def from_stdev(
        cls, samples: Any, *, axis: Optional[int] = None, mean_error: bool = False,
        granularity: Optional[Any] = None,
    ) -> "Measurement":
        """Use sample standard deviation (ddof=1), or standard error of the mean."""
        values = _numeric(samples, "samples")
        count = values.size if axis is None else values.shape[axis]
        if count < 2:
            raise ValueError("at least two measurements are needed for sample standard deviation")
        mean = np.mean(values, axis=axis)
        uncertainty = np.std(values, axis=axis, ddof=1)
        if mean_error:
            uncertainty = uncertainty / np.sqrt(count)
        return cls.from_pm(mean, uncertainty, granularity=granularity)

    @classmethod
    def from_dataframe(
        cls, frame: Any, value: str, *, uncertainty: Optional[str] = None,
        relative: Optional[str] = None, granularity: Optional[Any] = None,
    ) -> "Measurement":
        """Read named DataFrame columns;
        relative errors
        
        """
        return cls.from_pm(
            frame[value], None if uncertainty is None else frame[uncertainty],
            relative=None if relative is None else frame[relative], granularity=granularity,
        )

    def relative_uncertainty(self) -> Optional[np.ndarray]:
        """Return fractional uncertainty; zero-valued measurements have no relative error."""
        if self.uncertainty is None:
            return None
        if np.any(self.value == 0):
            raise ValueError("relative uncertainty is undefined for zero-valued measurements")
        return self.uncertainty / np.abs(self.value)

    def mean(self, *, axis: Optional[int] = None) -> "Measurement":
        """Return the mean with standard error and independent uncertainties combined."""
        result = Measurement.from_stdev(self.value, axis=axis, mean_error=True)
        uncertainty = result.uncertainty
        if self.uncertainty is not None:
            count = self.value.size if axis is None else self.value.shape[axis]
            propagated = np.hypot.reduce(self.uncertainty, axis=axis) / count
            uncertainty = np.hypot(uncertainty, propagated)
        return Measurement(result.value, uncertainty, unit=self.unit, prefix=self.prefix)

    def _binary(self, other: Any, operation: str) -> "Measurement":
        other = other if isinstance(other, Measurement) else Measurement(other)
        a, b = self.value, other.value
        if operation == "add":
            result, da, db = a + b, 1, 1
        elif operation == "subtract":
            result, da, db = a - b, 1, -1
        elif operation == "multiply":
            result, da, db = a * b, b, a
        else:
            if np.any(b == 0):
                raise ZeroDivisionError("cannot divide by a zero-valued measurement")
            result, da, db = a / b, 1 / b, -a / b**2
        terms = []
        if self.uncertainty is not None:
            terms.append((da * self.uncertainty) ** 2)
        if other.uncertainty is not None:
            terms.append((db * other.uncertainty) ** 2)
        return Measurement(result, np.sqrt(sum(terms)) if terms else None)

    def __add__(self, other: Any) -> "Measurement":
        return self._binary(other, "add")

    __radd__ = __add__

    def __sub__(self, other: Any) -> "Measurement":
        return self._binary(other, "subtract")

    def __rsub__(self, other: Any) -> "Measurement":
        return Measurement(other)._binary(self, "subtract")

    def __mul__(self, other: Any) -> "Measurement":
        return self._binary(other, "multiply")

    __rmul__ = __mul__

    def __truediv__(self, other: Any) -> "Measurement":
        return self._binary(other, "divide")

    def __rtruediv__(self, other: Any) -> "Measurement":
        return Measurement(other)._binary(self, "divide")

    def __pow__(self, power: float) -> "Measurement":
        if not np.isfinite(power):
            raise ValueError("power must be finite")
        with np.errstate(divide="raise", invalid="raise", over="raise"):
            result = self.value**power
            if self.uncertainty is None:
                uncertainty = None
            elif power == 0:
                uncertainty = np.zeros_like(self.value)
            else:
                uncertainty = np.abs(power * self.value ** (power - 1)) * self.uncertainty
        return Measurement(result, uncertainty)

    def to_string(
        self,
        format: Literal["auto", "raw", "scientific"] = "auto",
        *,
        decimals: Optional[int] = 3,
        unit: Optional[str] = None,
        prefix: Optional[str] = None,
    ) -> str:
        """Format the measurement, optionally overriding its display unit and prefix."""
        if format not in ("auto", "raw", "scientific"):
            raise ValueError("format must be 'auto', 'raw', or 'scientific'")
        if decimals is not None and (
            not isinstance(decimals, int) or isinstance(decimals, bool) or decimals < 0
        ):
            raise ValueError("decimals must be a non-negative integer or None")

        display_unit = self.unit if unit is None else unit
        display_prefix = self.prefix if unit is None and prefix is None else prefix
        if display_unit is not None and (
            not isinstance(display_unit, str) or not display_unit.strip()
        ):
            raise ValueError("unit must be a non-empty string")
        if display_prefix is not None and display_unit is None:
            raise ValueError("prefix requires a unit")

        prefix_symbol = ""
        scale = 1.0
        if display_prefix is not None:
            if not isinstance(display_prefix, str) or display_prefix not in _SI_PREFIXES:
                raise ValueError(f"unsupported SI prefix: {display_prefix}")
            prefix_symbol, exponent = _SI_PREFIXES[display_prefix]
            scale = 10.0**exponent

        value = self.value / scale
        uncertainty = None if self.uncertainty is None else self.uncertainty / scale
        if not np.all(np.isfinite(value)) or (
            uncertainty is not None and not np.all(np.isfinite(uncertainty))
        ):
            raise ValueError("prefix scaling produces non-finite display values")

        def format_number(number: float) -> str:
            use_scientific = format == "scientific" or (
                format == "auto" and number != 0 and not 1e-3 <= abs(number) < 1e3
            )
            if not use_scientific:
                return str(number) if decimals is None else f"{number:.{decimals}f}"
            if decimals is None:
                mantissa, exponent = np.format_float_scientific(
                    np.float64(number), unique=True, trim="-"
                ).split("e")
            else:
                mantissa, exponent = f"{number:.{decimals}e}".split("e")
            superscript_exponent = str(int(exponent)).translate(
                str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
            )
            return f"{mantissa} x 10{superscript_exponent}"

        def format_values(values: np.ndarray) -> str:
            if values.ndim == 0:
                return format_number(float(values))
            return np.array2string(
                values, formatter={"float_kind": format_number}
            )

        result = format_values(value)
        if uncertainty is not None:
            result += f" ± {format_values(uncertainty)}"
        if display_unit is not None:
            result += f" {prefix_symbol}{display_unit}"
        return result

    def set_unit(self, unit: Optional[str], prefix: Optional[str] = None) -> None:
        """Set display-only unit metadata; this does not convert values or affect math."""
        if unit is not None:
            if not isinstance(unit, str) or not unit.strip():
                raise ValueError("unit must be a non-empty string")
            unit = unit.strip()
        if prefix is not None:
            if unit is None:
                raise ValueError("prefix requires a unit")
            if not isinstance(prefix, str) or prefix not in _SI_PREFIXES:
                raise ValueError(f"unsupported SI prefix: {prefix}")
        object.__setattr__(self, "unit", unit)
        object.__setattr__(self, "prefix", prefix)

    def __str__(self) -> str:
        return self.to_string()


def unpack_measurements(data: Any) -> tuple:
    """Return numerical data and errors, including a Series of scalar Measurements."""
    if isinstance(data, Measurement):
        return data.value, data.uncertainty
    if hasattr(data, "__iter__") and not isinstance(data, (str, bytes)):
        items = list(data)
        if any(isinstance(item, Measurement) for item in items):
            if not all(isinstance(item, Measurement) and item.value.ndim == 0 for item in items):
                raise ValueError("a measurement column must contain only scalar Measurements")
            values = np.array([item.value.item() for item in items])
            if any(item.uncertainty is None for item in items):
                if not all(item.uncertainty is None for item in items):
                    raise ValueError("measurement column mixes known and missing uncertainties")
                return values, None
            return values, np.array([item.uncertainty.item() for item in items])
    return data, None
