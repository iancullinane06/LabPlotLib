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
