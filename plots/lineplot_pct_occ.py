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
import predicu.plot
import tikzplotlib

matplotlib.style.use("seaborn-darkgrid")

data = predicu.data.load_all_data()
data = data.loc[data.icu_name.isin(predicu.data.ICU_NAMES_GRAND_EST)]
agg = {col: "sum" for col in predicu.data.BEDCOUNT_COLUMNS}
data = data.groupby(["date", "department"]).agg(agg)
data = data.reset_index()


def compute_pct_occ(d):
    return (d["n_covid_occ"] / (d["n_covid_occ"] + d["n_covid_free"])).fillna(
        0
    )


data["pct_occ"] = compute_pct_occ(data)

fig, ax = plt.subplots(1, figsize=(7, 4))

date_idx_range = np.arange(len(data.date.unique()))
for department, d in data.groupby("department"):
    d = d.sort_values(by="date")
    predicu.plot.plot_int(
        date_idx_range,
        d["pct_occ"],
        ax=ax,
        color=predicu.plot.DEPARTMENT_GRAND_EST_COLOR[department],
        label=department,
        lw=2,
    )

ge_pct_occ = data.groupby("date").pct_occ.mean().sort_index().values
predicu.plot.plot_int(
    date_idx_range,
    ge_pct_occ,
    ax=ax,
    color="k",
    marker=False,
    label="Grand Est",
    lw=4,
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
            facecolor=predicu.plot.DEPARTMENT_GRAND_EST_COLOR[department],
            label=department,
            linewidth=3,
        )
        for department in sorted(data.department.unique())
    ]
    + [
        matplotlib.patches.Patch(
            facecolor="k", label="Grand Est", linewidth=3,
        )
    ],
    loc="lower right",
)
# ax.set_ylabel('Pourcentage d\'occupations des lits Covid+')
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
    "reports/figs/lineplot_pct_occ.tex",
    standalone=True,
    axis_width="14cm",
    axis_height="8cm",
    extra_axis_parameters=extra_axis_parameters,
    extra_tikzpicture_parameters=extra_tikzpicture_parameters,
)