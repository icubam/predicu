import matplotlib.gridspec
import matplotlib.pyplot as plt
import matplotlib.style
import seaborn as sns
import tikzplotlib

from predicu import load_all_data
from predicu.data import CUM_COLUMNS

matplotlib.style.use('seaborn-whitegrid')

data = load_all_data()

n_rows = (len(CUM_COLUMNS) + len(CUM_COLUMNS) % 2) // 2

fig = plt.figure(figsize=(n_rows * 5, 10))
gs = matplotlib.gridspec.GridSpec(n_rows, 2)
ax0 = None
for i, col in enumerate(CUM_COLUMNS):
  ax = fig.add_subplot(gs[i // 2, i % 2], sharex=ax0)
  if ax0 is None: ax0 = ax
  for g, d in data.groupby('department'):
    d = d.groupby('date')[col].sum().sort_index().cumsum()
    ax.plot(d.index.values, d.values, label=g)
  ax.set_title(col)
  ax.legend(ncol=2, loc="upper left", frameon=True)
  dates = sorted(list(data.date.unique()))
  ax.set_xticks(dates)
  ax.set_xticklabels([date.strftime('%d/%m') for date in dates],
                     rotation=45,
                     fontdict={'fontsize': 'x-small'})
fig.suptitle('Grand Est cumsum on ICUs')
fig.tight_layout()
fig.savefig('fig.pdf')
