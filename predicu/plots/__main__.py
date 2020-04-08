import argparse
import logging
from typing import Optional, List

import matplotlib
import matplotlib.style

import predicu.data
import predicu.plot
import predicu.plots


def generate_plots(
    plots: Optional[List[str]] = None,
    matplotlib_style: str = "seaborn-whitegrid",
    api_key: Optional[str] = None,
    output_type: str = "png",
    output_dir: str = "/tmp/",
):
    # Note: the default values here should match the defaults in CLI below.
    if plots is None:
        plots = predicu.plots.PLOTS

    plots_unknown = set(plots).difference(predicu.plots.PLOTS)
    if plots_unknown:
        raise ValueError(
            "Unknown plot(s): {}".format(", ".join(plots_unknown))
        )
    for plot in sorted(plots):
        logging.info("generating plot %s in %s" % (plot, output_dir))
        predicu.plots.plot(
            plot,
            api_key=api_key,
            matplotlib_style=matplotlib_style,
            output_dir=output_dir,
            output_type=output_type,
        )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    matplotlib.use("Agg")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api-key",
        help="API key for pulling data from ICUBAM.",
        default=None,
    )
    parser.add_argument(
        "--matplotlib-style",
        help="matplotlib style used in generated plots.",
        default="seaborn-whitegrid",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory where the resulting plots will be stored.",
        default="/tmp/",
    )
    parser.add_argument(
        "--plots",
        nargs="*",
        help="Specific plots to generate (all are by default).",
        default=None,
    )
    parser.add_argument(
        "--output-type", choices=["tex", "png", "pdf"], default="png"
    )
    args = parser.parse_args()
    generate_plots(**args.__dict__)
