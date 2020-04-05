import datetime

import matplotlib.gridspec
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import pandas as pd
import seaborn as sns

import predicu.data
import tikzplotlib
from predicu import load_all_data, load_pre_icubam_data
from predicu.data import CUM_COLUMNS
from predicu.plot import COL_COLOR, COLUMN_TO_HUMAN_READABLE

matplotlib.style.use("seaborn-darkgrid")

icus = set(
    list(
        load_pre_icubam_data(
            predicu.data.DEFAULT_PRE_ICUBAM_PATH
        ).icu_name.unique()
    )
)

print("nb of icus", len(icus))
print(sorted(list(icus)))

column = "n_covid_deaths"
d = load_all_data()
d = d.loc[d.icu_name.isin(icus)]
d = d.groupby(["date", "department"]).sum().reset_index()
d = d.groupby('department').last().reset_index()

get_dpt_pop = predicu.data.load_department_population().get

d = d.sort_values(by="date")
fig, ax = plt.subplots(1, figsize=(20, 10))

x = d.n_covid_occ

x = d.date.values
y = (
    d.n_covid_deaths.values
    / d.department.apply(predicu.data.load_department_population().get).values
    * 1e5
)

sns.barplot(x=x, y=y, ax=ax, capsize=0.2)
ax.axvline(6.5, c="red", alpha=0.7, ls="dotted", lw=6.0)
ax.set_xticklabels(
    [date.strftime("%d/%m") for date in d.date.unique()],
    rotation=45,
    fontdict={"fontsize": "x-small"},
)
ax.set_ylabel("Décès par 100,000 habitants")
ax.set_xlabel(None)
txt = ax.text(6.5, 3.5, "Début acquisition", fontsize="xx-large", color="red")
txt.set_horizontalalignment("right")
txt = ax.text(6.5, 3.2, r"\texttt{ICUBAM}", fontsize="xx-large", color="red")
txt.set_horizontalalignment("right")
# plt.show()
# __import__("sys").exit()
extra_axis_parameters = {
    # r"xticklabel style={font=\tiny}",
}
extra_tikzpicture_parameters = {
    # r"every axis legend/.code={\let\addlegendentry\relax}"
}
tikzplotlib.save(
    "reports/figs/barplot_deaths_per_day.tex",
    standalone=True,
    axis_width="10cm",
    axis_height="6cm",
    extra_axis_parameters=extra_axis_parameters,
    extra_tikzpicture_parameters=extra_tikzpicture_parameters,
)
