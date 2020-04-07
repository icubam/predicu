import datetime
import json

import matplotlib.gridspec
import matplotlib.lines
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import pandas as pd
import scipy.stats
import seaborn as sns

import predicu.data
import predicu.plot
import tikzplotlib

matplotlib.style.use("seaborn-whitegrid")

combined = predicu.data.load_combined_icubam_public()
icubam_public_n_icu_patients_corr = (
    combined.groupby("date")[
        ["n_icu_patients_icubam", "n_icu_patients_public"]
    ]
    .corr()
    .iloc[0::2, -1]
    .reset_index()
    .set_index("date")
    .rename(
        columns={"n_icu_patients_public": "corr_icubam_public_n_icu_patients"}
    )
)
combined = combined.loc[combined.date == combined.date.max()]

c_public = next(predicu.plot.RANDOM_COLORS)
c_icubam = next(predicu.plot.RANDOM_COLORS)


fig, ax = plt.subplots(1, figsize=(20, 10))
ax.set_xlim(0, combined.department_pop.max() * 1.1)
ax.set_ylim(0, combined.n_icu_patients_public.max() * 1.1)

for c, y in [
    (c_public, combined.n_icu_patients_public),
    (c_icubam, combined.n_icu_patients_icubam),
]:
    x = combined.department_pop
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    slope, _, _, _ = np.linalg.lstsq(x[:, np.newaxis], y)
    x = np.linspace(0, x.max(), 100)
    y = slope[0] * x
    x = x[y >= 0]
    y = y[y >= 0]
    ax.plot(x, y, lw=3, ls="dashed", color=c, alpha=0.4)

ax.scatter(
    combined.department_pop,
    combined.n_icu_patients_public,
    label="Donnée publique",
    s=combined.n_icu_patients_public,
)
ax.scatter(
    combined.department_pop,
    combined.n_icu_patients_icubam,
    label="Donnée ICUBAM",
    s=combined.n_icu_patients_icubam,
)


dept_name_pos = {
    "Bas-Rhin": "left",
    "Ardennes": "above",
    "Meuse": "left",
    "Haute-Marne": "below",
    "Aube": "below",
}

for _, row in combined.iterrows():
    line = matplotlib.lines.Line2D(
        xdata=[row.department_pop, row.department_pop],
        ydata=[row.n_icu_patients_public, row.n_icu_patients_icubam],
    )
    ax.add_line(line)
    x = row.department_pop + 10000
    y = np.abs(row.n_icu_patients_icubam + row.n_icu_patients_public) / 2
    ha = "left"
    if row.department in dept_name_pos:
        if dept_name_pos[row.department] == "above":
            x = row.department_pop
            y = max(row.n_icu_patients_icubam, row.n_icu_patients_public) + 10
            ha = "center"
        elif dept_name_pos[row.department] == "left":
            x = row.department_pop - 10000
            ha = "right"
        elif dept_name_pos[row.department] == "below":
            x = row.department_pop
            y = min(row.n_icu_patients_icubam, row.n_icu_patients_public) - 10
            ha = "center"
    text = ax.text(x, y, row.department)
    text.set_horizontalalignment(ha)
ax.set_ylabel("Patients en réanimation (total)")
ax.set_xlabel("Habitants départementaux")
ax.legend(loc="upper left")

# plt.show()
# __import__("sys").exit()
extra_axis_parameters = {
    # r"xticklabel style={font=\tiny}",
}
extra_tikzpicture_parameters = {
    # r"every axis legend/.code={\let\addlegendentry\relax}"
}
tikzplotlib.save(
    "reports/figs/scatterplot_patients_vs_dept_pop.tex",
    standalone=True,
    axis_width="12cm",
    axis_height="8cm",
    textsize=7.0,
    extra_axis_parameters=extra_axis_parameters,
    extra_tikzpicture_parameters=extra_tikzpicture_parameters,
)
