# LabPlotLib

LabPlotLib is a small Python library containing plotting-style helpers and a
searchable collection of mathematical symbols.

## Installation

Install the latest source checkout with pip:

```powershell
python -m pip install .
```

For development, install it in editable mode:

```powershell
python -m pip install -e .
```

## Symbol utilities

```python
from labplotlib import print_symbols, search, symbols

print(symbols["set_union"])
print(search("fraction"))
print_symbols(search("fraction_one"))
```

The `symbols` mapping is read-only. `search(name_part)` returns a read-only
mapping of symbol names containing `name_part` (case-insensitive).

## Plotting

```python
from labplotlib import errorbar_plot, line_plot, scatter_with_fit

line_plot([1, 2, 3], [1, 4, 9], title="Squares", xlabel="x", ylabel="y")
scatter_with_fit(x, y, degree=1, filename="fit.png", save_directory="plots")
errorbar_plot(x, y, yerr=err, show=False)  # returns the matplotlib Figure
```

Each function returns the `Figure`. Pass `filename` (and optionally
`save_directory`, created if missing) to save, and `show=False` to skip
`plt.show()`. Importing the package does not change global matplotlib
settings; the plot functions apply the Seaborn theme via `apply_theme()`, which
you can also call yourself. Lower-level helpers `style_axis` and `finish_plot`
are public too.

## Development

```powershell
python -m pip install -e ".[dev]"
ruff check .
python -m unittest discover -s tests
```

The version lives in `src/labplotlib/__init__.py`; see
[CHANGELOG.md](CHANGELOG.md) for release notes.

## Publishing

Publishing is automated when a GitHub Release is published. Configure a PyPI
trusted publisher for this repository with:

- Owner and repository: the values for this GitHub project
- Workflow: `.github/workflows/publish.yml`
- Environment: `pypi`

Then update the version in `pyproject.toml`, push the change, and create a
GitHub Release with a matching version tag (for example, `v0.1.1`). The
workflow runs the tests, builds the distributions, and publishes them without
requiring a PyPI API token in GitHub secrets.
