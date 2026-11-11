# Changelog

## 0.10.0

### Added
- `scatter_with_bands()` draws a linear fit with pointwise confidence and
  prediction bands. Both default to 95% coverage, which can be adjusted.
  Bands can use measurement uncertainties or supplied uncertainties, and
  `fit_range` can extend the fit beyond the data.

## 0.9.0

### Added
- `fit_model()` fits any `model(x, *params)` with uncertainties, χ², reduced χ²
  and p-value; built-in `exponential_decay`, `exponential_rise`, `lorentzian`,
  `gaussian`, `power_law` and `diode` models guess their own start values.
- `scatter_with_fit()` and `scatter_with_residuals()` accept `model`, `p0`,
  `show_stats`, `xerr`, `xscale` and `yscale`; `annotate_fit()` adds a
  statistics box.
- `bode_plot()` draws gain in dB with phase on a twin axis.
- Electronics helpers: `cutoff_frequency`, `rolloff_slope`, `resonance`,
  `time_constant`, `rise_time`, `phase_from_delay`, `time_delay`,
  `phase_difference`, `phase_from_lissajous`.
- `Measurement` gains `apply()`, `sin`/`cos`/`tan`/`arcsin`/`arccos`/`arctan`/
  `exp`/`log`/`log10`/`sqrt` in `labplotlib.measurement` with error propagation,
  `prefix="auto"` and `uncertainty_digits` in `to_string()`.
- `PolynomialFit` gains `p_value` and `dof`.

### Changed
- `scatter_with_fit()` draws and uses `Measurement` uncertainties by default;
  pass `use_errors=False` to disable.

## 0.8.0

### Added
- `scatter_plot()` colours points by a third variable `c`, with `cmap`,
  `colorbar`, `colorbar_label`, `vmin`, and `vmax` options.
- `get_cmap()` resolves Seaborn/Matplotlib colormap names; the default is
  `"crest"`, with `"flare"` and `"Spectral"` recommended.
- `add_colorbar()` attaches a labelled colourbar to an axes.

### Changed
- Fit plots colour the data and its fit with the same hue (fit paler). On shared
  axes each new dataset takes the next colour in the cycle. `fit_color` now
  defaults to `None` instead of `"C1"`.

## 0.6.0

### Added
- `Measurement.to_string()` supports raw, automatic, and scientific formats,
  optional units, and SI prefixes that rescale display only. Automatic format
  uses decimal notation for magnitudes from 10⁻³ up to (but not including)
  10³, and scientific notation outside that range.
- Measurement strings round to three decimal places by default; override this
  with `decimals=` or disable rounding with `decimals=None`.
- `Measurement.set_unit()` stores display-only unit and SI-prefix metadata,
  which is included by `str()` and never changes arithmetic.
- `Measurement.mean()` combines the sample standard error with independently
  propagated individual measurement uncertainties in quadrature.

## 0.5.0

### Added
- `Measurement` instances now print their value and, when available, their
  uncertainty.

## 0.4.0

### Changed
- Plotting helpers are now provided by `labplotlib.plotting` instead of
  `labplotlib.plots`.
- Fit plots can label the fit by slope or polynomial degree; residual plots
  use a taller figure with more space for the fit than the residual panel.

## 0.3.0

### Changed
- Plotting functions and `finish_plot` no longer show figures by default.
- Plotting functions no longer apply a global theme. Call `apply_theme`
  explicitly to opt in. When no save or show is requested, plot functions
  leave layout and finalization to the caller.
- Axis styling leaves unspecified labels unchanged.

### Added
- Existing axes can be supplied for composable plots, including a pair of axes
  for `scatter_with_residuals`.
- `polynomial_fit` provides fit coefficients, residuals, R², and chi-squared
  statistics, with optional weighting by y uncertainties.
- Plot labels, colors, markers, and save DPI can be customized.
- `Measurement` supports supplied absolute/relative uncertainties, sample
  standard deviations, quadrature propagation, and pandas columns.

## 0.2.0

### Changed (breaking)
- Modules renamed to lowercase: `labplotlib.styling` and `labplotlib.symbols`.
- Importing the package no longer changes global matplotlib state; call
  `apply_theme()` (plot functions do this automatically).
- Symbol `"+/-"` renamed to `"plus_minus"`; `"approximately_equal_to"` is now
  `≈` (the former `≅` is `"congruent_to"`); `"set_universal"` is now `𝕌`;
  `"multiplication"` is now `×`.
- `search` is now case-insensitive.

### Added
- Public plotting API: `line_plot`, `scatter_with_fit`, `errorbar_plot`,
  `style_axis`, `finish_plot`, `apply_theme`.
- `finish_plot` can skip saving/showing, creates the save directory, and
  returns the figure.
- `py.typed` marker, MIT license, project URLs, tests and CI.

### Fixed
- `print_symbols` no longer fails on multi-character symbols and pads hex
  escapes correctly.

## 0.1.0
- Initial release.
