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

    def test_mean_combines_standard_error_and_independent_uncertainties(self):
        readings = Measurement([1, 2, 3], [0.3, 0.4, 0.5], unit="m", prefix="milli")
        result = readings.mean()
        self.assertAlmostEqual(result.value, 2)
        self.assertAlmostEqual(result.uncertainty, np.sqrt(1 / 3 + (0.09 + 0.16 + 0.25) / 9))
        self.assertEqual((result.unit, result.prefix), ("m", "milli"))
        np.testing.assert_array_equal(readings.value, [1, 2, 3])
        np.testing.assert_allclose(readings.uncertainty, [0.3, 0.4, 0.5])

    def test_mean_missing_uncertainty_and_axes(self):
        result = Measurement([1, 2, 3]).mean()
        self.assertAlmostEqual(result.uncertainty, np.sqrt(1 / 3))
        readings = Measurement([[1, 10], [3, 14]], 0.2)
        result = readings.mean(axis=0)
        np.testing.assert_allclose(result.value, [2, 12])
        np.testing.assert_allclose(result.uncertainty, np.sqrt([1.02, 4.02]))
        row_means = readings.mean(axis=-1)
        np.testing.assert_allclose(row_means.value, [5.5, 8.5])
        np.testing.assert_allclose(row_means.uncertainty, np.sqrt([20.27, 30.27]))
        with self.assertRaisesRegex(ValueError, "at least two"):
            Measurement([1]).mean()
        with self.assertRaisesRegex(ValueError, "at least two"):
            Measurement([[1], [2]]).mean(axis=1)
        with self.assertRaisesRegex(ValueError, "at least two"):
            Measurement(1).mean()

    def test_mean_speed_from_dataframe_measurements(self):
        frame = pd.DataFrame({
            "length": [0.85, 0.86, 0.84],
            "length_error": [0.01, 0.01, 0.01],
            "frequency": [200, 200, 200],
            "frequency_error": [1, 1, 1],
            "harmonic": [1, 1, 1],
        })
        length = Measurement.from_dataframe(frame, "length", uncertainty="length_error")
        frequency = Measurement.from_dataframe(frame, "frequency", uncertainty="frequency_error")
        harmonic = Measurement.from_dataframe(frame, "harmonic")
        speed = 2 * length * frequency / harmonic
        mean = speed.mean()
        np.testing.assert_allclose(speed.value, [340, 344, 336])
        expected_errors = np.sqrt(4**2 + np.array([1.7, 1.72, 1.68]) ** 2)
        np.testing.assert_allclose(speed.uncertainty, expected_errors)
        expected = np.sqrt(16 / 3 + np.sum(expected_errors**2) / 9)
        self.assertAlmostEqual(mean.value, 340)
        self.assertAlmostEqual(mean.uncertainty, expected)

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

    def test_string_representation(self):
        self.assertEqual(str(Measurement(4)), "4.000")
        self.assertEqual(str(Measurement(4, 0.2)), "4.000 ± 0.200")

    def test_selectable_string_formats_and_si_prefixes_do_not_change_math(self):
        measurement = Measurement(2_000_000, 100_000)
        self.assertEqual(measurement.to_string(format="raw"), "2000000.000 ± 100000.000")
        self.assertEqual(measurement.to_string(), "2.000 x 10⁶ ± 1.000 x 10⁵")
        self.assertEqual(
            Measurement(4).to_string(format="scientific"),
            "4.000 x 10⁰",
        )
        self.assertEqual(
            measurement.to_string(unit="Pa", prefix="mega"),
            "2.000 ± 0.100 MPa",
        )
        self.assertEqual(
            Measurement(2_000_000_000).to_string(unit="Pa", prefix="G"),
            "2.000 GPa",
        )
        self.assertEqual(Measurement(999).to_string(), "999.000")
        self.assertEqual(Measurement(0.001).to_string(), "0.001")
        self.assertEqual(Measurement(0.0001).to_string(), "1.000 x 10⁻⁴")
        self.assertEqual(measurement.to_string(decimals=1), "2.0 x 10⁶ ± 1.0 x 10⁵")
        self.assertEqual(measurement.to_string(decimals=None), "2 x 10⁶ ± 1 x 10⁵")
        self.assertEqual(measurement.value, 2_000_000)
        self.assertEqual((measurement + Measurement(1)).value, 2_000_001)

    def test_stored_display_units_do_not_affect_arithmetic(self):
        measurement = Measurement(2_000_000, 100_000)
        measurement.set_unit("Pa", "mega")
        self.assertEqual(str(measurement), "2.000 ± 0.100 MPa")
        self.assertEqual(measurement.unit, "Pa")
        self.assertEqual(measurement.prefix, "mega")
        self.assertIsNone((measurement + Measurement(1)).unit)
        self.assertEqual(measurement.value, 2_000_000)

        measurement.set_unit("m")
        self.assertEqual(str(measurement), "2.000 x 10⁶ ± 1.000 x 10⁵ m")
        measurement.set_unit(None)
        self.assertIsNone(measurement.unit)
        self.assertEqual(str(measurement), "2.000 x 10⁶ ± 1.000 x 10⁵")

    def test_scientific_rounding_normalizes_exponent(self):
        self.assertEqual(Measurement(9_999).to_string(decimals=0), "1 x 10⁴")

    def test_string_format_rejects_invalid_options(self):
        with self.assertRaisesRegex(ValueError, "prefix requires"):
            Measurement(1).to_string(prefix="k")
        with self.assertRaisesRegex(ValueError, "unsupported SI prefix"):
            Measurement(1).to_string(unit="m", prefix="unknown")
        with self.assertRaisesRegex(ValueError, "decimals"):
            Measurement(1).to_string(decimals=-1)
        with self.assertRaisesRegex(ValueError, "prefix requires"):
            Measurement(1).set_unit(None, prefix="k")
        with self.assertRaisesRegex(ValueError, "unsupported SI prefix"):
            Measurement(1).set_unit("m", prefix="unknown")

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
