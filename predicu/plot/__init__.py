import os

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
