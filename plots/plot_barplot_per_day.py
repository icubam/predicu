import datetime

import matplotlib.gridspec
import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import seaborn as sns
import tikzplotlib

from predicu import load_all_data
from predicu.data import CUM_COLUMNS
from predicu.plot import COLUMN_COLOR, COLUMN_TO_HUMAN_READABLE

matplotlib.style.use('seaborn-darkgrid')

column_to_title = {
  'n_covid_deaths': 'Nombre de morts par jour en réanimation',
  'n_covid_healed': 'Nombre de sorties de réanimation par jour',
}

column = 'n_covid_deaths'
d = load_all_data()
fig, ax = plt.subplots(1, figsize=(20, 10))
sns.barplot(x='date', y=column, data=d, ax=ax)
# ax.set_title(column_to_title[column])
ax.axvline(7, c='gray', ls='dotted')
ax.set_xticklabels([date.strftime('%d/%m') for date in d.date.unique()],
                   rotation=45,
                   fontdict={'fontsize': 'x-small'})
ax.set_ylabel('Décès par jour et réanimation')
ax.set_xlabel(None)
txt = ax.text(7, 3.5, 'Début acquisition ICUBAM', fontsize='large')
txt.set_horizontalalignment('center')
tikzplotlib.save('reports/figs/barplot_deaths_per_day.tex', standalone=True)
