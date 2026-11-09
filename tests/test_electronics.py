import os
import unittest

os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np  # noqa: E402
from matplotlib import pyplot as plt  # noqa: E402

from labplotlib import (  # noqa: E402
    Measurement,
    bode_plot,
    cutoff_frequency,
    diode,
    exponential_decay,
    exponential_rise,
    fit_model,
    gain_to_db,
    lorentzian,
    phase_difference,
    phase_from_delay,
    phase_from_lissajous,
    resonance,
    rise_time,
    rolloff_slope,
    scatter_with_fit,
    scatter_with_residuals,
    time_constant,
    time_delay,
)
from labplotlib import measurement as m  # noqa: E402


class FitModelTests(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(1)

    def test_decay_recovers_tau_with_statistics(self):
        t = np.linspace(0, 5e-3, 60)
        sigma = 0.02
        y = exponential_decay(t, 5.0, 1e-3, 0.1) + self.rng.normal(0, sigma, t.size)
        fit = time_constant(t, y, yerr=sigma)

        tau = fit.parameter("tau")
        self.assertLess(abs(tau.value - 1e-3), 4 * tau.uncertainty)
        self.assertEqual(fit.dof, 57)
        self.assertTrue(0.5 < fit.reduced_chi_squared < 1.6)
        self.assertTrue(0 < fit.p_value <= 1)

    def test_rise_lorentzian_and_diode(self):
        t = np.linspace(0, 5e-3, 60)
        rise = time_constant(t, exponential_rise(t, 3.0, 1e-3, 0.0), kind="rise")
        self.assertAlmostEqual(rise.parameter("tau").value, 1e-3, places=6)

        f = np.linspace(800, 1200, 80)
        peak = fit_model(lorentzian, f, lorentzian(f, 2.0, 1000, 50, 0.1))
        self.assertAlmostEqual(peak.parameter("center").value, 1000, places=3)
        self.assertAlmostEqual(peak.parameter("width").value, 50, places=3)

        v = np.linspace(0.3, 0.7, 40)
        d = fit_model(diode, v, diode(v, 1e-12, 0.04))
        self.assertAlmostEqual(d.parameter("n_vt").value, 0.04, places=4)

    def test_measurement_errors_are_used_and_bad_inputs_rejected(self):
        t = np.linspace(0, 4, 30)
        y = Measurement(exponential_decay(t, 2, 1.0, 0) + self.rng.normal(0, 0.01, 30), 0.01)
        self.assertIsNotNone(fit_model(exponential_decay, t, y).chi_squared)
        with self.assertRaises(ValueError):
            fit_model(exponential_decay, t[:3], y.value[:3])
        with self.assertRaises(ValueError):
            fit_model(exponential_decay, t, y.value).parameter("missing")


class ElectronicsTests(unittest.TestCase):
    def test_cutoff_and_rolloff_of_first_order_low_pass(self):
        f = np.logspace(1, 5, 200)
        fc = 1500.0
        gain_db = -10 * np.log10(1 + (f / fc) ** 2)

        self.assertAlmostEqual(cutoff_frequency(f, gain_db) / fc, 1, places=2)
        slope = rolloff_slope(f, gain_db, 20 * fc, 100 * fc)
        self.assertAlmostEqual(slope.value, -20, delta=0.2)
        self.assertEqual(slope.unit, "dB/decade")

    def test_resonance_q_factor(self):
        f = np.linspace(500, 1500, 2001)
        f0, q = 1000.0, 20.0
        response = 1 / np.sqrt(1 + q**2 * (f / f0 - f0 / f) ** 2)
        result = resonance(f, response)

        self.assertAlmostEqual(result.frequency, f0, delta=1)
        self.assertAlmostEqual(result.q_factor, q, delta=0.5)
        self.assertIsNone(resonance(f[:1021], response[:1021]).q_factor)

    def test_rise_time_of_rc_step(self):
        t = np.linspace(0, 10e-3, 4001)
        tau = 1e-3
        y = 1 - np.exp(-t / tau)

        self.assertAlmostEqual(rise_time(t, y) / (tau * np.log(9)), 1, places=2)
        self.assertAlmostEqual(rise_time(t, 1 - y) / (tau * np.log(9)), 1, places=2)

    def test_phase_methods_agree(self):
        t = np.linspace(0, 4e-3, 4000, endpoint=False)
        f, phase = 1000.0, np.radians(40)
        a = np.sin(2 * np.pi * f * t)
        b = 0.5 * np.sin(2 * np.pi * f * t - phase) + 0.1

        delay = time_delay(t, a, b)
        self.assertAlmostEqual(phase_from_delay(delay, f).value, 40, delta=1.5)
        self.assertAlmostEqual(phase_difference(t, a, b, f), 40, places=6)
        self.assertAlmostEqual(phase_difference(t, b, a, f), -40, places=6)
        self.assertAlmostEqual(phase_from_lissajous(a, b), 40, delta=0.2)
        measured = phase_from_delay(Measurement(1e-4, 1e-6), f)
        self.assertAlmostEqual(measured.uncertainty, 0.36, places=6)
        self.assertEqual(measured.unit, "°")

    def test_gain_to_db_propagates_uncertainty(self):
        db = gain_to_db(Measurement([1.0, 0.1], [0.01, 0.001]))

        np.testing.assert_allclose(db.value, [0, -20])
        np.testing.assert_allclose(db.uncertainty, 20 / np.log(10) * 0.01)
        with self.assertRaises(ValueError):
            gain_to_db([0.0, 1.0])


class BodeAndPlotTests(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_bode_has_log_axis_and_twin_phase_axis(self):
        f = np.logspace(1, 4, 20)
        fig = bode_plot(f, 1 / np.sqrt(1 + (f / 500) ** 2), -np.degrees(np.arctan(f / 500)))

        self.assertEqual(len(fig.axes), 2)
        self.assertEqual(fig.axes[0].get_xscale(), "log")
        self.assertEqual(fig.axes[1].get_ylabel(), "Phase (°)")
        with self.assertRaises(ValueError):
            bode_plot(f, f, gain_db=f)

    def test_use_errors_default_draws_error_bars_and_can_be_disabled(self):
        x = [1, 2, 3, 4]
        y = Measurement([2.0, 4.1, 5.9, 8.0], 0.1)

        with_errors = scatter_with_fit(x, y)
        without = scatter_with_fit(x, y, use_errors=False)
        self.assertTrue(with_errors.axes[0].containers)
        self.assertFalse(without.axes[0].containers)
        weighted = scatter_with_fit(x, y, show_stats=True)
        self.assertIn("χ²", weighted.axes[0].texts[0].get_text())

    def test_xerr_from_measurement_is_drawn(self):
        fig = scatter_with_fit(Measurement([1.0, 2.0, 3.0, 4.0], 0.1), [1, 2, 3.2, 4])
        self.assertTrue(fig.axes[0].containers)

    def test_model_fit_and_log_scales_in_fit_plots(self):
        t = np.linspace(0.01, 5, 40)
        y = exponential_decay(t, 4.0, 1.0, 0.0) + 0.001 * np.sin(40 * t)
        fig = scatter_with_residuals(t, y, model=exponential_decay, yscale="log", show_stats=True)

        self.assertEqual(fig.axes[0].get_yscale(), "log")
        self.assertIn("tau", fig.axes[0].texts[0].get_text())
        fit_line = fig.axes[0].lines[0]
        self.assertEqual(len(fit_line.get_xdata()), 200)

        log_fig = scatter_with_fit(np.logspace(0, 3, 10), np.logspace(0, 3, 10) * 2, xscale="log")
        xs = log_fig.axes[0].lines[0].get_xdata()
        self.assertAlmostEqual(xs[1] / xs[0], xs[2] / xs[1])


class MeasurementFunctionTests(unittest.TestCase):
    def test_functions_propagate_uncertainty(self):
        x = Measurement([0.5, 2.0], 0.01)

        np.testing.assert_allclose(m.sin(x).uncertainty, np.abs(np.cos(x.value)) * 0.01)
        np.testing.assert_allclose(m.exp(x).uncertainty, np.exp(x.value) * 0.01)
        np.testing.assert_allclose(m.log(x).uncertainty, 0.01 / x.value)
        np.testing.assert_allclose(m.sqrt(x).uncertainty, 0.005 / np.sqrt(x.value))
        np.testing.assert_allclose(m.arctan(x).uncertainty, 0.01 / (1 + x.value**2))
        np.testing.assert_allclose(m.log10(x).value, np.log10(x.value))

    def test_domain_errors_and_missing_uncertainty(self):
        with self.assertRaises(ValueError):
            m.log(Measurement(0.0, 0.1))
        with self.assertRaises(ValueError):
            m.arcsin(Measurement(1.0, 0.1))
        self.assertIsNone(m.sqrt(4.0).uncertainty)
        self.assertEqual(m.sqrt(Measurement(0.0)).value, 0)

    def test_apply_uses_numerical_derivative(self):
        result = Measurement(3.0, 0.1).apply(lambda v: v**2)
        self.assertAlmostEqual(float(result.uncertainty), 0.6, places=5)

    def test_unit_aware_formatting(self):
        r = Measurement(1234.0, 56.0, unit="Ω", prefix="auto")

        self.assertEqual(r.to_string(uncertainty_digits=1), "1.23 ± 0.06 kΩ")
        self.assertEqual(Measurement(1.23e-6, 4e-8).to_string(uncertainty_digits=1, unit="F",
                                                               prefix="auto"), "1.23 ± 0.04 µF")
        self.assertEqual(Measurement(1.23e-6, 4e-8).to_string(uncertainty_digits=2, unit="F",
                                                               prefix="auto"), "1.230 ± 0.040 µF")
        self.assertEqual(Measurement(1.2, 0.1).to_string(uncertainty_digits=1), "1.2 ± 0.1")
        self.assertEqual(Measurement(0.0123, 0.00096).to_string(uncertainty_digits=1), "0.012 ± 0.001")
        self.assertEqual(Measurement(1.5e-5, 2e-7).to_string(uncertainty_digits=1),
                         "(1.50 ± 0.02) x 10⁻⁵")
        with self.assertRaises(ValueError):
            Measurement([1.0, 2.0], 0.1).to_string(uncertainty_digits=1)
        with self.assertRaises(ValueError):
            Measurement(1.0).to_string(uncertainty_digits=1)


if __name__ == "__main__":
    unittest.main()
