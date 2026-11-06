import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

from matplotlib import pyplot as plt  # noqa: E402

from labplotlib import errorbar_plot, line_plot, scatter_with_fit  # noqa: E402


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
