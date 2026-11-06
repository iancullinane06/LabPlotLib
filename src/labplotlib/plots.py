from typing import Optional, Sequence

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from .styling import PathLike, apply_theme, finish_plot, style_axis


def _new_figure(figsize):
    apply_theme()
    return plt.subplots(figsize=figsize)


def line_plot(
    x: Sequence[float],
    y: Sequence[float],
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    filename: Optional[str] = None,
    save_directory: Optional[PathLike] = None,
    show: bool = True,
    figsize=(8, 5),
) -> Figure:
    """Plot ``y`` against ``x`` as a line and return the figure."""
    fig, ax = _new_figure(figsize)
    ax.plot(x, y)
    style_axis(ax, title, xlabel, ylabel)
    return finish_plot(fig, filename, save_directory, show)


def scatter_with_fit(
    x: Sequence[float],
    y: Sequence[float],
    degree: int = 1,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    filename: Optional[str] = None,
    save_directory: Optional[PathLike] = None,
    show: bool = True,
    figsize=(8, 5),
) -> Figure:
    """Scatter the data with a least-squares polynomial fit of ``degree``."""
    x_values = np.asarray(x, dtype=float)
    y_values = np.asarray(y, dtype=float)
    if x_values.shape != y_values.shape:
        raise ValueError("x and y must have the same shape")
    if degree < 1 or x_values.size <= degree:
        raise ValueError("degree must be >= 1 and less than the number of points")

    coefficients = np.polyfit(x_values, y_values, degree)
    fit_x = np.linspace(x_values.min(), x_values.max(), 200)

    fig, ax = _new_figure(figsize)
    ax.scatter(x_values, y_values, label="data")
    ax.plot(fit_x, np.polyval(coefficients, fit_x), color="C1", label=f"fit (degree {degree})")
    ax.legend()
    style_axis(ax, title, xlabel, ylabel)
    return finish_plot(fig, filename, save_directory, show)


def errorbar_plot(
    x: Sequence[float],
    y: Sequence[float],
    yerr: Optional[Sequence[float]] = None,
    xerr: Optional[Sequence[float]] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    filename: Optional[str] = None,
    save_directory: Optional[PathLike] = None,
    show: bool = True,
    figsize=(8, 5),
) -> Figure:
    """Plot ``y`` against ``x`` with optional error bars."""
    fig, ax = _new_figure(figsize)
    ax.errorbar(x, y, yerr=yerr, xerr=xerr, fmt="o", capsize=3)
    style_axis(ax, title, xlabel, ylabel)
    return finish_plot(fig, filename, save_directory, show)
