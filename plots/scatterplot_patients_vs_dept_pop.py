import datetime
import json

import matplotlib.gridspec
import matplotlib.lines
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import pandas as pd
import seaborn as sns

import predicu.data
import tikzplotlib

matplotlib.style.use("seaborn-darkgrid")

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
combined = combined.loc[combined.date == di.date.max()]

fig, ax = plt.subplots(1, figsize=(20, 10))

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
    "Meuse": "above",
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
ax.legend()

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
    extra_axis_parameters=extra_axis_parameters,
    extra_tikzpicture_parameters=extra_tikzpicture_parameters,
)
