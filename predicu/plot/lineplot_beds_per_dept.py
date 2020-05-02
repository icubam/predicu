import matplotlib.patches
import matplotlib.pyplot as plt
import numpy as np

from predicu.data import BEDCOUNT_COLUMNS
from predicu.plot import DEPARTMENT_COLOR, RANDOM_MARKERS, plot_int

data_source = ["bedcounts"]


def plot(data):
    agg = {col: "sum" for col in BEDCOUNT_COLUMNS}
    data = data.groupby(["date", "department"]).agg(agg)
    data = data.reset_index()
    fig, ax = plt.subplots(1, figsize=(7, 4))
    for department, dg in data.groupby("department"):
        dg = dg.sort_values(by="date")
        x = np.arange(len(dg))
        y = dg.n_covid_occ.values  # + dg.n_covid_transfered.diff(1).fillna(0)
        plot_int(
            x,
            y,
            ax=ax,
            color=DEPARTMENT_COLOR[department],
            label=department,
            lw=2,
            marker=next(RANDOM_MARKERS),
        )
    dates = np.array(sorted(data.date.unique().flatten()))
    xticks = np.arange(0, len(dates), 3)
    ax.set_xticks(xticks)
    ax.set_xticklabels(
        [date.strftime("%d-%m") for date in dates[xticks]], rotation=45,
    )
    ax.legend(
        ncol=2,
        handles=[
            matplotlib.patches.Patch(
                facecolor=DEPARTMENT_COLOR[dpt], label=dpt, linewidth=3,
            )
            for dpt in sorted(data.department.unique())
        ],
        loc="upper left",
    )
    ax.set_ylabel(r"Occupied beds + transfers")
    tikzplotlib_kwargs = dict(axis_width="15cm", axis_height="8cm",)
    return fig, tikzplotlib_kwargs
