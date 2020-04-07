import matplotlib.pyplot as plt
import matplotlib.style
import numpy as np
import pandas as pd
import seaborn as sns

import predicu.data
import tikzplotlib

matplotlib.style.use("seaborn-whitegrid")

d = predicu.data.load_data_file()
d = d.rename(columns={"create_date": "date"})
d = format_data(d)
counts = d.groupby(["date", "icu_name"]).datetime.count().values
fig, ax = plt.subplots(1, figsize=(12, 8))
sns.countplot(counts)
# ax.set_title('Distributions des nombres de saisies par date et par ICU')
ax.set_xlabel("Nombre de saisies dans la journée")
ax.set_ylabel("Compte par date et réanimation")
tikzplotlib.save("reports/figs/n_inputs_countplot.tex", standalone=True)
