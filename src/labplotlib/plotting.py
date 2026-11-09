"""Composable plotting helpers for laboratory measurements."""

from typing import Optional, Sequence, Tuple, Union

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .measurement import unpack_measurements
from .methods import Errors, PlotErrors, _data, polynomial_fit
from matplotlib.colors import Colormap, to_hex, to_rgba

from .styling import PathLike, add_colorbar, finish_plot, get_cmap, style_axis

Size = Tuple[float, float]

def _plot_errors(errors: PlotErrors, size: int, name: str) -> np.ndarray:
    values = np.asarray(errors, dtype=float)
    if values.ndim == 0:
        values = np.full(size, values.item())
    if values.shape not in ((size,), (2, size)) or not np.all(np.isfinite(values)):
        raise ValueError(f"{name} must be a finite scalar, length-N, or 2-by-N sequence")
    if np.any(values < 0):
        raise ValueError(f"{name} must be non-negative")
    return values


def _axes(ax: Optional[Axes], figsize: Size) -> Tuple[Figure, Axes]:
    if ax is None:
        return plt.subplots(figsize=figsize)
    return ax.figure, ax


def _series_colors(ax: Axes, color: Optional[str], fit_color: Optional[str]) -> Tuple[str, str]:
    """Data colour (next in the axes cycle if unset) and a paler fit colour of the same hue."""
    if color is None:
        color = ax._get_lines.get_next_color()
    if fit_color is None:
        r, g, b, _ = to_rgba(color)
        fit_color = to_hex((1 - (1 - r) * 0.5, 1 - (1 - g) * 0.5, 1 - (1 - b) * 0.5))
    return color, fit_color


def _finish_if_requested(
    fig: Figure, filename: Optional[PathLike], save_directory: Optional[PathLike], show: bool
) -> Figure:
    if filename is not None or show:
        return finish_plot(fig, filename, save_directory, show)
    return fig


def line_plot(
    x: Sequence[float],
    y: Sequence[float],
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    filename: Optional[PathLike] = None,
    save_directory: Optional[PathLike] = None,
    show: bool = False,
    figsize: Size = (8, 5),
    *,
    ax: Optional[Axes] = None,
    label: Optional[str] = None,
    color: Optional[str] = None,
    marker: Optional[str] = None,
    linestyle: str = "-",
) -> Figure:
    """Draw a line on ax (or a new figure), and return the figure."""
    x_values, y_values = _data(x, y)
    fig, ax = _axes(ax, figsize)
    ax.plot(x_values, y_values, label=label, color=color, marker=marker, linestyle=linestyle)
    style_axis(ax, title, xlabel, ylabel)
    return _finish_if_requested(fig, filename, save_directory, show)


def scatter_plot(
    x: Sequence[float],
    y: Sequence[float],
    c: Optional[Sequence[float]] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    filename: Optional[PathLike] = None,
    save_directory: Optional[PathLike] = None,
    show: bool = False,
    figsize: Size = (8, 5),
    *,
    ax: Optional[Axes] = None,
    label: Optional[str] = None,
    color: Optional[str] = None,
    marker: str = "o",
    cmap: Union[str, Colormap, None] = None,
    colorbar: bool = False,
    colorbar_label: Optional[str] = None,
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
) -> Figure:
    """Scatter points, optionally coloured by ``c`` with a colormap and colourbar."""
    x_values, y_values = _data(x, y)
    if c is None:
        if colorbar or cmap is not None:
            raise ValueError("c is required when cmap or colorbar is used")
        c_values = None
    else:
        c_values = np.asarray(c, dtype=float)
        if c_values.shape != x_values.shape:
            raise ValueError("c must have the same length as x and y")
    fig, ax = _axes(ax, figsize)
    if c_values is None:
        ax.scatter(x_values, y_values, label=label, color=color, marker=marker)
    else:
        mappable = ax.scatter(x_values, y_values, c=c_values, cmap=get_cmap(cmap), marker=marker,
                              vmin=vmin, vmax=vmax, label=label)
        if colorbar:
            add_colorbar(fig, ax, mappable, colorbar_label)
    style_axis(ax, title, xlabel, ylabel)
    return _finish_if_requested(fig, filename, save_directory, show)


def scatter_with_fit(
    x: Sequence[float],
    y: Sequence[float],
    degree: int = 1,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    filename: Optional[PathLike] = None,
    save_directory: Optional[PathLike] = None,
    show: bool = False,
    label_slope: bool = True,
    label_intercept: bool = True,
    figsize: Size = (8, 5),
    *,
    ax: Optional[Axes] = None,
    yerr: Optional[Errors] = None,
    label: str = "data",
    color: Optional[str] = None,
    fit_color: Optional[str] = None,
    marker: str = "o",
) -> Figure:
    """Plot measurements and a polynomial fit; yerr weights the fit when supplied."""
    if yerr is None:
        _, yerr = unpack_measurements(y)
    x_values, y_values = _data(x, y)
    fit = polynomial_fit(x_values, y_values, degree, yerr)
    fit_x = np.linspace(x_values.min(), x_values.max(), 200)
    fig, ax = _axes(ax, figsize)
    color, fit_color = _series_colors(ax, color, fit_color)
    if yerr is None:
        ax.scatter(x_values, y_values, label=label, color=color, marker=marker)
    else:
        ax.errorbar(x_values, y_values, yerr=yerr, fmt=marker, color=color, label=label, capsize=3)
    ax.plot(
        fit_x, np.polyval(fit.coefficients, fit_x),
        color=fit_color, label=f"fit (y = {fit.coefficients[-2]:.3g}x" + (f" + {fit.coefficients[-1]:.3g}" if label_intercept else "") + ")" if label_slope else f"fit (degree {degree})",
    )
    ax.legend()
    style_axis(ax, title, xlabel, ylabel)
    return _finish_if_requested(fig, filename, save_directory, show)


def errorbar_plot(
    x: Sequence[float],
    y: Sequence[float],
    yerr: Optional[PlotErrors] = None,
    xerr: Optional[PlotErrors] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    filename: Optional[PathLike] = None,
    save_directory: Optional[PathLike] = None,
    show: bool = False,
    figsize: Size = (8, 5),
    *,
    ax: Optional[Axes] = None,
    label: Optional[str] = None,
    color: Optional[str] = None,
    marker: str = "o",
    capsize: float = 3,
) -> Figure:
    """Plot measurements with optional symmetric or asymmetric uncertainties."""
    if yerr is None:
        _, yerr = unpack_measurements(y)
    if xerr is None:
        _, xerr = unpack_measurements(x)
    x_values, y_values = _data(x, y)
    plot_yerr = None if yerr is None else _plot_errors(yerr, x_values.size, "yerr")
    plot_xerr = None if xerr is None else _plot_errors(xerr, x_values.size, "xerr")
    fig, ax = _axes(ax, figsize)
    ax.errorbar(x_values, y_values, yerr=plot_yerr, xerr=plot_xerr, fmt=marker, capsize=capsize,
                label=label, color=color)
    style_axis(ax, title, xlabel, ylabel)
    return _finish_if_requested(fig, filename, save_directory, show)


def scatter_with_residuals(
    x: Sequence[float],
    y: Sequence[float],
    degree: int = 1,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    filename: Optional[PathLike] = None,
    save_directory: Optional[PathLike] = None,
    show: bool = False,
    label_slope: bool = True,
    figsize: Size = (8, 7),
    *,
    axes: Optional[Tuple[Axes, Axes]] = None,
    yerr: Optional[Errors] = None,
    label: str = "data",
    color: Optional[str] = None,
    fit_color: Optional[str] = None,
    marker: str = "o",
) -> Figure:
    """Plot a polynomial fit and its residuals (observed minus predicted)."""
    if yerr is None:
        _, yerr = unpack_measurements(y)
    x_values, y_values = _data(x, y)
    fit = polynomial_fit(x_values, y_values, degree, yerr)
    if axes is None:
        fig, (ax, residual_ax) = plt.subplots(2, 1, figsize=figsize, sharex=True, height_ratios=[3, 1])
    else:
        ax, residual_ax = axes
        if ax is residual_ax or ax.figure is not residual_ax.figure:
            raise ValueError("axes must be distinct and belong to the same figure")
        fig = ax.figure
    color, fit_color = _series_colors(ax, color, fit_color)
    scatter_with_fit(x_values, y_values, degree, title, None, ylabel, ax=ax, yerr=yerr,
                     label=label, color=color, fit_color=fit_color, marker=marker, label_slope=label_slope)
    if yerr is None:
        residual_ax.scatter(x_values, fit.residuals, color=color, marker=marker)
    else:
        residual_ax.errorbar(x_values, fit.residuals, yerr=yerr, fmt=marker, color=color, capsize=3)
    residual_ax.axhline(0, color="k", linestyle="--")
    style_axis(residual_ax, "Residuals", xlabel, f"Residual ({ylabel})" if ylabel else "Residual")
    return _finish_if_requested(fig, filename, save_directory, show)
