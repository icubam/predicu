import datetime
import json

import matplotlib.gridspec
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import pandas as pd
import seaborn as sns

import predicu.data
import tikzplotlib

matplotlib.style.use("seaborn-darkgrid")

public_data = predicu.data.load_public_data()

public_data["department"] = public_data.department_code.apply(
    predicu.data.CODE_TO_DEPARTMENT.get
)
public_data = public_data.loc[
    public_data.department.isin(predicu.data.DEPARTMENTS_GRAND_EST)
]

d = predicu.data.load_all_data()
d = d.loc[d.icu_name.isin(predicu.data.ICU_NAMES_GRAND_EST)]
public_data = public_data.loc[public_data.date == d.date.max()]
d = d.groupby(["date", "department"]).sum().reset_index()
d = d.groupby("department").last().reset_index()
d["department_code"] = d.department.apply(predicu.data.DEPARTMENT_TO_CODE.get)

__import__("pdb").set_trace()

get_dpt_pop = predicu.data.load_department_population().get

fig, ax = plt.subplots(1, figsize=(20, 10))

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
    axis_width="10cm",
    axis_height="6cm",
    extra_axis_parameters=extra_axis_parameters,
    extra_tikzpicture_parameters=extra_tikzpicture_parameters,
)
