# LabPlotLib reference

This reference describes the LabPlotLib 0.8.0 API. Each page covers one
module, with examples, parameters, and return values.

| Module | What it covers |
| --- | --- |
| [measurement](measurement.md) | Values, uncertainties, arithmetic, physics functions, and formatting |
| [plotting](plotting.md) | Line plots, fits, error bars, residuals, and Bode plots |
| [fitting](fitting.md) | Arbitrary model fits with χ², p-values, and built-in electronics models |
| [electronics](electronics.md) | Cutoff, roll-off, resonance, time constants, rise time, and phase |
| [methods](methods.md) | Polynomial fits, fit statistics, and clustering |
| [styling](styling.md) | Theme, axes, figure layout, saving, and showing |
| [symbols](symbols.md) | Mathematical symbol lookup and printing |

Most frequently used names are available directly from `labplotlib`. Other
functions shown with module imports are available from their respective modules.
See the [measurement example](../examples/measurement_formatting.py) for a
complete runnable program, and the [speed-of-sound example](../examples/speed_of_sound.py)
for a DataFrame-based calculation of a mean with uncertainty.

## Conventions

- Parameters after `*` in a signature must be supplied by keyword.
- Plotting helpers return a Matplotlib `Figure`; they do not call `show()` by
  default. When neither saving nor showing, they leave figure layout to the
  caller.
- A `Measurement` stores a value and an optional **absolute standard
  uncertainty**. Its units are display metadata, not dimensional analysis or
  unit conversion.
- Examples assume LabPlotLib is installed. DataFrame examples additionally
  require pandas.
