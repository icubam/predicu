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
from predicu import load_all_data, load_pre_icubam_data
from predicu.data import CUM_COLUMNS, NCUM_COLUMNS, load_icu_name_to_department
from predicu.plot import COLUMN_TO_HUMAN_READABLE

matplotlib.style.use("seaborn-darkgrid")

pre_icubam_data = load_pre_icubam_data()
grand_est_icu_names = set(pre_icubam_data.icu_name.unique())
data = load_all_data()
data = data.loc[data.icu_name.isin(grand_est_icu_names)]

agg = {col: 'sum' for col in CUM_COLUMNS + NCUM_COLUMNS}
data = data.groupby(["date", "department"]).agg(agg)
data = data.reset_index()

unique_dpts = sorted(data.department.unique())
# colors = matplotlib.cm.bright(np.linspace(1, 0, len(unique_dpts)))
colors = itertools.cycle(sns.color_palette("bright"))
dpt2color = dict(zip(unique_dpts, colors))
marker = itertools.cycle(('x', '+', '1', '.', '|', '3', '2'))

def plot_int(x, y, ax, marker="o", label=None, color="k"):
    interp = scipy.interpolate.interp1d
    f = interp(x, y, kind="quadratic")
    x_i = np.linspace(0, len(x) - 1, len(x) * 5)
    y_i = f(x_i)
    ax.scatter(x, y, marker=marker, label=label, color=color)
    ax.plot(x_i, y_i, color=color)
    return ax


fig, ax = plt.subplots(1, figsize=(10, 6))
# for col in CUM_COLUMNS + ["n_covid_occ"]:
    # color = next(colors)
    # x = np.arange(len(data))
    # y = data[col].values
    # plot_int(
        # x,
        # y,
        # ax=ax,
        # color=color,
        # marker="*",
        # label=COLUMN_TO_HUMAN_READABLE[col],
    # )

dfs = []
for dpt, d in data.groupby("department"):
    d = d.sort_values(by="date")
    d["charge"] = d[CUM_COLUMNS + ["n_covid_occ"]].diff(1).fillna(0).sum(axis=1)
    x = np.arange(len(d))
    y = d.charge.values
    dfs.append(d)
    d = pd.concat(dfs).groupby("date").sum().sort_index().reset_index()
    x = np.arange(len(d))
    y = d.charge.values
    plot_int(x, y, ax=ax, color=next(colors), marker=next(marker), label=dpt)

ax.set_xticks(np.arange(data.date.unique().shape[0]))
ax.set_xticklabels(
    [date.strftime("%d-%m") for date in sorted(data.date.unique())],
    rotation=45,
)
ax.legend(ncol=2, loc="upper left")
fig.tight_layout()
fig.savefig("fig.png")
# plt.show()

extra_axis_parameters = {
    # r"xticklabel style={font=\scriptsize}",
    # r"yticklabel style={font=\scriptsize}",
}
extra_tikzpicture_parameters = {
    # r"every axis legend/.code={\let\addlegendentry\relax}"
}
tikzplotlib.save(
    "/tmp/fig.tex",
    standalone=True,
    axis_width="10cm",
    axis_height="6cm",
    extra_axis_parameters=extra_axis_parameters,
    extra_tikzpicture_parameters=extra_tikzpicture_parameters,
)
