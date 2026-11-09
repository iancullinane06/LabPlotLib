"""Least-squares fitting of arbitrary models, with built-in electronics models."""

import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import chi2

from .measurement import Measurement, unpack_measurements
from .methods import Errors, _data, _errors

Model = Callable[..., Any]


def exponential_decay(t, amplitude, tau, offset):
    """offset + amplitude * exp(-t / tau): RC discharge."""
    return offset + amplitude * np.exp(-np.asarray(t, dtype=float) / tau)


def exponential_rise(t, amplitude, tau, offset):
    """offset + amplitude * (1 - exp(-t / tau)): RC charging."""
    return offset + amplitude * (1 - np.exp(-np.asarray(t, dtype=float) / tau))


def lorentzian(x, amplitude, center, width, offset):
    """Lorentzian peak; ``width`` is the full width at half maximum, so Q = center / width."""
    half = width / 2
    return offset + amplitude * half**2 / ((np.asarray(x, dtype=float) - center) ** 2 + half**2)


def gaussian(x, amplitude, mean, sigma, offset):
    """Gaussian peak with standard deviation ``sigma`` on a constant offset."""
    return offset + amplitude * np.exp(-((np.asarray(x, dtype=float) - mean) ** 2) / (2 * sigma**2))


def power_law(x, coefficient, exponent):
    """coefficient * x ** exponent."""
    return coefficient * np.asarray(x, dtype=float) ** exponent


def diode(voltage, i_s, n_vt):
    """Shockley diode: i_s * (exp(voltage / n_vt) - 1); n_vt is ideality factor times kT/q."""
    with np.errstate(over="ignore"):
        return i_s * np.expm1(np.asarray(voltage, dtype=float) / n_vt)


def _first_crossing(x: np.ndarray, condition: np.ndarray, default: float) -> float:
    hits = np.flatnonzero(condition)
    return float(x[hits[0]] - x[0]) if hits.size else default


def _sorted(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    order = np.argsort(x)
    return x[order], y[order]


def _guess_decay(x: np.ndarray, y: np.ndarray) -> Sequence[float]:
    x, y = _sorted(x, y)
    offset, amplitude = y[-1], y[0] - y[-1]
    span = float(x[-1] - x[0]) or 1.0
    tau = _first_crossing(x, np.abs(y - offset) <= abs(amplitude) / np.e, span / 3)
    return [amplitude, tau or span / 3, offset]


def _guess_rise(x: np.ndarray, y: np.ndarray) -> Sequence[float]:
    x, y = _sorted(x, y)
    offset, amplitude = y[0], y[-1] - y[0]
    span = float(x[-1] - x[0]) or 1.0
    tau = _first_crossing(x, np.abs(y - offset) >= 0.632 * abs(amplitude), span / 3)
    return [amplitude, tau or span / 3, offset]


def _peak_guess(x: np.ndarray, y: np.ndarray) -> Tuple[float, float, float, float]:
    upward = y.max() - np.median(y) >= np.median(y) - y.min()
    offset = float(y.min() if upward else y.max())
    index = int(np.argmax(y) if upward else np.argmin(y))
    amplitude = float(y[index] - offset)
    inside = x[np.abs(y - offset) >= abs(amplitude) / 2]
    span = float(x.max() - x.min()) or 1.0
    width = float(inside.max() - inside.min()) if inside.size > 1 else span / 10
    return offset, amplitude, float(x[index]), max(width, span / x.size)


def _guess_lorentzian(x: np.ndarray, y: np.ndarray) -> Sequence[float]:
    offset, amplitude, center, width = _peak_guess(x, y)
    return [amplitude, center, width, offset]


def _guess_gaussian(x: np.ndarray, y: np.ndarray) -> Sequence[float]:
    offset, amplitude, center, width = _peak_guess(x, y)
    return [amplitude, center, width / 2.355, offset]


def _guess_power_law(x: np.ndarray, y: np.ndarray) -> Sequence[float]:
    positive = (x > 0) & (y > 0)
    if positive.sum() < 2 or np.unique(x[positive]).size < 2:
        return [1.0, 1.0]
    exponent, log_coefficient = np.polyfit(np.log(x[positive]), np.log(y[positive]), 1)
    return [float(np.exp(log_coefficient)), float(exponent)]


def _guess_diode(x: np.ndarray, y: np.ndarray) -> Sequence[float]:
    positive = y > 0
    if positive.sum() >= 2 and np.unique(x[positive]).size >= 2:
        slope, intercept = np.polyfit(x[positive], np.log(y[positive]), 1)
        if slope > 0:
            return [float(np.exp(intercept)), float(1 / slope)]
    return [1e-12, 0.05]


_GUESSES: Dict[Model, Callable[[np.ndarray, np.ndarray], Sequence[float]]] = {
    exponential_decay: _guess_decay,
    exponential_rise: _guess_rise,
    lorentzian: _guess_lorentzian,
    gaussian: _guess_gaussian,
    power_law: _guess_power_law,
    diode: _guess_diode,
}


@dataclass(frozen=True)
class ModelFit:
    """Result of :func:`fit_model`.

    ``chi_squared``, ``reduced_chi_squared`` and ``p_value`` are only available when
    uncertainties on y were supplied. Without them, parameter uncertainties are scaled
    to the scatter of the residuals.
    """

    model: Model
    names: Tuple[str, ...]
    values: np.ndarray
    uncertainties: np.ndarray
    covariance: np.ndarray
    residuals: np.ndarray
    dof: int
    r_squared: Optional[float]
    chi_squared: Optional[float] = None
    reduced_chi_squared: Optional[float] = None
    p_value: Optional[float] = None

    @property
    def parameters(self) -> Dict[str, Measurement]:
        """Fitted parameters as Measurements keyed by name."""
        return {
            name: Measurement(value, uncertainty)
            for name, value, uncertainty in zip(self.names, self.values, self.uncertainties)
        }

    def parameter(self, name: str) -> Measurement:
        """Return one fitted parameter as a Measurement."""
        parameters = self.parameters
        if name not in parameters:
            raise ValueError(f"unknown parameter {name!r}; choose from {', '.join(self.names)}")
        return parameters[name]

    def predict(self, x: Any) -> np.ndarray:
        """Evaluate the fitted model at ``x``."""
        return np.asarray(self.model(np.asarray(x, dtype=float), *self.values), dtype=float)

    def summary(self) -> str:
        """Multi-line text of the parameters and fit statistics."""
        lines = [f"{name} = {parameter.to_string(uncertainty_digits=2)}"
                 for name, parameter in self.parameters.items()]
        return "\n".join(lines + fit_statistics(self))


def fit_statistics(fit: Any) -> list:
    """Lines of text for chi-squared, reduced chi-squared, p-value and R² of a fit."""
    lines = []
    if getattr(fit, "chi_squared", None) is not None:
        lines.append(f"χ² = {fit.chi_squared:.3g}")
        if getattr(fit, "reduced_chi_squared", None) is not None:
            lines.append(f"χ²ᵣ = {fit.reduced_chi_squared:.3g} (dof = {fit.dof})")
        if getattr(fit, "p_value", None) is not None:
            lines.append(f"p = {fit.p_value:.3g}")
    if getattr(fit, "r_squared", None) is not None:
        lines.append(f"R² = {fit.r_squared:.4f}")
    return lines


def fit_model(
    model: Model,
    x: Sequence[float],
    y: Sequence[float],
    yerr: Optional[Errors] = None,
    p0: Optional[Sequence[float]] = None,
    *,
    bounds: Tuple[Any, Any] = (-np.inf, np.inf),
    maxfev: int = 20000,
) -> ModelFit:
    """Fit ``model(x, *parameters)`` to y by (weighted) least squares.

    The parameter names come from the model's signature. ``yerr`` (or the
    uncertainties of a Measurement ``y``) weights the fit and is treated as absolute,
    enabling chi-squared, reduced chi-squared and a p-value. ``p0`` is the initial guess;
    the built-in models estimate one automatically.
    """
    if yerr is None:
        _, yerr = unpack_measurements(y)
    x_values, y_values = _data(x, y)
    if not callable(model):
        raise TypeError("model must be callable as model(x, *parameters)")
    parameters = list(inspect.signature(model).parameters.values())[1:]
    if not parameters or any(
        p.kind not in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) for p in parameters
    ):
        raise ValueError("model must take x followed by one or more named parameters")
    names = tuple(p.name for p in parameters)
    if x_values.size <= len(names):
        raise ValueError("a fit needs more points than model parameters")
    sigma = None if yerr is None else _errors(yerr, x_values.size, "yerr", True)
    if p0 is None and model in _GUESSES:
        p0 = _GUESSES[model](x_values, y_values)
    if p0 is not None and len(p0) != len(names):
        raise ValueError(f"p0 must have {len(names)} values: {', '.join(names)}")
    try:
        popt, pcov = curve_fit(
            model, x_values, y_values, p0=p0, sigma=sigma, absolute_sigma=sigma is not None,
            bounds=bounds, maxfev=maxfev,
        )
    except RuntimeError as exc:
        raise RuntimeError("the fit did not converge; try a better starting guess p0") from exc
    if not np.all(np.isfinite(pcov)):
        raise ValueError("parameter uncertainties could not be estimated; check the model and p0")
    residuals = y_values - np.asarray(model(x_values, *popt), dtype=float)
    total = float(np.sum((y_values - y_values.mean()) ** 2))
    dof = x_values.size - len(names)
    chi_squared = reduced = p_value = None
    if sigma is not None:
        chi_squared = float(np.sum((residuals / sigma) ** 2))
        reduced = chi_squared / dof
        p_value = float(chi2.sf(chi_squared, dof))
    return ModelFit(
        model=model, names=names, values=popt, uncertainties=np.sqrt(np.diag(pcov)),
        covariance=pcov, residuals=residuals, dof=dof,
        r_squared=None if total == 0 else float(1 - np.sum(residuals**2) / total),
        chi_squared=chi_squared, reduced_chi_squared=reduced, p_value=p_value,
    )
