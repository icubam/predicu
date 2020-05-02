import datetime
import logging
import os

import click

from predicu.data import load_bedcounts
from predicu.plot import generate_plots
from predicu.preprocessing import preprocess_bedcounts


@click.group()
def cli():
    pass


@cli.command(name="export")
@click.option("--output-dir", "-o", default="/tmp", type=str)
@click.option("--api-key", default=None)
@click.option("--spread-cum-jump-correction", default=False, type=bool)
@click.option("--icubam-host", default="localhost", type=str)
@click.option(
    "--max-date",
    default=None,
    help="max date of the exported data (e.g. 2020-04-05)",
    type=str,
)
def export_data_cli(
    output_dir, api_key, spread_cum_jump_correction, icubam_host, max_date
):
    export_data(
        output_dir, api_key, spread_cum_jump_correction, icubam_host, max_date
    )


def export_data(
    output_dir, api_key, spread_cum_jump_correction, icubam_host, max_date
):
    if not os.path.isdir(output_dir):
        logging.info("creating directory %s" % output_dir)
        os.makedirs(output_dir)
    logging.info("exporting data to %s" % output_dir)
    if not os.path.isdir(output_dir):
        raise IOError(f"Output dir `{output_dir}' does not exist.")
    datetimestr = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%M")
    filename = "predicu_data_preprocessed_{}.csv".format(datetimestr)
    path = os.path.join(output_dir, filename)
    d = load_bedcounts(api_key=api_key, icubam_host=icubam_host)
    d = preprocess_bedcounts(d, max_date=max_date)
    d.to_csv(path)
    logging.info("export DONE.")


@cli.command(
    name="plot", help="Specific plots to generate (all are by default).",
)
@click.option("--api-key", default=None)
@click.option("--icubam-host", default="localhost", type=str)
@click.option(
    "--matplotlib-style",
    help="matplotlib style used in generated plots.",
    default="seaborn-whitegrid",
)
@click.option(
    "--output-dir",
    "-o",
    default="/tmp",
    type=str,
    help="Directory where the resulting plots will be stored.",
)
@click.option(
    "--output-type",
    "--output-type",
    type=click.Choice(["tex", "png", "pdf"]),
    default="png",
)
@click.option(
    "--restrict-to-region",
    default=None,
    help="Whether to restrict the data a region. Valid values are: Grand-Est.",
)
@click.argument(
    "plots", nargs=-1,
)
def plot_cli(**kwargs):
    import matplotlib

    matplotlib.use("Agg")
    if not kwargs["plots"]:
        kwargs["plots"] = None
    generate_plots(**kwargs)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    cli()
