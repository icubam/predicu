import itertools

import matplotlib.cm
import matplotlib.gridspec
import matplotlib.patches
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import scipy.interpolate
import seaborn as sns

import tikzplotlib
from predicu import load_all_data, load_pre_icubam_data
from predicu.data import CUM_COLUMNS, NCUM_COLUMNS, load_icu_name_to_department

matplotlib.style.use("seaborn-darkgrid")

pre_icubam_data = load_pre_icubam_data()
grand_est_icu_names = set(pre_icubam_data.icu_name.unique())

column = "n_covid_free"

agg = dict()
agg.update({col: "max" for col in CUM_COLUMNS})
agg.update({col: "sum" for col in NCUM_COLUMNS})

data = load_all_data()
data = data.loc[data.icu_name.isin(grand_est_icu_names)]
data = data.groupby(["date", "department"]).agg(agg)
data = data.reset_index()

unique_dpts = sorted(data.department.unique())
# colors = matplotlib.cm.bright(np.linspace(1, 0, len(unique_dpts)))
colors = itertools.cycle(sns.color_palette("bright"))
dpt2color = dict(zip(unique_dpts, colors))
marker = itertools.cycle(("*", "d", "P"))


def plot_int(x, y, ax, marker="o", label=None, color='k'):
    interp = scipy.interpolate.interp1d
    f = interp(x, y, kind="quadratic")
    x_i = np.linspace(0, len(x) - 1, len(x) * 5)
    y_i = f(x_i)
    ax.scatter(x, y, marker=marker, color=color)
    ax.plot(x_i, y_i, color=color, label=label)
    return ax


fig, ax = plt.subplots(1, figsize=(10, 10))

for dpt, d in data.groupby("department"):
    d["charge"] = d[CUM_COLUMNS].sum(axis=1).diff(1).fillna(0) + d.n_covid_occ
    d = d.sort_values(by="date")
    print(d.shape)
    x = np.arange(len(d))
    y = d.charge.values
    # bp = x[(x % 5) == 0]
    # pp = scipy.interpolate.PPoly.from_spline(
        # scipy.interpolate.splrep(x[bp], y[bp])
    # )
    plot_int(x, y, ax=ax, color=dpt2color[dpt], marker=next(marker), label=dpt)
    # ax.scatter(x, y, c=dpt2color[dpt], marker=next(marker), label=dpt, s=3)
    # ax.plot(x, y, alpha=1.0, c=dpt2color[dpt], lw=0.5)
    # xi = np.linspace(0, len(d) - 1, 20)
    # yi = pp(xi)
    # ax.plot(xi, yi, ls="solid", c=dpt2color[dpt], lw=1.5)
ax.legend(ncol=2, loc="upper left")
# fig.savefig('fig.png')
# plt.show()

ax.set_xticks(np.arange(data.date.unique().shape[0]))
ax.set_xticklabels(
    [date.strftime("%d-%m") for date in sorted(data.date.unique())],
    rotation=45,
)

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
    axis_width="14cm",
    axis_height="10cm",
    extra_axis_parameters=extra_axis_parameters,
    extra_tikzpicture_parameters=extra_tikzpicture_parameters,
)
