import pandas as pd

import predicu.data

d = predicu.data.load_all_data(cache=False)
d = d.loc[d.date == pd.to_datetime("2020-03-31")]
d = d.loc[d.department == "Haut-Rhin"]
d = d.groupby("icu_name").last()
d = d.groupby("icu_name")[predicu.data.CUM_COLUMNS].last()
print(d)
