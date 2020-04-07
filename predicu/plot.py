import itertools

import numpy as np
import scipy
import seaborn

import predicu.data

COLUMN_TO_HUMAN_READABLE = {
    "n_covid_deaths": "Décès",
    "n_covid_healed": "Sorties de réa",
    "n_covid_transfered": "Transferts (autre réa)",
    "n_covid_refused": "Refus (faute de place)",
    "n_covid_free": "Lits Covid+ libres",
    "n_ncovid_free": "Lits Covid- libres",
    "n_covid_occ": "Lits Covid+ occupés",
    "n_ncovid_occ": "Lits Covid- occupés",
    "flow": "Flux total de patients",
    "pct_deaths": "Pourcentage de décès",
    "pct_healed": "Pourcentage de sorties",
}

COL_COLOR = {
    col: seaborn.color_palette(
        "colorblind", len(predicu.data.BEDCOUNT_COLUMNS) + 1
    )[i]
    for i, col in enumerate(predicu.data.BEDCOUNT_COLUMNS + ["flow"])
}
COL_COLOR.update(
    {
        "n_covid_deaths": (0, 0, 0),
        "n_covid_healed": (
            0.00784313725490196,
            0.6196078431372549,
            0.45098039215686275,
        ),
        "n_covid_occ": (0.8, 0.47058823529411764, 0.7372549019607844),
        "n_covid_transfered": (
            0.00392156862745098,
            0.45098039215686275,
            0.6980392156862745,
        ),
        "n_covid_refused": (0.8352941176470589, 0.3686274509803922, 0.0),
        "pct_deaths": (0, 0, 0),
        "pct_healed": (
            0.00784313725490196,
            0.6196078431372549,
            0.45098039215686275,
        ),
    }
)
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
RANDOM_MARKERS = itertools.cycle(("x", "+", ".", "|"))
RANDOM_COLORS = itertools.cycle(seaborn.color_palette("colorblind", 10))


def plot_int(
    x,
    y,
    ax,
    marker=None,
    label=None,
    color=None,
    lw=1.0,
    ls="solid",
    s=3,
    fill_below=False,
):
    f = scipy.interpolate.interp1d(x, y, kind="quadratic")
    x_i = np.linspace(0, len(x) - 1, len(x) * 5)
    y_i = f(x_i)
    if marker is not None:
        ax.scatter(x, y, marker=marker, color=color)
    if fill_below:
        ax.fill_between(x_i, np.zeros(len(y_i)), y_i, color=color, label=label)
        ax.plot(x_i, y_i, color="white", lw=1, ls="dashed", alpha=1.0)
    else:
        ax.plot(x_i, y_i, color=color, lw=lw, label=label, ls=ls)
    return ax
