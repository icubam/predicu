import itertools

import numpy as np
import scipy
import seaborn

import predicu.data

COLUMN_TO_HUMAN_READABLE = {
    "n_covid_deaths": "Décès",
    "n_covid_healed": "Sorties",
    "n_covid_transfered": "Transferts",
    "n_covid_refused": "Refus",
    "n_covid_free": "Lits Covid+ libres",
    "n_ncovid_free": "Lits Covid- libres",
    "n_covid_occ": "Lits Covid+ occupés",
    "n_ncovid_occ": "Lits Covid- occupés",
    "flow": "Flux total de patients",
}

COL_COLOR = {
    col: seaborn.color_palette(
        "colorblind", len(predicu.data.BEDCOUNT_COLUMNS) + 1
    )[i]
    for i, col in enumerate(predicu.data.BEDCOUNT_COLUMNS + ["flow"])
}

DEPARTMENT_COLOR = {
    dpt: seaborn.color_palette("colorblind", len(predicu.data.DEPARTMENTS))[i]
    for i, dpt in enumerate(predicu.data.DEPARTMENTS)
}
DEPARTMENT_GRAND_EST_COLOR = {
    dpt: seaborn.color_palette(
        "colorblind", len(predicu.data.DEPARTMENTS_GRAND_EST)
    )[i]
    for i, dpt in enumerate(predicu.data.DEPARTMENTS_GRAND_EST)
}

RANDOM_MARKERS = itertools.cycle(("x", "+", "1", ".", "|", "3", "2"))

RANDOM_COLORS = itertools.cycle(seaborn.color_palette("colorblind", 10))


def plot_int(
    x,
    y,
    ax,
    marker=None,
    label=None,
    color=None,
    lw=1.0,
    s=3,
    fill_below=False,
):
    f = scipy.interpolate.interp1d(x, y, kind="quadratic")
    x_i = np.linspace(0, len(x) - 1, len(x) * 5)
    y_i = f(x_i)
    # ax.scatter(x, y, marker=marker, color=color, s=s)
    if fill_below:
        ax.fill_between(x_i, np.zeros(len(y_i)), y_i, color=color, label=label)
        ax.plot(x_i, y_i, color="white", lw=1, ls="solid", alpha=0.5)
    else:
        ax.plot(x_i, y_i, color=color, lw=lw, label=label)
    return ax
