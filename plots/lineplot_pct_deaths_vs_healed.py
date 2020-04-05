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
data = data.groupby(["date"]).agg(agg)
data = data.sort_index().reset_index()
data["pct_deaths"] = data["n_covid_deaths"] / (
    data["n_covid_deaths"] + data["n_covid_healed"]
)
data["pct_healed"] = data["n_covid_healed"] / (
    data["n_covid_healed"] + data["n_covid_deaths"]
)

fig, ax = plt.subplots(1, figsize=(7, 4))
for col in ["pct_deaths", "pct_healed"]:
    predicu.plot.plot_int(
        np.arange(len(data)),
        data[col],
        ax=ax,
        color=predicu.plot.COL_COLOR[col],
        label=predicu.plot.COLUMN_TO_HUMAN_READABLE[col],
        marker=next(predicu.plot.RANDOM_MARKERS),
        lw=2,
    )
ax.set_xticks(np.arange(data.date.unique().shape[0]))
ax.set_xticklabels(
    [date.strftime("%d-%m") for date in sorted(data.date.unique())],
    rotation=45,
)
ax.set_ylabel("Pourcentage")
ax.legend()

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
    "reports/figs/lineplot_pct_deaths_vs_healed.tex",
    standalone=True,
    axis_width="14cm",
    axis_height="6cm",
    extra_axis_parameters=extra_axis_parameters,
    extra_tikzpicture_parameters=extra_tikzpicture_parameters,
)
