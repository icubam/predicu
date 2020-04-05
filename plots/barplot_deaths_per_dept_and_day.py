import itertools
import sys

import matplotlib.cm
import matplotlib.gridspec
import matplotlib.patches
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import pandas as pd
import seaborn as sns

import predicu.data
import predicu.plot
import tikzplotlib

matplotlib.style.use("seaborn-dark")

data = predicu.data.load_all_data()
data = data.loc[data.icu_name.isin(predicu.data.ICU_NAMES_GRAND_EST)]
data = (
    data.groupby(["date", "department"])
    .agg({col: "sum" for col in predicu.data.BEDCOUNT_COLUMNS})
    .reset_index()
)
dfs = []
for department, d in data.groupby("department"):
    d = d.sort_values(by="date")
    d["n_covid_deaths_per_day"] = d.n_covid_deaths.diff(1).fillna(0)
    dfs.append(d.reset_index())
data = pd.concat(dfs)

col = "n_covid_deaths_per_day"
sorted_depts = sorted(data.department.unique())
fig, ax = plt.subplots(1, figsize=(8, 8))
for i, (date, d_date) in enumerate(
    data.sort_values(by="date").groupby("date")
):
    for j, department in enumerate(sorted_depts):
        d_dept = d_date.loc[d_date.department == department]
        height = d_date[d_date.department.isin(sorted_depts[j:])][col].sum()
        rect_patch = matplotlib.patches.Rectangle(
            xy=(i, 0),
            width=1,
            height=height,
            fill=True,
            linewidth=0.7,
            edgecolor="white",
            facecolor=predicu.plot.DEPARTMENT_GRAND_EST_COLOR[department],
            label=department,
        )
        ax.add_patch(rect_patch)
ax.set_xlim(0, len(data.date.unique()))
ax.set_xticks(np.arange(len(data.date.unique())) + 0.5)
ax.set_xticklabels(
    [date.strftime("%d-%m") for date in sorted(data.date.unique())],
    rotation=45,
)
ax.set_ylim(0, data.groupby(["date"])[col].sum().max() + 5)
ax.set_ylabel("Décès par jour")
yticks = np.arange(0, 20, 5)
for ytick in yticks:
    ax.axhline(y=ytick, ls="dashed", c="w")
ax.set_yticks(yticks)
ax.legend(
    ncol=2,
    handles=[
        matplotlib.patches.Patch(
            facecolor=predicu.plot.DEPARTMENT_GRAND_EST_COLOR[dept],
            label=dept,
        )
        for dept in reversed(sorted_depts)
    ],
    loc="upper left",
)

# plt.show()
# __import__("sys").exit()

# ax.set_title(r'Nbr de décès par réa (18 mars $\rightarrow$ 3 avril)')
extra_axis_parameters = {
    # r"xticklabel style={font=\scriptsize}",
    # r"yticklabel style={font=\scriptsize}",
}
extra_tikzpicture_parameters = {
    # r"every axis legend/.code={\let\addlegendentry\relax}"
}
tikzplotlib.save(
    "reports/figs/barplot_deaths_per_dept_and_day.tex",
    standalone=True,
    axis_width="14cm",
    axis_height="10cm",
    textsize=5.0,
    extra_axis_parameters=extra_axis_parameters,
    extra_tikzpicture_parameters=extra_tikzpicture_parameters,
)
