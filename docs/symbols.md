# Mathematical symbols

```python
from labplotlib import print_symbols, search, symbols
```

## `symbols`

A read-only mapping from descriptive names to Unicode strings. Some values,
such as `"degree_celsius"`, contain more than one character.

```python
from labplotlib import symbols

print(symbols["sigma"])   # σ
print(symbols["squared"]) # ²
```

## `search(namelike)`

Find symbols whose names contain a substring, without case sensitivity.

| Parameter | Meaning |
| --- | --- |
| `namelike` | String to search for in symbol names. An empty string matches every name. |

**Returns:** a read-only mapping of matching names to symbol strings; it may
be empty.

```python
from labplotlib import search

print(dict(search("sigma")))  # {'sigma': 'σ'}
```

## `print_symbols(symbols_to_print=symbols)`

Print names, symbol values, and their decimal and hexadecimal Unicode code
points.

| Parameter | Meaning |
| --- | --- |
| `symbols_to_print` | Mapping of names to symbol strings; defaults to all library symbols. |

**Returns:** `None`; writes to standard output.

```python
from labplotlib import print_symbols, search

print_symbols(search("sigma"))
```
