# Fitting arbitrary models

```python
from labplotlib import fit_model, ModelFit, exponential_decay, exponential_rise, lorentzian, gaussian, power_law, diode
```

## `fit_model(model, x, y, yerr=None, p0=None, *, bounds=(-inf, inf), maxfev=20000)`

Fit `model(x, *parameters)` to data by (weighted) least squares, using
`scipy.optimize.curve_fit`.

| Parameter | Meaning |
| --- | --- |
| `model` | A function whose first argument is `x`, followed by one or more named parameters. The names are read from its signature. |
| `x`, `y` | Data, as for the [plotting functions](plotting.md). `Measurement` values are accepted. |
| `yerr` | Positive scalar or per-point standard uncertainties. Treated as absolute, so they weight the fit and give a meaningful χ². When omitted, uncertainties carried by a `Measurement` `y` are used. |
| `p0` | Starting parameters, one per model parameter. The built-in models estimate their own; supply `p0` for custom models, since nonlinear fits can fail from a poor start. |
| `bounds` | Optional `(lower, upper)` parameter bounds, as in `curve_fit`. |
| `maxfev` | Maximum function evaluations. |

**Returns:** a [`ModelFit`](#modelfit). Raises `ValueError` for bad data, fewer
points than parameters (more points than parameters are required), a wrong-length `p0`, or
parameter uncertainties that cannot be estimated, and `RuntimeError` if the
fit does not converge.

Without `yerr`, parameter uncertainties are scaled to the scatter of the
residuals and `chi_squared`, `reduced_chi_squared` and `p_value` are `None`.
The fit does not account for uncertainty in x or for correlated errors.

```python
import numpy as np
from labplotlib import exponential_decay, fit_model

t = np.linspace(0, 5e-3, 40)
v = exponential_decay(t, 5.0, 1e-3, 0.0) + np.random.default_rng(0).normal(0, 0.05, t.size)
fit = fit_model(exponential_decay, t, v, yerr=0.05)

print(fit.parameter("tau").to_string(uncertainty_digits=1, unit="s", prefix="auto"))
print(fit.summary())
```

## `ModelFit`

| Attribute or method | Meaning |
| --- | --- |
| `names`, `values`, `uncertainties` | Parameter names, best-fit values and one-sigma uncertainties. |
| `covariance` | Parameter covariance matrix. |
| `parameters` | Dict of parameter name to `Measurement`. |
| `parameter(name)` | One parameter as a `Measurement`; an unknown name raises `ValueError`. |
| `predict(x)` | Model evaluated at `x` with the fitted parameters. |
| `residuals` | Observed minus predicted, in input order. |
| `dof` | Points minus parameters. |
| `chi_squared`, `reduced_chi_squared`, `p_value` | χ², χ²/dof, and the probability of a χ² at least this large by chance. `None` without `yerr`. |
| `r_squared` | Unweighted R², or `None` when all y values are equal. |
| `summary()` | Multi-line text of the parameters (rounded to their uncertainties) and statistics. |

A reduced χ² near 1 and a moderate p-value mean the model and uncertainties
agree with the data. Much larger than 1 suggests a poor model or underestimated
errors; much smaller than 1 suggests overestimated errors. The
`fit_statistics(fit)` helper (in `labplotlib.fitting`) returns the statistics
lines used by `summary()`, for any `ModelFit` or `PolynomialFit`.

## Built-in models

| Model | Formula | Typical use |
| --- | --- | --- |
| `exponential_decay(t, amplitude, tau, offset)` | `offset + amplitude·exp(−t/tau)` | RC discharge. |
| `exponential_rise(t, amplitude, tau, offset)` | `offset + amplitude·(1 − exp(−t/tau))` | RC charging. |
| `lorentzian(x, amplitude, center, width, offset)` | `offset + amplitude·(width/2)² / ((x−center)² + (width/2)²)` | Resonance curves; `width` is the FWHM, so Q = `center / width`. |
| `gaussian(x, amplitude, mean, sigma, offset)` | `offset + amplitude·exp(−(x−mean)²/(2σ²))` | Peaks and noise distributions. |
| `power_law(x, coefficient, exponent)` | `coefficient·x**exponent` | Scaling laws. |
| `diode(voltage, i_s, n_vt)` | `i_s·(exp(voltage/n_vt) − 1)` | Shockley diode I–V; `n_vt` is the ideality factor times kT/q. |

Any other function works too. Give a starting guess for it:

```python
import numpy as np
from labplotlib import fit_model

def damped_sine(t, amplitude, decay, omega, phase):
    return amplitude * np.exp(-decay * t) * np.sin(omega * t + phase)

fit = fit_model(damped_sine, t, y, yerr=0.02, p0=[1.0, 0.5, 20.0, 0.0])
```

To plot a fit and its residuals in one step, pass `model=` to
[`scatter_with_fit` or `scatter_with_residuals`](plotting.md).
