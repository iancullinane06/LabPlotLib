"""Analysis helpers for electronics laboratory data."""

from dataclasses import dataclass
from typing import Any, Literal, Optional, Sequence

import numpy as np
from scipy.signal import fftconvolve

from .fitting import ModelFit, exponential_decay, exponential_rise, fit_model
from .measurement import Measurement, log10, unpack_measurements
from .methods import Errors, _data

HALF_POWER_DB = 10 * np.log10(2)


def gain_to_db(gain: Any) -> Measurement:
    """Convert a linear amplitude ratio (e.g. Vout / Vin) to dB, propagating uncertainty."""
    values, errors = unpack_measurements(gain)
    return 20 * log10(Measurement(values, errors))


def _sorted_positive_frequency(frequency: Sequence[float], response: Sequence[float]):
    f, r = _data(frequency, response)
    if np.any(f <= 0):
        raise ValueError("frequency must be positive")
    order = np.argsort(f)
    return f[order], r[order]


def cutoff_frequencies(
    frequency: Sequence[float],
    gain_db: Sequence[float],
    *,
    reference_db: Optional[float] = None,
    drop_db: float = HALF_POWER_DB,
) -> np.ndarray:
    """Every frequency where the gain crosses ``reference_db - drop_db`` (the -3 dB points).

    The reference defaults to the maximum gain. Crossings are found by interpolating
    linearly in dB against log-frequency.
    """
    f, g = _sorted_positive_frequency(frequency, gain_db)
    reference = float(np.max(g)) if reference_db is None else float(reference_db)
    shifted = g - (reference - drop_db)
    log_f = np.log10(f)
    crossings = []
    for i in range(f.size):
        if shifted[i] == 0:
            crossings.append(f[i])
        if i + 1 < f.size and shifted[i] * shifted[i + 1] < 0:
            fraction = shifted[i] / (shifted[i] - shifted[i + 1])
            crossings.append(10 ** (log_f[i] + fraction * (log_f[i + 1] - log_f[i])))
    return np.array(crossings, dtype=float)


def cutoff_frequency(
    frequency: Sequence[float],
    gain_db: Sequence[float],
    *,
    reference_db: Optional[float] = None,
    drop_db: float = HALF_POWER_DB,
    which: Literal["first", "last"] = "first",
) -> float:
    """The -3 dB frequency; ``which`` picks the first or last crossing when there are several."""
    if which not in ("first", "last"):
        raise ValueError("which must be 'first' or 'last'")
    crossings = cutoff_frequencies(frequency, gain_db, reference_db=reference_db, drop_db=drop_db)
    if crossings.size == 0:
        raise ValueError("the gain never crosses the cutoff level")
    return float(crossings[0] if which == "first" else crossings[-1])


def rolloff_slope(
    frequency: Sequence[float],
    gain_db: Sequence[float],
    f_min: float,
    f_max: float,
) -> Measurement:
    """Slope in dB per decade from a straight-line fit of dB against log10(frequency).

    Only points with ``f_min <= frequency <= f_max`` are used (at least three).
    The uncertainty is the standard error of the fitted slope.
    """
    f, g = _sorted_positive_frequency(frequency, gain_db)
    chosen = (f >= f_min) & (f <= f_max)
    if chosen.sum() < 3 or np.unique(f[chosen]).size < 3:
        raise ValueError("at least three distinct frequencies are needed in the chosen range")
    coefficients, covariance = np.polyfit(np.log10(f[chosen]), g[chosen], 1, cov=True)
    return Measurement(coefficients[0], np.sqrt(covariance[0, 0]), unit="dB/decade")


@dataclass(frozen=True)
class Resonance:
    """Peak location and half-power bandwidth; bandwidth and Q are None if not bracketed."""

    frequency: float
    peak: float
    bandwidth: Optional[float]
    q_factor: Optional[float]
    lower: Optional[float]
    upper: Optional[float]


def resonance(
    frequency: Sequence[float],
    response: Sequence[float],
    *,
    level: float = 1 / np.sqrt(2),
) -> Resonance:
    """Resonant frequency and Q factor of a peak in a linear amplitude response.

    The bandwidth is measured between the points where the response falls to
    ``level`` times the peak (1/√2 for half power) and Q = frequency / bandwidth.
    """
    if not 0 < level < 1:
        raise ValueError("level must be between 0 and 1")
    f, r = _sorted_positive_frequency(frequency, response)
    i = int(np.argmax(r))
    centre, peak = float(f[i]), float(r[i])
    if 0 < i < f.size - 1:
        a, b, c = np.polyfit(f[i - 1:i + 2], r[i - 1:i + 2], 2)
        vertex = -b / (2 * a) if a < 0 else centre
        if f[i - 1] <= vertex <= f[i + 1]:
            centre, peak = float(vertex), float(np.polyval([a, b, c], vertex))
    target = peak * level

    def edge(indices: range) -> Optional[float]:
        for j in indices:
            if r[j] < target:
                k = j + 1 if indices.step < 0 else j - 1
                return float(f[j] + (target - r[j]) * (f[k] - f[j]) / (r[k] - r[j]))
        return None

    lower = edge(range(i, -1, -1))
    upper = edge(range(i, f.size))
    if lower is None or upper is None:
        return Resonance(centre, peak, None, None, lower, upper)
    bandwidth = upper - lower
    return Resonance(centre, peak, bandwidth, centre / bandwidth, lower, upper)


def time_constant(
    t: Sequence[float],
    y: Sequence[float],
    *,
    kind: Literal["decay", "rise"] = "decay",
    yerr: Optional[Errors] = None,
    p0: Optional[Sequence[float]] = None,
) -> ModelFit:
    """Fit an RC exponential and return the :class:`ModelFit`; read ``fit.parameter("tau")``."""
    if kind not in ("decay", "rise"):
        raise ValueError("kind must be 'decay' or 'rise'")
    model = exponential_decay if kind == "decay" else exponential_rise
    return fit_model(model, t, y, yerr, p0)


def rise_time(
    t: Sequence[float],
    y: Sequence[float],
    low: float = 0.1,
    high: float = 0.9,
    *,
    initial: Optional[float] = None,
    final: Optional[float] = None,
) -> float:
    """Time for a step to go from ``low`` to ``high`` of its swing (10–90% by default).

    Works for falling edges too. ``initial`` and ``final`` default to the median of the
    first and last tenth of the samples.
    """
    if not 0 < low < high < 1:
        raise ValueError("require 0 < low < high < 1")
    times, values = _data(t, y)
    order = np.argsort(times)
    times, values = times[order], values[order]
    edge = max(1, times.size // 10)
    start = float(np.median(values[:edge])) if initial is None else float(initial)
    end = float(np.median(values[-edge:])) if final is None else float(final)
    if start == end:
        raise ValueError("initial and final levels must differ")
    progress = (values - start) / (end - start)

    def crossing(level: float) -> float:
        hits = np.flatnonzero(progress >= level)
        if hits.size == 0:
            raise ValueError("the signal never reaches the requested level")
        j = int(hits[0])
        if j == 0:
            return float(times[0])
        fraction = (level - progress[j - 1]) / (progress[j] - progress[j - 1])
        return float(times[j - 1] + fraction * (times[j] - times[j - 1]))

    return crossing(high) - crossing(low)


def phase_from_delay(delay: Any, frequency: Any) -> Measurement:
    """Phase lag in degrees, 360 · frequency · delay, propagating any uncertainties."""
    def as_measurement(value: Any) -> Measurement:
        return value if isinstance(value, Measurement) else Measurement(value)

    result = 360.0 * as_measurement(delay) * as_measurement(frequency)
    result.set_unit("°")
    return result


def time_delay(time: Sequence[float], a: Sequence[float], b: Sequence[float]) -> float:
    """Delay of signal ``b`` relative to ``a`` (positive when b lags), by cross-correlation.

    Requires uniform sampling; signals are mean-subtracted and Hann-windowed, and the peak
    is refined to sub-sample resolution. A short record of a sinusoid is biased by the
    finite window (a few percent of a period for ~4 periods; better with more), so for
    sinusoids at a known frequency prefer :func:`phase_difference`.
    """
    times, a_values = _data(time, a)
    _, b_values = _data(time, b)
    if times.size < 3:
        raise ValueError("at least three samples are needed")
    steps = np.diff(times)
    if np.any(steps <= 0) or np.ptp(steps) > 0.01 * np.mean(steps):
        raise ValueError("time must be strictly increasing and uniformly sampled")
    window = np.hanning(a_values.size)
    a_values = (a_values - a_values.mean()) * window
    b_values = (b_values - b_values.mean()) * window
    correlation = fftconvolve(b_values, a_values[::-1], mode="full")
    j = int(np.argmax(correlation))
    lag = float(j - (a_values.size - 1))
    if 0 < j < correlation.size - 1:
        left, mid, right = correlation[j - 1:j + 2]
        curvature = left - 2 * mid + right
        if curvature != 0:
            lag += 0.5 * (left - right) / curvature
    return lag * float(np.mean(steps))


def phase_difference(
    time: Sequence[float], a: Sequence[float], b: Sequence[float], frequency: float
) -> float:
    """Phase lag of ``b`` behind ``a`` in degrees (-180, 180], for sinusoids at ``frequency``.

    Each signal is least-squares fitted with an offset plus sine and cosine terms at the
    given frequency, so offsets, partial periods and noise are handled exactly.
    """
    if not frequency > 0:
        raise ValueError("frequency must be positive")
    times, a_values = _data(time, a)
    _, b_values = _data(time, b)
    if times.size < 4:
        raise ValueError("at least four samples are needed")
    omega = 2 * np.pi * frequency
    design = np.column_stack([np.ones_like(times), np.sin(omega * times), np.cos(omega * times)])

    def phase(values: np.ndarray) -> float:
        (_, sine, cosine), *_ = np.linalg.lstsq(design, values, rcond=None)
        return float(np.arctan2(cosine, sine))

    lag = float(np.degrees(phase(a_values) - phase(b_values)))
    return float(lag - 360 * np.ceil((lag - 180) / 360))


def phase_from_lissajous(x: Sequence[float], y: Sequence[float]) -> float:
    """Phase difference in degrees (0 to 180) between two sinusoids, from their XY ellipse.

    Fits a x² + b xy + c y² + d x + e y = 1 and uses cos(phase) = -b / (2√(ac)). The sign
    of the phase cannot be recovered from a Lissajous figure; offsets are handled.
    """
    x_values, y_values = _data(x, y)
    if x_values.size < 5:
        raise ValueError("at least five points are needed")
    design = np.column_stack([x_values**2, x_values * y_values, y_values**2, x_values, y_values])
    (a, b, c, _, _), *_ = np.linalg.lstsq(design, np.ones(x_values.size), rcond=None)
    if a * c <= 0:
        raise ValueError("the data do not trace an ellipse")
    return float(np.degrees(np.arccos(np.clip(-b / (2 * np.sqrt(a * c)), -1.0, 1.0))))
