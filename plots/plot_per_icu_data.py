import matplotlib.gridspec
import matplotlib.pyplot as plt
import matplotlib.style
import seaborn as sns

from predicu import load_all_data
from predicu.data import CUM_COLUMNS

matplotlib.style.use('seaborn-whitegrid')

icubam_bedcount_path = 'data/bedcount_2020-03-31.pickle'
pre_icubam_path = 'data/pre_icubam_data.csv'
data = load_all_data(
  icubam_bedcount_path=icubam_bedcount_path, pre_icubam_path=pre_icubam_path
)

n_rows = (len(CUM_COLUMNS) + len(CUM_COLUMNS) % 2) // 2

fig = plt.figure(figsize=(n_rows * 7, 14))
gs = matplotlib.gridspec.GridSpec(n_rows, 2)
for i, col in enumerate(CUM_COLUMNS):
  ax = fig.add_subplot(gs[i // 2, (i + 1) % 2])
  sns.lineplot(x='date', y=col, data=data)
  ax.set_title(col)
fig.suptitle('Grand Est daily increases averaged over ICUs')
fig.tight_layout()
plt.show()
