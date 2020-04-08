import os
from typing import Optional, List
import logging

import matplotlib.style

PLOTS = []
for path in os.listdir(os.path.dirname(__file__)):
    if path.endswith(".py") and any(
        path.startswith(prefix)
        for prefix in ["barplot", "lineplot", "scatterplot", "stackplot"]
    ):
        plot_name = path.rsplit(".", 1)[0]
        PLOTS.append(plot_name)


def plot(plot_name, **plot_args):
    plot_fun = __import__(
        f"predicu.plots.{plot_name}", globals(), locals(), ["plot"], 0
    ).plot
    matplotlib.style.use(plot_args["matplotlib_style"])
    fig, tikzplotlib_kwargs = plot_fun(api_key=plot_args["api_key"])
    output_type = plot_args["output_type"]
    if plot_args["output_type"] == "tex":
        output_path = os.path.join(plot_args["output_dir"], f"{plot_name}.tex")
        __import__("tikzplotlib").save(
            filepath=output_path,
            figure=fig,
            **tikzplotlib_kwargs,
            standalone=True,
        )
    elif output_type in ["png", "pdf"]:
        fig.savefig(
            os.path.join(plot_args["output_dir"], f"{plot_name}.{output_type}")
        )
    else:
        raise ValueError(f"Unknown output type: {output_type}")


def generate_plots(
    plots: Optional[List[str]] = None,
    matplotlib_style: str = "seaborn-whitegrid",
    api_key: Optional[str] = None,
    output_type: str = "png",
    output_dir: str = "/tmp/",
):
    # Note: the default values here should match the defaults in CLI below.
    if plots is None:
        plots = PLOTS

    plots_unknown = set(plots).difference(PLOTS)
    if plots_unknown:
        raise ValueError(
            "Unknown plot(s): {}".format(", ".join(plots_unknown))
        )
    for name in sorted(plots):
        logging.info("generating plot %s in %s" % (name, output_dir))
        plot(
            name,
            api_key=api_key,
            matplotlib_style=matplotlib_style,
            output_dir=output_dir,
            output_type=output_type,
        )
