# Electronics analysis

```python
from labplotlib import (
    gain_to_db, cutoff_frequency, cutoff_frequencies, rolloff_slope, resonance,
    time_constant, rise_time, phase_from_delay, time_delay, phase_difference,
    phase_from_lissajous,
)
```

Helpers for typical electronics-lab measurements. Frequency-response helpers
take frequencies in any consistent unit; all frequencies must be positive.
See [`bode_plot`](plotting.md) to display frequency-response data.

## Frequency response

### `gain_to_db(gain)`

Convert a linear amplitude ratio (for example `Vout / Vin`) to decibels,
`20·log10(gain)`. **Returns:** a `Measurement` whose uncertainty is propagated
from the input's. Non-positive gains raise `ValueError`.

### `cutoff_frequency(frequency, gain_db, *, reference_db=None, drop_db=3.0103, which="first")`

The frequency at which the gain falls `drop_db` below `reference_db` (the −3 dB
point). The reference defaults to the maximum gain. Crossings are found by
interpolating dB linearly against log-frequency.

| Parameter | Meaning |
| --- | --- |
| `reference_db` | Passband gain in dB. Set it when the maximum is not the passband (for example when the response has a resonant peak). |
| `drop_db` | Drop below the reference; the default is the exact half-power value, `10·log10(2)`. |
| `which` | `"first"` or `"last"` crossing when there are several. |

**Returns:** the frequency as a `float`. Raises `ValueError` if the gain never
crosses the level. `cutoff_frequencies(...)` takes the same arguments (except
`which`) and returns every crossing as an array, which is what a band-pass
filter needs (a lower and an upper cutoff).

### `rolloff_slope(frequency, gain_db, f_min, f_max)`

Slope of the stop-band in dB per decade, from a straight-line fit of dB against
`log10(frequency)` using points with `f_min <= frequency <= f_max` (at least
three distinct frequencies). **Returns:** a `Measurement` in `"dB/decade"`
whose uncertainty is the standard error of the slope. A first-order filter
gives about −20 dB/decade and a second-order filter about −40.

### `resonance(frequency, response, *, level=1/sqrt(2))`

Resonant frequency and quality factor of a peak in a **linear amplitude**
response (not dB). The peak is refined by a parabola through its three highest
points. The bandwidth is the distance between the points either side where the
response falls to `level` times the peak (1/√2 for half power), and
`Q = frequency / bandwidth`.

**Returns:** a `Resonance` with `frequency`, `peak`, `lower`, `upper`,
`bandwidth` and `q_factor`. If the response does not fall to the level on both
sides within the data, `bandwidth` and `q_factor` are `None`. For noisy data,
fit a [`lorentzian`](fitting.md) instead and use `Q = center / width`.

```python
import numpy as np
from labplotlib import cutoff_frequency, gain_to_db, resonance, rolloff_slope

f = np.logspace(1, 5, 60)
gain = 1 / np.sqrt(1 + (f / 1500) ** 2)             # first-order low-pass
print(cutoff_frequency(f, gain_to_db(gain).value))   # about 1500
print(rolloff_slope(f, gain_to_db(gain).value, 15_000, 100_000))
```

## Transient response

### `time_constant(t, y, *, kind="decay", yerr=None, p0=None)`

Fit an RC exponential. `kind="decay"` uses `exponential_decay` and
`kind="rise"` uses `exponential_rise`. **Returns:** the
[`ModelFit`](fitting.md#modelfit); read the time constant with
`fit.parameter("tau")`, a `Measurement` with its uncertainty.

### `rise_time(t, y, low=0.1, high=0.9, *, initial=None, final=None)`

Time for a step to go from `low` to `high` of its swing (10–90% by default),
by interpolation. It also gives the fall time of a falling edge. `initial` and
`final` default to the median of the first and last tenth of the samples; set
them explicitly for noisy or short records. **Returns:** the time as a
`float`. For a first-order RC circuit the 10–90% rise time is `τ·ln 9 ≈ 2.2 τ`.
Raises `ValueError` if the signal never reaches a level.

```python
from labplotlib import rise_time, time_constant

fit = time_constant(t, v, kind="rise", yerr=0.02)
tau = fit.parameter("tau")
print(tau.to_string(uncertainty_digits=1, unit="s", prefix="auto"))
print(rise_time(t, v))
```

## Phase

### `phase_from_delay(delay, frequency)`

Phase lag in degrees, `360·frequency·delay`. Plain numbers and `Measurement`
values are accepted, and uncertainties are propagated. **Returns:** a
`Measurement` with unit `"°"`.

### `time_delay(time, a, b)`

Delay of signal `b` relative to `a` (positive when `b` lags), found by
cross-correlating the mean-subtracted, Hann-windowed signals with sub-sample
refinement. The time axis must be uniformly sampled. **Returns:** seconds (in
the units of `time`) as a `float`. For a short record of a sinusoid the finite
window biases the result by a few percent of a period (about 4 periods), so
prefer `phase_difference` for sinusoids at a known frequency.

### `phase_difference(time, a, b, frequency)`

Phase lag of `b` behind `a` in degrees, in (−180, 180], for sinusoids at a
known `frequency`. Each signal is least-squares fitted with an offset, sine and
cosine at that frequency, so offsets, partial periods and noise are handled
exactly. The time axis need not be uniform.

### `phase_from_lissajous(x, y)`

Phase difference, 0 to 180 degrees, between two sinusoids of the same frequency
from the XY (Lissajous) figure. An ellipse is fitted to the points and
`cos(phase) = −b / (2√(ac))` is read from its coefficients; offsets and partial
traces are handled. The sign of the phase cannot be recovered from the figure.
Raises `ValueError` if the points do not trace an ellipse.

```python
from labplotlib import phase_difference, phase_from_delay, phase_from_lissajous
from labplotlib import Measurement

print(phase_difference(t, ch1, ch2, 1000.0))           # degrees, signed
print(phase_from_lissajous(ch1, ch2))                   # degrees, 0 to 180
print(phase_from_delay(Measurement(1e-4, 1e-6), 1000))  # 36.000 ± 0.360 °
```
