import datetime

import matplotlib.gridspec
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import pandas as pd
import seaborn as sns
import tikzplotlib

import predicu.data
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
d = d.loc[d.date < pd.to_datetime("2020-04-03")]
d = d.groupby(["date", "department"]).sum().reset_index()
d = d.sort_values(by="date")
fig, ax = plt.subplots(1, figsize=(20, 10))

x = d.date.values
y = (
    d.n_covid_deaths.values
    / d.department.apply(predicu.data.load_department_population().get).values
    * 1e5
)

sns.barplot(x=x, y=y, ax=ax, ci='sd', capsize=.2)
ax.axvline(6.5, c="red", alpha=0.7, ls="dotted", lw=2.0)
ax.set_xticklabels(
    [date.strftime("%d/%m") for date in d.date.unique()],
    rotation=45,
    fontdict={"fontsize": "x-small"},
)
ax.set_ylabel("Décès (cumulés) par département")
ax.set_xlabel(None)
txt = ax.text(6.5, 32, "Début acquisition ICUBAM", fontsize="large")
txt.set_horizontalalignment("center")
plt.show()
# tikzplotlib.save(
    # "reports/build/figs/barplot_deaths_per_day.tex", standalone=True
# )
