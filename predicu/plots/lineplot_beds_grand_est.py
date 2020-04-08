import datetime
import itertools

import matplotlib.cm
import matplotlib.gridspec
import matplotlib.patches
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import pandas as pd

import predicu.data
import predicu.plot


def plot(**plot_args):
    data = predicu.data.load_all_data(api_key=plot_args["api_key"])
    data = data.loc[data.icu_name.isin(predicu.data.ICU_NAMES_GRAND_EST)]
    n_occ = data.groupby("date").sum()["n_covid_occ"]
    n_free = data.groupby("date").sum()["n_covid_free"]
    n_transfered = (
        data.groupby("date").sum()["n_covid_transfered"].diff(1).fillna(0)
    )
    n_tot = n_occ + n_free
    n_req = n_occ + n_transfered
    fig, ax = plt.subplots(1, figsize=(18, 12))

    x_icubam_beg = np.argwhere(
        np.sort(data.date.unique()) == datetime.date(2020, 3, 25)
    ).flatten()[0]
    ax.axvline(x=x_icubam_beg, c="red", lw=7, ls="dashed")
    text = ax.text(
        x=x_icubam_beg - 0.5,
        y=n_tot.max() * 0.95,
        s=r"Début \texttt{ICUBAM}",
        fontsize="xx-large",
        fontweight="bold",
        color="red",
    )
    text.set_horizontalalignment("right")

    date_range_idx = np.arange(len(n_req))

    ax = predicu.plot.plot_int(
        date_range_idx,
        n_tot.values,
        ax=ax,
        color=next(predicu.plot.RANDOM_COLORS),
        marker=next(predicu.plot.RANDOM_MARKERS),
        label="Total (lits)",
        lw=2,
    )
    ax = predicu.plot.plot_int(
        date_range_idx,
        n_req.values,
        ax=ax,
        color=next(predicu.plot.RANDOM_COLORS),
        marker=next(predicu.plot.RANDOM_MARKERS),
        label="Lits occupés + transferts",
        lw=2,
    )
    ax = predicu.plot.plot_int(
        date_range_idx,
        n_occ.values,
        ax=ax,
        color=next(predicu.plot.RANDOM_COLORS),
        marker=next(predicu.plot.RANDOM_MARKERS),
        label="Lits occupés",
        lw=2,
    )
    ax.set_ylabel(r"Nombre de lits")
    ax.legend(loc="lower right")
    ax.set_xticks(np.arange(data.date.unique().shape[0]))
    ax.set_xticklabels(
        [date.strftime("%d-%m") for date in sorted(data.date.unique())],
        rotation=45,
    )
    tikzplotlib_kwargs = dict(axis_width="13.5cm", axis_height="7.2cm",)
    return fig, tikzplotlib_kwargs