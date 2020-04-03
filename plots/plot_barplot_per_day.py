import datetime

import matplotlib.gridspec
import matplotlib.pyplot as plt
import matplotlib.style
import pandas as pd
import numpy as np
import seaborn as sns
import tikzplotlib

import predicu.data
from predicu import load_all_data, load_pre_icubam_data
from predicu.data import CUM_COLUMNS
from predicu.plot import COLUMN_COLOR, COLUMN_TO_HUMAN_READABLE

matplotlib.style.use('seaborn-darkgrid')

icus = set(
  list(
    load_pre_icubam_data(predicu.data.DEFAULT_PRE_ICUBAM_PATH
                         ).icu_name.unique()
  )
)

print('nb of icus', len(icus))
print(sorted(list(icus)))

column_to_title = {
  'n_covid_deaths': 'Nombre de morts par jour en réanimation',
  'n_covid_healed': 'Nombre de sorties de réanimation par jour',
}

column = 'n_covid_deaths'
d = load_all_data()
__import__('pdb').set_trace()
d = d.loc[d.icu_name.isin(icus)]
d = d[['date', 'icu_name', 'department', column, 'datetime']]
d = d.groupby(['date', 'icu_name']).max().reset_index()
d = d.groupby(['date', 'department']).sum().reset_index()
d = d.loc[d.date < pd.to_datetime("2020-04-03")]
# d[column] = d[column].diff(1).fillna(d[column].iloc[0])
# __import__('pdb').set_trace()
fig, ax = plt.subplots(1, figsize=(20, 10))
sns.barplot(x='date', y=column, data=d, ax=ax)
# ax.set_title(column_to_title[column])
ax.axvline(6.5, c='red', alpha=0.7, ls='dotted', lw=2.0)
ax.set_xticklabels([date.strftime('%d/%m') for date in d.date.unique()],
                   rotation=45,
                   fontdict={'fontsize': 'x-small'})
ax.set_ylabel('Décès par jour et réanimation')
ax.set_xlabel(None)
txt = ax.text(6.5, 3.5, 'Début acquisition ICUBAM', fontsize='large')
txt.set_horizontalalignment('center')
# plt.show()
# tikzplotlib.save('reports/build/figs/barplot_deaths_per_day.tex', standalone=True)
