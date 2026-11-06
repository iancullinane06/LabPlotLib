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
mapping containing symbol names that include `name_part`.

Importing `labplotlib.Styling` applies the library's Seaborn plotting theme.

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
