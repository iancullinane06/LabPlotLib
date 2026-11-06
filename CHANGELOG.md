# Changelog

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
