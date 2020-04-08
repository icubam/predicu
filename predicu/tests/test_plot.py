import pytest
import os
from pathlib import Path

import predicu.plots
from predicu.plots import generate_plots
import predicu.data


def test_generate_plots_wrong_name():

    msg = "Unknown plot.* invalid2"
    with pytest.raises(ValueError, match=msg):
        generate_plots(plots=["invalid2"])


@pytest.mark.parametrize("name", predicu.plots.PLOTS)
def test_generate_plots(name, tmpdir, monkeypatch):
    output_dir = str(tmpdir.mkdir("sub"))
    monkeypatch.setitem(
        predicu.data.DATA_PATHS,
        "icubam",
        os.path.join(
            predicu.data.BASE_PATH,
            "tests/data/fake_all_bedcounts_2020-04-08_16h41.csv",
        ),
    )
    generate_plots(plots=[name], output_dir=output_dir)

    assert (Path(output_dir) / (name + ".png")).exists()
