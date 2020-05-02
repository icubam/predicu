import matplotlib.pyplot as plt
import numpy as np

from predicu.data import BEDCOUNT_COLUMNS
from predicu.plot import (
    COL_COLOR,
    COLUMN_TO_HUMAN_READABLE,
    RANDOM_MARKERS,
    plot_int,
)

data_source = ["bedcounts"]


def plot(data):
    agg = {col: "sum" for col in BEDCOUNT_COLUMNS}
    data = data.groupby(["date"]).agg(agg)
    data = data.sort_index().reset_index()
    fig, ax = plt.subplots(1, figsize=(7, 4))
    for col in ["n_covid_deaths", "n_covid_healed"]:
        plot_int(
            np.arange(len(data)),
            data[col],
            ax=ax,
            color=COL_COLOR[col],
            label=COLUMN_TO_HUMAN_READABLE[col],
            marker=next(RANDOM_MARKERS),
            lw=2,
        )
    dates = np.array(sorted(data.date.unique().flatten()))
    xticks = np.arange(0, len(dates), 3)
    ax.set_xticks(xticks)
    ax.set_xticklabels(
        [date.strftime("%d-%m") for date in dates[xticks]], rotation=45,
    )
    ax.set_ylabel("Nombre de patients")
    ax.legend()
    tikzplotlib_kwargs = dict(axis_width="15cm", axis_height="6cm",)
    return fig, tikzplotlib_kwargs
