"""Measurements and independent uncertainty propagation."""

from dataclasses import dataclass
from typing import Any, Optional, Union

import numpy as np

Numeric = Union[float, np.ndarray]


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
        """Read named DataFrame columns; relative errors are fractions, not percentages."""
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
