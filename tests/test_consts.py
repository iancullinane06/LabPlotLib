import math
import os
import subprocess
import sys
from pathlib import Path

from labplotlib import Measurement, consts


def test_boltzmann():
    assert consts.kb == 1.380649e-23


def test_multiplies_into_measurement():
    t = Measurement(300.0, 3.0)
    for result in (consts.kb * t, t * consts.kb):
        assert math.isclose(float(result.value), consts.kb * 300.0)
        assert math.isclose(float(result.uncertainty), consts.kb * 3.0)
    ratio = t / consts.kb
    assert math.isclose(float(ratio.value), 300.0 / consts.kb)


def test_derived_constants():
    assert math.isclose(consts.R, 8.314462618, rel_tol=1e-9)
    assert math.isclose(consts.sigma, 5.670374419e-8, rel_tol=1e-8)
    assert math.isclose(consts.hbar, 1.054571817e-34, rel_tol=1e-9)


def test_direct_execution_lists_constants():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, str(Path(consts.__file__).resolve())],
        capture_output=True,
        check=True,
        encoding="utf-8",
        env=env,
    )
    assert "kb = " in result.stdout
    assert "1.380649e-23" in result.stdout
    assert "m/s²" in result.stdout
