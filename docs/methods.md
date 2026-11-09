# Numerical methods

`polynomial_fit` and `PolynomialFit` are available from the package root.
The other functions on this page are imported from `labplotlib.methods`.

## `polynomial_fit(x, y, degree=1, yerr=None)`

Fit a polynomial to y versus x, optionally weighted by y standard
uncertainties.

| Parameter | Meaning |
| --- | --- |
| `x`, `y` | Matching, non-empty one-dimensional sequences of finite values. Measurements can supply values and, for y, inferred uncertainty. |
| `degree` | Positive integer degree. The data must contain at least `degree + 1` points with distinct x values. |
| `yerr` | Optional positive finite scalar or length-N sequence of independent y standard uncertainties. Overrides uncertainty inferred from `y`. |

**Returns:** a `PolynomialFit`. Invalid input raises `ValueError`. The fit
uses `1 / yerr` as NumPy's fitting weights, minimizing squared residuals divided
by `yerr**2`. It does not account for x uncertainty or correlated errors.

```python
from labplotlib import polynomial_fit

fit = polynomial_fit([0, 1, 2], [1, 3, 5], yerr=0.2)
print(fit.coefficients)        # approximately [2, 1]
print(fit.reduced_chi_squared)
```

### `PolynomialFit`

| Attribute | Meaning |
| --- | --- |
| `coefficients` | NumPy array ordered from highest power to constant. |
| `residuals` | NumPy array of observed minus predicted y values, in input order. |
| `r_squared` | Unweighted R², or `None` when all y values are equal. |
| `chi_squared` | Chi-squared statistic, or `None` without y uncertainties. |
| `reduced_chi_squared` | Chi-squared divided by `N - degree - 1`, or `None` without uncertainties or positive degrees of freedom. |
| `p_value` | Probability of a chi-squared at least this large by chance, or `None` without uncertainties or positive degrees of freedom. |
| `dof` | Degrees of freedom, `N - degree - 1`, or `None` if not computed. |
## `chi_squared(y_obs, y_exp, y_err)`

```python
from labplotlib.methods import chi_squared
```

Compute the sum of `((observed - expected) / error) ** 2`.

| Parameter | Meaning |
| --- | --- |
| `y_obs` | Observed values, convertible to a NumPy array. |
| `y_exp` | Expected values, broadcastable with `y_obs`. |
| `y_err` | Errors, broadcastable with the data; use nonzero standard uncertainties. |

**Returns:** a NumPy numeric scalar. Inputs are passed to NumPy operations;
this helper does not validate shapes, errors, or finiteness.

```python
from labplotlib.methods import chi_squared

statistic = chi_squared([1.0, 2.1], [1.0, 2.0], [0.1, 0.1])
print(statistic)  # approximately 1
```

## `reduced_chi_squared(y_obs, y_exp, y_err, dof)`

Divide `chi_squared` by the supplied
degrees of freedom.

| Parameter | Meaning |
| --- | --- |
| `y_obs`, `y_exp`, `y_err` | Observations, expectations, and errors as described for `chi_squared`. |
| `dof` | Degrees of freedom; supply a positive number appropriate to the model. |

**Returns:** the reduced chi-squared numeric value. This helper does not
validate degrees of freedom.

```python
from labplotlib.methods import reduced_chi_squared

print(reduced_chi_squared([1.0, 2.1], [1.0, 2.0], [0.1, 0.1], dof=1))
```

## `p_value_chi_squared(y_obs, y_exp, y_err, dof=1)`

Calculate `1 - scipy.stats.chi2.cdf(statistic, dof)`.

| Parameter | Meaning |
| --- | --- |
| `y_obs`, `y_exp`, `y_err` | Observations, expectations, and errors as described for `chi_squared`. |
| `dof` | Degrees of freedom, default `1`; supply a positive value appropriate to the model. |

**Returns:** a numeric p-value. This helper does not validate the data or
degrees of freedom; SciPy's distribution behavior applies.

```python
from labplotlib.methods import p_value_chi_squared

print(p_value_chi_squared([1.0, 2.1], [1.0, 2.0], [0.1, 0.1], dof=1))
```

## `k_means(X, k, max_iters=100)`

Cluster rows of a NumPy array by Euclidean distance.

| Parameter | Meaning |
| --- | --- |
| `X` | Two-dimensional NumPy array with one sample per row. |
| `k` | Number of clusters; initial centroids are sampled without replacement. |
| `max_iters` | Maximum number of assignment/update iterations, default `100`. |

**Returns:** `(centroids, labels)`, arrays of cluster centers and row
assignments. Initialization is random and there is no seed parameter. The
implementation has no explicit empty-cluster handling; empty clusters may
produce NaN centroids. Supply at least one iteration and `1 <= k <= len(X)`.

```python
import numpy as np
from labplotlib.methods import k_means

centroids, labels = k_means(np.array([[0.0], [0.1], [5.0], [5.1]]), k=2)
print(centroids, labels)
```
