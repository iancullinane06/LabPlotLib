# Changelog

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
