import pickle

import numpy as np
import pandas as pd


def load_and_preprocess_data(bedcount_path):
  ext = bedcount_path.rsplit('.', 1)[-1]
  if ext == 'pickle':
    with open(bedcount_path, 'rb') as f:
      d = pickle.load(f)
  elif ext == 'h5':
    d = pd.read_hdf(bedcount_path)
  elif ext == 'csv':
    d = pd.read_csv(bedcount_path)
  else:
    raise ValueError(f'unknown extension {ext}')
  # columns with cumulative values from which we will compute the per day diff
  cum_columns = [
    'n_covid_free', 'n_covid_occ', 'n_covid_deaths', 'n_covid_healed'
  ]
  max_increases = {
    'n_covid_free': 100,
    'n_covid_occ': 100,
    'n_covid_deaths': 100,
    'n_covid_healed': 100,
  }
  d['datetime'] = pd.to_datetime(d['date'])
  d['date'] = pd.to_datetime(d['date']).dt.date
  clean_data_points = list()
  per_icu_prev_data_point = dict()
  for date in sorted(d['date'].unique()):
    date_d = d.loc[d['date'] == date]
    for icu_name in d['icu_name'].unique():
      new_data_point = {'date': date, 'icu_name': icu_name}
      new_data_point.update({col: 0 for col in cum_columns})
      date_icu_d = date_d.loc[date_d['icu_name'] == icu_name]
      if len(date_icu_d) > 0:
        date_icu_d = date_icu_d.sort_values(by='datetime')
        prev_data_point = per_icu_prev_data_point.get(icu_name, None)
        if prev_data_point is None:
          new_data_point.update({
            col: date_icu_d[col].iloc[-1]
            for col in cum_columns
          })
        else:
          for col in cum_columns:
            for candidate in reversed(list(date_icu_d[col])):
              if candidate > prev_data_point[col]:
                increase = candidate - prev_data_point[col]
                if increase <= max_increases[col]:
                  new_data_point[col] = increase
                  break
      clean_data_points.append(new_data_point)
      per_icu_prev_data_point[icu_name] = new_data_point
  return pd.DataFrame(clean_data_points)
