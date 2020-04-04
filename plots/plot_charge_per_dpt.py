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


grp_column = "department"

agg = {col: "sum" for col in CUM_COLUMNS + NCUM_COLUMNS}
data = data.groupby(["date", grp_column]).agg(agg)
data = data.reset_index()

colors = itertools.cycle(sns.color_palette("bright"))
marker = itertools.cycle(("x", "+", "1", ".", "|", "3", "2"))


def compute_charge(d):
    return np.clip(
        d[CUM_COLUMNS + ["n_covid_occ"]].sum(axis=1).diff(1).fillna(0), 0, 1e6
    )


fig, ax = plt.subplots(1, figsize=(7, 4))
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
x = np.arange(len(data.date.unique()))

for grp, d in data.groupby(grp_column):
    d = d.sort_values(by="date")
    d["charge"] = compute_charge(d)
    plot_int(
        x,
        d.charge.cumsum().values,
        ax=ax,
        color=next(colors),
        marker=next(marker),
        label=grp,
        lw=1,
    )

ge = data.groupby("date").agg(agg).sort_index().reset_index()
ge["charge"] = compute_charge(ge)

plot_int(
    x,
    ge.charge.cumsum().values,
    ax=ax,
    color=next(colors),
    marker=None,
    label="Grand Est",
    lw=1,
)

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
