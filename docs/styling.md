# Styling and finalizing figures

```python
from labplotlib import apply_theme, style_axis, finish_plot
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
