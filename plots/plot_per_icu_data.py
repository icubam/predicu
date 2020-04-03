import matplotlib.cm
import matplotlib.gridspec
import matplotlib.patches
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import seaborn as sns
import tikzplotlib

from predicu import load_all_data, load_pre_icubam_data
from predicu.data import CUM_COLUMNS, load_icu_name_to_department

matplotlib.style.use("seaborn-dark")

pre_icubam_data = load_pre_icubam_data()
grand_est_icu_names = set(pre_icubam_data.icu_name.unique())

data = load_all_data()
data = data.loc[data.icu_name.isin(grand_est_icu_names)]
# last known total number of deaths per icu
data = data.groupby("icu_name").n_covid_deaths.max()
# remove icus with zero deaths
data = data.loc[data > 0]
# sort values by nb of deaths (descending)
data = data.sort_values()
# reset index
data = data.reset_index()

icu2dpt = load_icu_name_to_department()
data["department"] = data["icu_name"].apply(icu2dpt.get)
data.groupby('department').n_covid_deaths.sum().reset_index()

unique_dpts = sorted(list(set(list(data["department"].unique()))))
colors = matplotlib.cm.Set2(np.linspace(1, 0, len(unique_dpts)))
dpt2color = dict(zip(unique_dpts, colors))

fig, ax = plt.subplots(1, figsize=(3, 8))

for i, row in data.iterrows():
    rect_patch = matplotlib.patches.Rectangle(
        xy=(0, i),
        width=row["n_covid_deaths"],
        height=1,
        fill=True,
        linewidth=0.7,
        edgecolor="white",
        facecolor=dpt2color[row["department"]],
        label=row["department"],
    )
    ax.add_patch(rect_patch)
    ax.text(
        row["n_covid_deaths"],
        i + 0.15,
        r"\Large{{{}}}".format(row["n_covid_deaths"]),
    )
ax.set_xlim(0, data["n_covid_deaths"].iloc[-1] + 3)
ax.set_ylim(0, len(data))
xticks = [5, 10, 15, 20]
for xtick in xticks:
    ax.axvline(x=xtick, ls="dashed", c="w")
ax.set_xticks(xticks)
ax.set_yticks(np.arange(len(data)) + 0.5)
ax.set_yticklabels(data.icu_name)
ax.legend(
    handles=[
        matplotlib.patches.Patch(facecolor=dpt2color[dpt], label=dpt)
        for dpt in unique_dpts
    ],
    loc="lower right",
)
# ax.set_title(r'Nbr de décès par réa (18 mars $\rightarrow$ 3 avril)')
# fig.savefig('fig.pdf')
extra_axis_parameters = {
    r"xticklabel style={font=\scriptsize}",
    r"yticklabel style={font=\scriptsize}",
}
extra_tikzpicture_parameters = {
    # r"every axis legend/.code={\let\addlegendentry\relax}"
}
tikzplotlib.save(
    "/tmp/fig.tex",
    standalone=True,
    axis_width="8cm",
    axis_height="12cm",
    textsize=8.0,
    extra_axis_parameters=extra_axis_parameters,
    extra_tikzpicture_parameters=extra_tikzpicture_parameters,
)
