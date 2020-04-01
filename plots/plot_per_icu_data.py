import matplotlib.gridspec
import matplotlib.pyplot as plt
import matplotlib.style
import seaborn as sns

from predicu import load_all_data
from predicu.data import CUM_COLUMNS

matplotlib.style.use('seaborn-whitegrid')

data = load_all_data()

fig = plt.figure(figsize=(10, len(CUM_COLUMNS) * 10))
gs = matplotlib.gridspec.GridSpec(len(CUM_COLUMNS), 1)
ax0 = None
for i, col in enumerate(CUM_COLUMNS):
  ax = fig.add_subplot(gs[i, 0], sharex=ax0)
  if ax0 is None: ax0 = ax
  sns.lineplot(x='date', y=col, data=data)
  ax.set_title(col)
fig.suptitle('Grand Est daily increases averaged over ICUs')
fig.tight_layout()
fig.savefig('fig.pdf')
