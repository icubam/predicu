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

import predicu.data
import predicu.flow
import predicu.plot
import tikzplotlib

matplotlib.style.use("seaborn-darkgrid")

data = predicu.data.load_all_data()
data = data.loc[data.icu_name.isin(predicu.data.ICU_NAMES_GRAND_EST)]
agg = {col: "sum" for col in predicu.data.BEDCOUNT_COLUMNS}
data = data.groupby(["date", "department"]).agg(agg)
data = data.reset_index()

fig, ax = plt.subplots(1, figsize=(7, 4))
date_idx_range = np.arange(len(data.date.unique()))
for department, dg in data.groupby("department"):
    dg = dg.sort_values(by="date")
    y = dg.n_covid_occ + dg.n_covid_transfered.diff(1).fillna(0)
    predicu.plot.plot_int(
        date_idx_range,
        y,
        ax=ax,
        color=predicu.plot.DEPARTMENT_GRAND_EST_COLOR[department],
        label=department,
        lw=2,
        marker=next(predicu.plot.RANDOM_MARKERS),
    )

ax.set_xticks(np.arange(data.date.unique().shape[0]))
ax.set_xticklabels(
    [date.strftime("%d-%m") for date in sorted(data.date.unique())],
    rotation=45,
)
ax.legend(
    ncol=2,
    handles=[
        matplotlib.patches.Patch(
            facecolor=predicu.plot.DEPARTMENT_GRAND_EST_COLOR[dpt],
            label=dpt,
            linewidth=3,
        )
        for dpt in sorted(data.department.unique())
    ],
    loc="upper left",
)
ax.set_ylabel(r'Somme lits occ. + transferts')
# fig.tight_layout()
# fig.savefig("fig.png")
# plt.show()
# __import__("sys").exit()

extra_axis_parameters = {
    # r"xticklabel style={font=\scriptsize}",
    # r"yticklabel style={font=\scriptsize}",
}
extra_tikzpicture_parameters = {
    # r"every axis legend/.code={\let\addlegendentry\relax}"
}
tikzplotlib.save(
    "reports/figs/lineplot_beds_per_dept.tex",
    standalone=True,
    axis_width="15cm",
    axis_height="8cm",
    extra_axis_parameters=extra_axis_parameters,
    extra_tikzpicture_parameters=extra_tikzpicture_parameters,
)
