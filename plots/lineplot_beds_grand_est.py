import itertools

import matplotlib.cm
import matplotlib.gridspec
import matplotlib.patches
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import pandas as pd
import scipy.interpolate
import seaborn as sns

import tikzplotlib
import predicu.data
import predicu.plot

matplotlib.style.use("seaborn-darkgrid")

data = predicu.data.load_all_data()
data = data.loc[data.icu_name.isin(predicu.data.ICU_NAMES_GRAND_EST)]
n_occ = data.groupby("date").sum()["n_covid_occ"]
n_free = data.groupby("date").sum()["n_covid_free"]
n_transfered = (
    data.groupby("date").sum()["n_covid_transfered"].diff(1).fillna(0)
)
n_tot = n_occ + n_free
n_req = n_occ + n_transfered
fig, ax = plt.subplots(1, figsize=(18, 12))
x = np.arange(len(n_req))

def plot_int(x, y, ax, marker="o", label=None, color="k", lw=1):
    interp = scipy.interpolate.interp1d
    f = interp(x, y, kind="quadratic")
    x_i = np.linspace(0, len(x) - 1, len(x) * 5)
    y_i = f(x_i)
    ax.scatter(x, y, marker=marker, label=label, color=color, lw=lw)
    ax.plot(x_i, y_i, color=color)
    return ax


ax = plot_int(
    x,
    n_tot.values,
    ax=ax,
    color=next(predicu.plot.RANDOM_COLORS),
    marker=next(predicu.plot.RANDOM_MARKERS),
    label="Total (lits)",
    lw=2,
)
ax = plot_int(
    x,
    n_req.values,
    ax=ax,
    color=next(predicu.plot.RANDOM_COLORS),
    marker=next(predicu.plot.RANDOM_MARKERS),
    label="Lits occupés + transferts",
    lw=2,
)
ax = plot_int(
    x,
    n_occ.values,
    ax=ax,
    color=next(predicu.plot.RANDOM_COLORS),
    marker=next(predicu.plot.RANDOM_MARKERS),
    label="Lits occupés",
    lw=2,
)
# n_transfered.plot(ax=ax, label="Transfered")
# n_transf
ax.set_ylabel(r"Nombre de lits")
ax.legend(loc='lower right')
ax.set_xticks(np.arange(data.date.unique().shape[0]))
ax.set_xticklabels(
    [date.strftime("%d-%m") for date in sorted(data.date.unique())],
    rotation=45,
)
# plt.show()
extra_axis_parameters = {
    # r"xticklabel style={font=\scriptsize}",
    # r"yticklabel style={font=\scriptsize}",
}
extra_tikzpicture_parameters = {
    # r"every axis legend/.code={\let\addlegendentry\relax}"
}
tikzplotlib.save(
    "reports/figs/lineplot_beds_grand_est.tex",
    standalone=True,
    axis_width="13.5cm",
    axis_height="7.2cm",
    extra_axis_parameters=extra_axis_parameters,
    extra_tikzpicture_parameters=extra_tikzpicture_parameters,
)
