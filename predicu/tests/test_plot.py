from pathlib import Path

import pytest

from predicu.plot import PLOTS, generate_plots
from predicu.tests.utils import load_test_data


def test_generate_plots_wrong_name():
    msg = "Unknown plot.* invalid2"
    with pytest.raises(ValueError, match=msg):
        generate_plots(plots=["invalid2"])
