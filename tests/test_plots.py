import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np  # noqa: E402
from matplotlib import pyplot as plt  # noqa: E402

from labplotlib import (  # noqa: E402
    errorbar_plot,
    finish_plot,
    line_plot,
    polynomial_fit,
    scatter_plot,
    scatter_with_fit,
    scatter_with_residuals,
)


class FitColourTests(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_second_dataset_gets_new_colour_and_fit_is_paler_same_hue(self):
        fig, ax = plt.subplots()
        scatter_with_fit([1, 2, 3], [1, 2, 3.1], ax=ax)
        scatter_with_fit([1, 2, 3], [2, 4, 6.2], ax=ax)

        first, second = ax.collections
        self.assertNotEqual(first.get_facecolor()[0].tolist(), second.get_facecolor()[0].tolist())
        data = np.array(first.get_facecolor()[0][:3])
        fit = np.array(ax.lines[0].get_color() if isinstance(ax.lines[0].get_color(), tuple)
                       else plt.matplotlib.colors.to_rgb(ax.lines[0].get_color()))
        self.assertTrue(np.all(fit >= data))
        self.assertTrue(np.all(fit > data - 1e-9))


class ColormapTests(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_default_cmap_is_crest_and_colorbar_added(self):
        fig = scatter_plot([1, 2, 3], [1, 2, 3], c=[0, 1, 2], colorbar=True, colorbar_label="T")

        self.assertEqual(len(fig.axes), 2)
        self.assertEqual(fig.axes[1].get_ylabel(), "T")
        self.assertEqual(fig.axes[0].collections[0].get_cmap().name, "crest")

    def test_named_cmap_and_no_colorbar_by_default(self):
        fig = scatter_plot([1, 2, 3], [1, 2, 3], c=[0, 1, 2], cmap="Spectral")

        self.assertEqual(len(fig.axes), 1)
        self.assertEqual(fig.axes[0].collections[0].get_cmap().name, "Spectral")

    def test_cmap_without_c_or_bad_c_raises(self):
        with self.assertRaises(ValueError):
            scatter_plot([1, 2], [1, 2], colorbar=True)
        with self.assertRaises(ValueError):
            scatter_plot([1, 2], [1, 2], c=[1, 2, 3])


class PlotTests(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_line_plot_returns_titled_figure(self):
        fig = line_plot([1, 2, 3], [1, 4, 9], title="T", xlabel="x", ylabel="y", show=False)

        ax = fig.axes[0]
        self.assertEqual(ax.get_title(), "T")
        self.assertEqual(ax.get_xlabel(), "x")

    def test_saves_and_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "nested" / "out"
            line_plot([1, 2], [1, 2], filename="p.png", save_directory=target, show=False)

            self.assertTrue((target / "p.png").is_file())

    def test_scatter_with_fit_has_two_artists(self):
        fig = scatter_with_fit([1, 2, 3, 4], [2, 4, 6, 8], show=False)

        ax = fig.axes[0]
        self.assertEqual(len(ax.lines), 1)
        self.assertEqual(len(ax.collections), 1)

    def test_scatter_with_fit_validates_input(self):
        with self.assertRaises(ValueError):
            scatter_with_fit([1, 2, 3], [1, 2], show=False)
        with self.assertRaises(ValueError):
            scatter_with_fit([1, 2], [1, 2], degree=2, show=False)

    def test_errorbar_plot(self):
        fig = errorbar_plot([1, 2, 3], [1, 2, 3], yerr=[0.1, 0.1, 0.1], show=False)

        self.assertEqual(len(fig.axes), 1)

    def test_composing_plots_preserves_axes_labels_and_does_not_finish(self):
        fig, ax = plt.subplots()
        ax.set_xlabel("time (s)")
        before = dict(plt.rcParams)
        with patch("matplotlib.pyplot.show") as show, patch.object(fig, "tight_layout") as layout:
            self.assertIs(line_plot([0, 1], [1, 2], ax=ax, label="line"), fig)
            self.assertIs(errorbar_plot([0, 1], [1, 2], yerr=0.1, ax=ax), fig)
            show.assert_not_called()
            layout.assert_not_called()
        self.assertEqual(ax.get_xlabel(), "time (s)")
        self.assertEqual(dict(plt.rcParams), before)
        self.assertEqual(ax.lines[0].get_label(), "line")
        plt.close(fig)

    def test_finish_is_explicit_and_show_is_opt_in(self):
        fig = line_plot([0, 1], [1, 2])
        with tempfile.TemporaryDirectory() as tmp, patch("matplotlib.pyplot.show") as show:
            self.assertIs(finish_plot(fig, "nested/plot.png", tmp, dpi=100), fig)
            self.assertTrue((Path(tmp) / "nested" / "plot.png").is_file())
            show.assert_not_called()
            finish_plot(fig, show=True)
            show.assert_called_once()

    def test_fit_statistics_and_weighting(self):
        fit = polynomial_fit([0, 1, 2], [1, 3, 5], yerr=0.5)
        np.testing.assert_allclose(fit.coefficients, [2, 1])
        np.testing.assert_allclose(fit.residuals, [0, 0, 0], atol=1e-12)
        self.assertAlmostEqual(fit.r_squared, 1.0)
        self.assertAlmostEqual(fit.chi_squared, 0.0)
        self.assertAlmostEqual(fit.reduced_chi_squared, 0.0)
        weighted = polynomial_fit([0, 1, 2], [0, 1, 10], yerr=[0.1, 0.1, 100])
        self.assertAlmostEqual(weighted.coefficients[0], 1, places=3)
        self.assertIsNone(polynomial_fit([0, 1], [2, 2]).r_squared)
        self.assertIsNone(polynomial_fit([0, 1], [1, 2], yerr=1).reduced_chi_squared)

    def test_invalid_fit_input(self):
        for x, y, kwargs in [
            ([[1, 2]], [[1, 2]], {}),
            ([1, 1], [1, 2], {}),
            ([1, float("nan")], [1, 2], {}),
            ([1, 2], [1, 2], {"degree": 1.5}),
            ([1, 2], [1, 2], {"yerr": 0}),
            ([1, 2], [1, 2], {"yerr": [1]}),
        ]:
            with self.subTest(x=x, kwargs=kwargs), self.assertRaises(ValueError):
                polynomial_fit(x, y, **kwargs)

    def test_residuals_with_existing_axes_and_unsorted_x(self):
        fig, axes = plt.subplots(2, 1)
        result = scatter_with_residuals(
            [2, 0, 1], [5, 1, 3], ylabel="position (m)", xlabel="time (s)", axes=axes
        )
        self.assertIs(result, fig)
        self.assertEqual(len(fig.axes), 2)
        self.assertTrue(np.all(np.diff(axes[0].lines[0].get_xdata()) >= 0))
        np.testing.assert_allclose(axes[1].collections[0].get_offsets()[:, 1], 0, atol=1e-12)
        self.assertEqual(axes[1].get_ylabel(), "Residual (position (m))")
        other, other_ax = plt.subplots()
        with self.assertRaises(ValueError):
            scatter_with_residuals([0, 1], [1, 2], axes=(axes[0], other_ax))
        plt.close(other)

    def test_asymmetric_errorbars(self):
        fig = errorbar_plot([1, 2], [2, 3], yerr=[[0.1, 0.2], [0.2, 0.3]])
        self.assertEqual(len(fig.axes[0].containers), 1)
        with self.assertRaises(ValueError):
            errorbar_plot([1, 2], [2, 3], yerr=[0.1, -0.2])

    def test_import_does_not_change_theme(self):
        import subprocess
        import sys

        code = (
            "import matplotlib as m; before = dict(m.rcParams); import labplotlib; "
            "assert dict(m.rcParams) == before"
        )
        subprocess.run([sys.executable, "-c", code], check=True)


if __name__ == "__main__":
    unittest.main()
