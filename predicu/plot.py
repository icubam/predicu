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


def plot_int(x, y, ax, marker=None, label=None, color=None, lw=1.0):
    f = scipy.interpolate.interp1d(x, y, kind="quadratic")
    x_i = np.linspace(0, len(x) - 1, len(x) * 5)
    y_i = f(x_i)
    ax.scatter(x, y, marker=marker, label=label, color=color)
    ax.plot(x_i, y_i, color=color, lw=lw)
    return ax
