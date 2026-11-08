# LabPlotLib

LabPlotLib helps with common physics-lab tasks: plotting measurements and
error bars, fitting polynomials, inspecting residuals, propagating independent
uncertainties, and finding mathematical symbols. It builds on NumPy,
Matplotlib, Seaborn, and SciPy.

## Installation

Install a published version from PyPI:

```powershell
python -m pip install labplotlib
```

The examples below describe the current source checkout; a published version
may not yet contain all these features. To install the checkout instead, run
this command from the project directory:

```powershell
python -m pip install .
```

For development, install it in editable mode:

```powershell
python -m pip install -e .
```

## Plotting

```python
import matplotlib.pyplot as plt
from labplotlib import errorbar_plot, finish_plot, polynomial_fit, scatter_with_residuals

time = [0, 1, 2, 3]                   # seconds
position = [0.1, 2.0, 4.2, 5.9]     # metres
uncertainty = [0.2, 0.2, 0.3, 0.2]   # standard deviations, metres

fig, ax = plt.subplots()
errorbar_plot(time, position, yerr=uncertainty, ax=ax, label="measurements",
              xlabel="Time (s)", ylabel="Position (m)")
ax.legend()
finish_plot(fig, "position.png", "plots", dpi=300, show=True)

fit = polynomial_fit(time, position, yerr=uncertainty)
print("Gradient and intercept:", fit.coefficients)
print("Reduced chi-squared:", fit.reduced_chi_squared)
fig = scatter_with_residuals(time, position, yerr=uncertainty,
                             xlabel="Time (s)", ylabel="Position (m)")
finish_plot(fig, "fit-and-residuals.pdf", "plots")
plt.close(fig)
```

`line_plot`, `errorbar_plot`, and `scatter_with_fit` accept an optional `ax`;
`scatter_with_residuals` accepts `axes=(main_ax, residual_ax)`. They create
axes if none are supplied and return the `Figure`. Call `finish_plot` when
ready to arrange, save, and optionally show the entire figure. No figure is
shown by default. The older `filename`, `save_directory`, and `show` arguments
on the plotting functions still work for one-step use.

Plotting does not change global Matplotlib settings. Call `apply_theme()`
explicitly *before* creating figures if you want the library's global Seaborn
theme. Use Matplotlib axes methods for scales, limits, and other customization.
Add units to axis labels as shown above.

### Plot types and styling

| Function | What it draws |
| --- | --- |
| `line_plot(x, y)` | Data connected by a line. |
| `errorbar_plot(x, y, xerr=..., yerr=...)` | Points with optional x and y error bars. |
| `scatter_with_fit(x, y, degree=1, yerr=...)` | Points and a polynomial fit. |
| `scatter_with_residuals(x, y, degree=1, yerr=...)` | A fit and a second axes showing residuals. |

These functions accept equal-length, finite, one-dimensional data, including
NumPy arrays and numeric pandas Series. `errorbar_plot` accepts scalar,
per-point, or asymmetric errors: for asymmetric errors, pass a 2-by-N array
of lower and upper error magnitudes. Fit `yerr` values must instead be
positive scalars or per-point standard uncertainties.

For example, overlay two data series and adjust the axes before finishing:

```python
import matplotlib.pyplot as plt
from labplotlib import apply_theme, errorbar_plot, finish_plot, line_plot, style_axis

apply_theme()  # Optional: changes global Matplotlib settings.
fig, ax = plt.subplots(figsize=(8, 5))
line_plot([1, 2, 3], [2, 4, 6], ax=ax, label="model", linestyle="--")
errorbar_plot([1, 2, 3], [2.1, 3.9, 6.2], yerr=0.2, ax=ax,
              label="measurements", marker="o", capsize=4)
style_axis(ax, title="Position over time", xlabel="Time (s)", ylabel="Position (m)")
ax.legend()
finish_plot(fig, "comparison.png", "plots", dpi=300)
plt.close(fig)
```

`style_axis` leaves labels unchanged when they are omitted. `finish_plot`
applies a tight layout, creates missing save directories, and returns the
figure. It does not show or close the figure by default; use `show=True` to
show it and `plt.close(fig)` when you are finished with it.

### Fit results

`polynomial_fit` returns coefficients in descending power order, residuals
(`observed - predicted`), unweighted R², and, when `yerr` is supplied,
chi-squared and reduced chi-squared. Fits minimize squared residuals divided
by `yerr**2`: use independent, positive one-standard-deviation uncertainties,
not variances. Reduced chi-squared requires more measurements than fitted
parameters; it and R² are `None` when undefined. Fits do not account for
uncertainties in x, correlated errors, or systematic errors. Residual error
bars display the supplied measurement uncertainties, not fitted-residual
uncertainties. A good R² alone does not establish that a model is appropriate.

```python
from labplotlib import polynomial_fit

result = polynomial_fit([0, 1, 2, 3], [0.1, 2.0, 4.2, 5.9],
                        degree=1, yerr=[0.2, 0.2, 0.3, 0.2])
slope, intercept = result.coefficients
print("Slope:", slope, "intercept:", intercept)
print("Residuals:", result.residuals)
print("R²:", result.r_squared)
print("Chi-squared:", result.chi_squared)
print("Reduced chi-squared:", result.reduced_chi_squared)
```

For degree `d`, the fit needs at least `d + 1` distinct x values. The default
degree is 1, so the first coefficient is the gradient and the second is the
intercept. Without `yerr` the fit is unweighted and both chi-squared fields
are `None`.

## Measurements and uncertainty

`Measurement` stores a value (or array of values) and optional **absolute
standard uncertainty**. Use `from_pm` when uncertainties are known, or
`from_stdev` for repeated observations:

```python
from labplotlib import Measurement

length = Measurement.from_pm(2.0, 0.1, relative=0.02, granularity=0.01)
time = Measurement.from_stdev([1.2, 1.3, 1.4], mean_error=True)
speed = length / time
print(speed.value, speed.uncertainty, speed.relative_uncertainty())
```

`relative` is a fraction (`0.02` means 2%). Absolute, relative and
granularity contributions are combined in quadrature. Supply `granularity`
as an **absolute standard uncertainty**, not automatically as a raw instrument
resolution: convert the resolution to a standard uncertainty using an
appropriate distribution first. `from_stdev` uses sample standard deviation
(`ddof=1`); `mean_error=True` uses the standard error of the mean instead.
Granularity is combined afterward and is not reduced by the number of readings.

Use arrays for a series of measurements, or leave uncertainty unspecified:

```python
from labplotlib import Measurement

positions = Measurement.from_pm([1.0, 2.0, 3.0], [0.1, 0.1, 0.2])
unmeasured = Measurement.from_pm([1.0, 2.0, 3.0])
print(positions.value, positions.uncertainty)
print(unmeasured.uncertainty)  # None
```

Both `value` and `uncertainty` are NumPy arrays, including zero-dimensional
arrays for scalar values. `from_stdev` requires at least two observations;
pass `axis=0` or `axis=1` to summarise repeated readings in a 2D array along
the chosen axis.

Arithmetic (`+`, `-`, `*`, `/`, and powers) uses first-order propagation in
quadrature and assumes independent input uncertainties. Correlated quantities,
including repeated use of the same measurement, require a covariance-aware
analysis instead. Missing uncertainties stay `None` when none are supplied;
when combining an uncertain value with one without an uncertainty, only the
supplied contribution is included. This does not establish that the other
measurement is exact. Relative uncertainty is undefined for zero values.

### CSV and pandas

Read a CSV with pandas and pass its numeric columns directly to the plotters,
or associate a value column with absolute and/or fractional error columns:

For example, `experiment.csv` might contain:

```csv
time,distance,distance_error
0,0.1,0.2
1,2.0,0.2
2,4.2,0.3
3,5.9,0.2
```

```python
import pandas as pd
from labplotlib import Measurement, scatter_with_residuals, finish_plot

data = pd.read_csv("experiment.csv")
distance = Measurement.from_dataframe(data, "distance", uncertainty="distance_error")
fig = scatter_with_residuals(data["time"], distance,
                             xlabel="Time (s)", ylabel="Distance (m)")
finish_plot(fig, "experiment.pdf")
```

Here, the column names are supplied to `from_dataframe`; use `relative="name"`
for a column of fractional uncertainties, and optionally pass both
`uncertainty` and `relative` to combine them. The CSV example needs pandas,
which can be installed with `python -m pip install pandas`.

`errorbar_plot` automatically uses uncertainties on `Measurement` x and y
values. `scatter_with_fit`, `scatter_with_residuals`, and `polynomial_fit`
automatically use y uncertainties for weighting; explicit `yerr` overrides
them. Ordinary numeric pandas Series work without a `Measurement`. A Series
of scalar `Measurement` objects is also supported; its uncertainties must
either all be supplied or all be absent. `line_plot` uses the values only.

```python
import pandas as pd
from labplotlib import Measurement, errorbar_plot

readings = pd.Series([Measurement.from_pm(1.0, 0.1),
                      Measurement.from_pm(2.0, 0.2)])
fig = errorbar_plot(pd.Series([0, 1]), readings, xlabel="Time (s)", ylabel="Length (m)")
```

## Additional analysis helpers

These functions are available from `labplotlib.methods`:

```python
import numpy as np
from labplotlib.methods import chi_squared, reduced_chi_squared, p_value_chi_squared, k_means

observed = [1.1, 1.9, 3.2]
expected = [1.0, 2.0, 3.0]
errors = [0.2, 0.2, 0.2]
dof = 2  # Set this for your model and fitted parameters.
print(chi_squared(observed, expected, errors))
print(reduced_chi_squared(observed, expected, errors, dof))
print(p_value_chi_squared(observed, expected, errors, dof))

points = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]])
centroids, labels = k_means(points, k=1)
```

For chi-squared, provide matching numeric arrays and positive standard
uncertainties, and use a positive number of degrees of freedom. The p-value
uses the chi-squared distribution. For `k_means`, provide a two-dimensional
NumPy array with one sample per row and `1 <= k <=` the number of samples.
Centroids are initialized randomly; results can vary and empty clusters can
produce invalid centroids. Inspect the result before drawing conclusions.

## Symbol utilities

```python
from labplotlib import print_symbols, search, symbols

print(symbols["pm"])
print(search("fraction"))
print_symbols(search("fraction_one"))
```

`symbols` and the mapping returned by `search(name_part)` are read-only.
Search matches names case-insensitively. `print_symbols()` prints all symbols;
pass a mapping to print a selection with its decimal and hexadecimal code points.

## Development

Ruff is an optional code linter; it is not required to use or publish the
library. Twine is a separate tool for checking and uploading distributions.

```powershell
python -m pip install -e ".[dev]"
ruff check .
python -m unittest discover -s tests
```

The version lives in `src/labplotlib/__init__.py`; see
[CHANGELOG.md](CHANGELOG.md) for release notes.

## Publishing

To publish manually with Twine, update the version in
`src/labplotlib/__init__.py`, then build and check the distributions:

```powershell
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

Ensure `dist/` contains only the distributions for the version being
released. When prompted, use `__token__` as the username and your PyPI API
token as the password; don't commit or share the token. PyPI does not allow
uploading the same distribution version again.

Alternatively, the GitHub Actions workflow publishes when a GitHub Release is
published. To use it, configure a PyPI trusted publisher for this repository:

- Owner and repository: the values for this GitHub project
- Workflow: `.github/workflows/publish.yml`
- Environment: `pypi`

Then push the version change and publish a GitHub Release with a matching
version tag. The workflow runs the tests, builds the distributions, and
publishes them without requiring a PyPI API token in GitHub secrets. Choose
either the manual upload or the workflow for a given release, not both.
