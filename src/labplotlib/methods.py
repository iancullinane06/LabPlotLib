from dataclasses import dataclass
from typing import Optional, Sequence, Tuple, Union

import numpy as np
from scipy.stats import chi2

from .measurement import unpack_measurements

Errors = Union[float, Sequence[float]]
PlotErrors = Union[float, Sequence[float], Sequence[Sequence[float]]]

@dataclass(frozen=True)
class PolynomialFit:
    """Fit results; coefficients are ordered from highest power to constant."""

    coefficients: np.ndarray
    residuals: np.ndarray
    r_squared: Optional[float]
    chi_squared: Optional[float]
    reduced_chi_squared: Optional[float]


def _data(x: Sequence[float], y: Sequence[float]) -> Tuple[np.ndarray, np.ndarray]:
    x_values = np.asarray(unpack_measurements(x)[0], dtype=float)
    y_values = np.asarray(unpack_measurements(y)[0], dtype=float)
    if x_values.ndim != 1 or y_values.ndim != 1 or x_values.size == 0:
        raise ValueError("x and y must be non-empty one-dimensional sequences")
    if x_values.shape != y_values.shape:
        raise ValueError("x and y must have the same length")
    if not np.all(np.isfinite(x_values)) or not np.all(np.isfinite(y_values)):
        raise ValueError("x and y must contain only finite values")
    return x_values, y_values


def _errors(errors: Errors, size: int, name: str, positive: bool = False) -> np.ndarray:
    values = np.asarray(errors, dtype=float)
    if values.ndim == 0:
        values = np.full(size, values.item())
    if values.ndim != 1 or values.size != size or not np.all(np.isfinite(values)):
        raise ValueError(f"{name} must be a finite scalar or a sequence matching the data")
    invalid = np.any(values <= 0) if positive else np.any(values < 0)
    if invalid:
        requirement = "positive" if positive else "non-negative"
        raise ValueError(f"{name} must be {requirement}")
    return values


def polynomial_fit(
    x: Sequence[float],
    y: Sequence[float],
    degree: int = 1,
    yerr: Optional[Errors] = None,
) -> PolynomialFit:
    """Fit y vs x, optionally weighting by independent y standard deviations.

    R² is unweighted. Chi-squared is provided only when yerr is given;
    reduced chi-squared is unavailable when there are no degrees of freedom.
    """
    _, inferred_yerr = unpack_measurements(y)
    if yerr is None:
        yerr = inferred_yerr
    x_values, y_values = _data(x, y)
    if isinstance(degree, bool) or not isinstance(degree, (int, np.integer)) or degree < 1:
        raise ValueError("degree must be a positive integer")
    if x_values.size <= degree or np.unique(x_values).size <= degree:
        raise ValueError("a fit needs at least degree + 1 points with distinct x values")
    uncertainties = None if yerr is None else _errors(yerr, x_values.size, "yerr", True)
    weights = None if uncertainties is None else 1.0 / uncertainties
    coefficients = np.polyfit(x_values, y_values, degree, w=weights)
    residuals = y_values - np.polyval(coefficients, x_values)
    total = float(np.sum((y_values - np.mean(y_values)) ** 2))
    r_squared = None if total == 0 else float(1 - np.sum(residuals**2) / total)
    chi_squared = None
    reduced_chi_squared = None
    if uncertainties is not None:
        chi_squared = float(np.sum((residuals / uncertainties) ** 2))
        dof = x_values.size - degree - 1
        if dof > 0:
            reduced_chi_squared = chi_squared / dof
    return PolynomialFit(coefficients, residuals, r_squared, chi_squared, reduced_chi_squared)


def k_means(X, k, max_iters=100):
    """Perform k-means clustering on the dataset X."""
    n_samples, n_features = X.shape
    # Initialize centroids randomly from the data points
    rng = np.random.default_rng()
    centroids = X[rng.choice(n_samples, k, replace=False)]
    for _ in range(max_iters):
        # Assign each sample to the nearest centroid
        distances = np.linalg.norm(X[:, np.newaxis, :] - centroids[np.newaxis, :, :], axis=2)
        labels = np.argmin(distances, axis=1)
        # Update centroids
        new_centroids = np.array([X[labels == i].mean(axis=0) for i in range(k)])
        if np.allclose(centroids, new_centroids):
            break
        centroids = new_centroids
    return centroids, labels


def chi_squared(y_obs, y_exp, y_err):
    """Compute the chi-squared statistic for observed and expected data with errors."""
    y_obs = np.asarray(y_obs)
    y_exp = np.asarray(y_exp)
    y_err = np.asarray(y_err)
    chi2 = np.sum(((y_obs - y_exp) / y_err) ** 2)
    return chi2


def reduced_chi_squared(y_obs, y_exp, y_err, dof):
    """Compute the reduced chi-squared statistic for observed and expected data with errors."""
    chi2 = chi_squared(y_obs, y_exp, y_err)
    return chi2 / dof


def p_value_chi_squared(y_obs, y_exp, y_err, dof=1):
    """Compute the p-value for the chi-squared statistic with the given degrees of freedom."""
    chi2_stat = chi_squared(y_obs, y_exp, y_err)
    p_value = 1 - chi2.cdf(chi2_stat, dof)
    return p_value
