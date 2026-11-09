# Styling and finalising figures

```python
from labplotlib import apply_theme, style_axis, finish_plot, get_cmap, add_colorbar
```

## `apply_theme()`

Apply the library's Seaborn dark-grid theme globally, including a light gray
axes background. Importing LabPlotLib and calling its plotting functions do not
apply this theme automatically.

**Parameters:** none. **Returns:** `None`.

```python
from labplotlib import apply_theme

apply_theme()  # changes global Matplotlib styling
```

## `style_axis(ax, title=None, xlabel=None, ylabel=None)`

Set a title and/or axis labels on an existing Matplotlib axes.

| Parameter | Meaning |
| --- | --- |
| `ax` | Matplotlib `Axes` to style. |
| `title` | Optional title, styled bold at size 14; `None` leaves it unchanged. |
| `xlabel`, `ylabel` | Optional x and y labels; `None` leaves each unchanged. |

**Returns:** `None`.

```python
import matplotlib.pyplot as plt
from labplotlib import style_axis

fig, ax = plt.subplots()
style_axis(ax, title="Experiment", xlabel="Time (s)", ylabel="Distance (m)")
```

## `finish_plot(fig, filename=None, save_directory=None, show=False, *, dpi=None)`

Apply `tight_layout()`, optionally save and/or show the figure, and return it.

| Parameter | Meaning |
| --- | --- |
| `fig` | Matplotlib `Figure` to finalize. |
| `filename` | Optional string or `Path` for the output file. No file is saved if `None`. |
| `save_directory` | Optional base directory; defaults to the current working directory. Created along with any needed parent directories when saving. |
| `show` | Show figures via `matplotlib.pyplot.show()` when `True`; defaults to `False`. |
| `dpi` | Optional resolution passed to `fig.savefig`; used only when saving. |

**Returns:** the same `Figure`. Saving and layout errors propagate to the
caller.

```python
from labplotlib import finish_plot, line_plot

fig = line_plot([0, 1, 2], [1, 3, 5])
finish_plot(fig)  # layout only; add filename="plot.png" to save
```

## Colormaps and colourbars

Colour-mapped plots such as [`scatter_plot`](plotting.md) default to Seaborn's
`"crest"`. Recommended maps:

| Map | Use for |
| --- | --- |
| `"crest"` (default, `DEFAULT_CMAP`) | Sequential data. |
| `"flare"` | Sequential data, warm tones. |
| `"Spectral"` (`DIVERGING_CMAP`) | Data centred on a meaningful midpoint, such as residuals. |

Any Seaborn or Matplotlib name works, including reversed forms such as
`"crest_r"`, as does a `Colormap` object.

### `get_cmap(cmap=None)`

Resolve a name or `Colormap` to a `Colormap` through
`seaborn.color_palette(..., as_cmap=True)`. `None` returns the default
(`"crest"`). Unknown names raise `ValueError`.

### `add_colorbar(fig, ax, mappable, label=None)`

Attach a colourbar for `mappable` (for example the return value of
`ax.scatter(..., c=...)`) to `ax`, optionally labelled, and return the
`Colorbar`. Call it before `finish_plot` so the layout leaves room for it.

```python
import matplotlib.pyplot as plt
from labplotlib import add_colorbar, finish_plot, get_cmap

fig, ax = plt.subplots()
points = ax.scatter([0, 1, 2], [1, 3, 5], c=[-1, 0, 1], cmap=get_cmap("Spectral"))
add_colorbar(fig, ax, points, label="Residual")
finish_plot(fig)
```

