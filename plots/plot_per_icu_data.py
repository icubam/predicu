import matplotlib.gridspec
import matplotlib.pyplot as plt
import matplotlib.style
import seaborn as sns

from predicu.data import load_all_data

matplotlib.style.use('seaborn-whitegrid')

icubam_bedcount_path = 'data/bedcount_2020-03-31.pickle'
pre_icubam_path = 'data/pre_icubam_data.csv'
data = load_all_data(
  icubam_bedcount_path=icubam_bedcount_path, pre_icubam_path=pre_icubam_path
)

columns = ['n_covid_free', 'n_covid_occ', 'n_covid_deaths', 'n_covid_healed']

fig = plt.figure(figsize=(20, 20))
gs = matplotlib.gridspec.GridSpec(2, 2)
for i, col in enumerate(columns):
  ax = fig.add_subplot(gs[i // 2, (i + 1) % 2])
  sns.lineplot(x='date', y=col, data=data)
  ax.set_title(col)
fig.suptitle('Grand Est daily increases averaged over ICUs')
plt.show()
