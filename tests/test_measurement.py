import unittest

import numpy as np
import pandas as pd

from labplotlib import Measurement, errorbar_plot, polynomial_fit, scatter_with_residuals


class MeasurementTests(unittest.TestCase):
    def test_pm_combines_independent_components_and_relative_uncertainty(self):
        m = Measurement.from_pm([10, -20], [3, 4], relative=0.1, granularity=2)
        np.testing.assert_allclose(m.uncertainty, np.sqrt([14, 24]))
        np.testing.assert_allclose(m.relative_uncertainty(), np.sqrt([14, 24]) / [10, 20])
        self.assertIsNone(Measurement.from_pm(2).uncertainty)
        with self.assertRaises(ValueError):
            Measurement.from_pm(0, 1).relative_uncertainty()

    def test_sample_spread_and_standard_error(self):
        m = Measurement.from_stdev([1, 2, 3], granularity=0.5)
        self.assertEqual(m.value, 2)
        self.assertAlmostEqual(m.uncertainty, np.sqrt(1.25))
        mean = Measurement.from_stdev([1, 2, 3], mean_error=True, granularity=0.5)
        self.assertAlmostEqual(mean.uncertainty, np.sqrt(1 / 3 + 0.25))
        vectors = Measurement.from_stdev([[1, 10], [3, 14]], axis=0)
        np.testing.assert_allclose(vectors.value, [2, 12])
        np.testing.assert_allclose(vectors.uncertainty, np.sqrt([2, 8]))
        with self.assertRaises(ValueError):
            Measurement.from_stdev([1])

    def test_propagation_and_missing_errors(self):
        a = Measurement.from_pm(4, 0.2)
        b = Measurement.from_pm(2, 0.1)
        self.assertAlmostEqual((a + b).uncertainty, np.hypot(0.2, 0.1))
        self.assertAlmostEqual((a * b).uncertainty, np.hypot(2 * 0.2, 4 * 0.1))
        self.assertAlmostEqual((a / b).uncertainty, np.hypot(0.2 / 2, 4 * 0.1 / 4))
        self.assertAlmostEqual((a**2).uncertainty, 1.6)
        self.assertAlmostEqual((10 - a).value, 6)
        self.assertAlmostEqual((10 / a).uncertainty, 0.125)
        self.assertIsNone((Measurement(1) + 2).uncertainty)
        self.assertAlmostEqual((a + Measurement(1)).uncertainty, 0.2)
        with self.assertRaises(ZeroDivisionError):
            a / Measurement(0)
        with self.assertRaises(ValueError):
            Measurement(2, -1)

    def test_dataframe_columns_and_plot_integration(self):
        import matplotlib.pyplot as plt

        frame = pd.DataFrame({"time": [0, 1, 2], "distance": [1, 3, 5], "error": [0.2] * 3})
        m = Measurement.from_dataframe(frame, "distance", uncertainty="error")
        fit = polynomial_fit(frame["time"], m)
        np.testing.assert_allclose(fit.coefficients, [2, 1])
        self.assertIsNotNone(fit.chi_squared)
        fig = errorbar_plot(frame["time"], m)
        self.assertEqual(len(fig.axes[0].containers), 1)
        fig2 = scatter_with_residuals(frame["time"], m)
        self.assertEqual(len(fig2.axes[0].containers), 1)
        column = pd.Series([Measurement.from_pm(v, 0.2) for v in frame["distance"]])
        fig3 = errorbar_plot(frame["time"], column)
        self.assertEqual(len(fig3.axes[0].containers), 1)
        np.testing.assert_allclose(polynomial_fit(frame["time"], column).coefficients, [2, 1])
        plt.close(fig)
        plt.close(fig2)
        plt.close(fig3)

    def test_partial_missing_column_errors_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "mixes"):
            errorbar_plot([1, 2], pd.Series([Measurement(1), Measurement(2, 0.1)]))


if __name__ == "__main__":
    unittest.main()
