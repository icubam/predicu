import matplotlib.pyplot as plt
import matplotlib.style
import pandas as pd
import numpy as np
import seaborn as sns
import tikzplotlib

from predicu.data import DEFAULT_ICUBAM_PATH, format_data, load_data_file

matplotlib.style.use('seaborn-darkgrid')

d = load_data_file(DEFAULT_ICUBAM_PATH)
d = d.rename(columns={'create_date': 'date'})
d = format_data(d)
counts = d.groupby(['date', 'icu_name']).datetime.count().values
fig, ax = plt.subplots(1, figsize=(12, 8))
sns.countplot(counts)
# ax.set_title('Distributions des nombres de saisies par date et par ICU')
ax.set_xlabel('Nombre de saisies dans la journée')
ax.set_ylabel('Compte par date et réanimation')
tikzplotlib.save('reports/figs/n_inputs_countplot.tex', standalone=True)
