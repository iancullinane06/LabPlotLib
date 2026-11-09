# Plotting

```python
from labplotlib import line_plot, scatter_with_fit, errorbar_plot, scatter_with_residuals
```

Each function returns a Matplotlib `Figure`. Inputs must be non-empty,
one-dimensional, equally sized sequences of finite values. `Measurement`
arrays and sequences of scalar measurements can also be used. Plotting
functions do not apply a global theme. They do not show or save unless
requested; if neither is requested, they do not finalize layout. Use
[`finish_plot`](styling.md)
when the figure is ready.

## Shared parameters

The function sections below specify which of these options are available and
their defaults. Options following `*` in a signature are keyword-only.

| Parameter | Meaning |
| --- | --- |
| `x`, `y` | Horizontal and vertical data, with matching lengths. |
| `title`, `xlabel`, `ylabel` | Optional text for the axes; `None` leaves an existing label unchanged. |
| `filename` | Optional file name or path; triggers saving when supplied. |
| `save_directory` | Optional base directory for saving; defaults to the current directory and is ignored without a filename. |
| `show` | Show the figure when `True`; defaults to `False`. |
| `figsize` | Figure size in inches when creating a figure; ignored when existing axes are supplied. |
| `ax` | Optional existing Matplotlib `Axes`; its figure is returned. |
| `axes` | Optional pair `(fit_axes, residual_axes)` of distinct axes in the same figure. |
| `label` | Label for the data artist. |
| `color` | Matplotlib color for the data artist. |
| `marker` | Matplotlib marker for the data artist. |
| `degree` | Positive integer polynomial degree; defaults to `1`. A fit requires at least `degree + 1` distinct x values. |
| `yerr` in fit functions | Positive finite scalar or one-dimensional sequence of y standard uncertainties, used to weight the fit and draw error bars. When omitted, uncertainty is inferred from `y` if available. |
| `fit_color` | Matplotlib color for the fitted curve, default `"C1"`. |
| `label_slope` | When `True`, label the fit with the coefficient of the x term; otherwise use the degree. For nonlinear fits that coefficient is not the slope at every point. |

## `line_plot`

```text
line_plot(x, y, title=None, xlabel=None, ylabel=None, filename=None,
          save_directory=None, show=False, figsize=(8, 5), *, ax=None,
          label=None, color=None, marker=None, linestyle="-")
```

Draw a connected line. See the [shared parameters](#shared-parameters);
`linestyle` is a Matplotlib line style. Measurement values are used, not their
uncertainties.

**Returns:** the new or existing `Figure`.

```python
from labplotlib import line_plot

fig = line_plot([0, 1, 2], [1, 3, 5], xlabel="Time (s)", ylabel="Distance (m)")
```

## `scatter_with_fit`

```text
scatter_with_fit(x, y, degree=1, title=None, xlabel=None, ylabel=None,
                 filename=None, save_directory=None, show=False,
                 label_slope=True, figsize=(8, 5), *, ax=None, yerr=None,
                 label="data", color=None, fit_color="C1", marker="o")
```

Plot observations and a polynomial fit. See the
[shared parameters](#shared-parameters). Explicit `yerr` overrides inferred
measurement uncertainty. The function adds a legend. See
[`polynomial_fit`](methods.md) for the
weighting and statistics.

**Returns:** the new or existing `Figure`.

```python
from labplotlib import scatter_with_fit

fig = scatter_with_fit([0, 1, 2], [1, 3, 5], yerr=0.2, ylabel="Distance (m)")
```

## `errorbar_plot`

```text
errorbar_plot(x, y, yerr=None, xerr=None, title=None, xlabel=None, ylabel=None,
              filename=None, save_directory=None, show=False, figsize=(8, 5),
              *, ax=None, label=None, color=None, marker="o", capsize=3)
```

Plot observations with optional x and y error bars. See the
[shared parameters](#shared-parameters).

| Parameter | Meaning |
| --- | --- |
| `xerr`, `yerr` | Optional finite, non-negative scalar, length-N sequence, or 2-by-N array of lower and upper errors. When omitted, uncertainty is inferred from the corresponding measurement data if available. |
| `capsize` | Error-bar cap size in points; defaults to `3`. |

**Returns:** the new or existing `Figure`. Invalid error shapes or negative
errors raise `ValueError`.

```python
from labplotlib import Measurement, errorbar_plot

distance = Measurement([1, 3, 5], [0.1, 0.2, 0.1])
fig = errorbar_plot([0, 1, 2], distance, xlabel="Time (s)")
```

## `scatter_with_residuals`

```text
scatter_with_residuals(x, y, degree=1, title=None, xlabel=None, ylabel=None,
                       filename=None, save_directory=None, show=False,
                       label_slope=True, figsize=(8, 7), *, axes=None,
                       yerr=None, label="data", color=None, fit_color="C1",
                       marker="o")
```

Draw a polynomial fit above residuals (`observed - predicted`). See the
[shared parameters](#shared-parameters). New axes share the x axis and use
a 3:1 height ratio. When uncertainties are supplied, the lower panel shows
the supplied measurement uncertainties, not fitted-residual uncertainties.

**Returns:** the new or existing `Figure`. Invalid `axes` pairs raise
`ValueError`.

```python
from labplotlib import scatter_with_residuals

fig = scatter_with_residuals([0, 1, 2], [1.1, 2.9, 5.2], yerr=0.2,
                             xlabel="Time (s)", ylabel="Distance (m)")
```
