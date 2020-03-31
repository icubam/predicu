import pickle

import numpy as np
import pandas as pd

CUM_COLUMNS = [
  'n_covid_free', 'n_covid_occ', 'n_covid_deaths', 'n_covid_healed'
]

ALL_COLUMNS = ['icu_name', 'date', 'datetime'] + CUM_COLUMNS


def load_data_file(data_path):
  ext = data_path.rsplit('.', 1)[-1]
  if ext == 'pickle':
    with open(data_path, 'rb') as f:
      d = pickle.load(f)
  elif ext == 'h5':
    d = pd.read_hdf(data_path)
  elif ext == 'csv':
    d = pd.read_csv(data_path)
  else:
    raise ValueError(f'unknown extension {ext}')
  return d


def load_all_data(icubam_bedcount_path, pre_icubam_path):
  return pd.concat([
    load_pre_icubam_data(pre_icubam_path),
    load_icubam_bedcount_data(icubam_bedcount_path),
  ])


def load_pre_icubam_data(pre_icubam_path):
  d = load_data_file(pre_icubam_path)
  d = d.rename(
    columns={
      'Hopital': 'icu_name',
      'NbSortieVivant': 'n_covid_healed',
      'NbCOVID': 'n_covid_occ',
      'NbLitDispo': 'n_covid_free',
      'NbDeces': 'n_covid_deaths',
      'Date': 'date'
    }
  )
  fix_icu_names = {
    'C-SCweitzer': 'C-Schweitzer',
    'Bezannes': 'C-Bezannes',
    'NHC-Chir': 'NHC-ChirC',
    'CHR-SSPI': 'CHR-Thionville',
    'CHR-CCV': 'CHR-Thionville',
  }
  for wrong_name, fixed_name in fix_icu_names.items():
    d.loc[d.icu_name == wrong_name, 'icu_name'] = fixed_name
  d['datetime'] = pd.to_datetime(d['date'])
  d['date'] = d.datetime.dt.date
  return get_clean_daily_values(d[ALL_COLUMNS])


def load_icubam_bedcount_data(icubam_bedcount_path):
  d = load_data_file(icubam_bedcount_path)
  d['datetime'] = pd.to_datetime(d['date'])
  d['date'] = pd.to_datetime(d['date']).dt.date
  return get_clean_daily_values(d[ALL_COLUMNS])


def get_clean_daily_values(d):
  max_daily_increase = {
    'n_covid_free': 100,
    'n_covid_occ': 100,
    'n_covid_deaths': 100,
    'n_covid_healed': 100,
  }
  clean_data_points = list()
  per_icu_prev_data_point = dict()
  for date in sorted(d['date'].unique()):
    date_d = d.loc[d['date'] == date]
    for icu_name in d['icu_name'].unique():
      new_data_point = {'date': date, 'icu_name': icu_name}
      new_data_point.update({col: 0 for col in CUM_COLUMNS})
      date_icu_d = date_d.loc[date_d['icu_name'] == icu_name]
      if len(date_icu_d) > 0:
        date_icu_d = date_icu_d.sort_values(by='datetime')
        prev_data_point = per_icu_prev_data_point.get(icu_name, None)
        if prev_data_point is None:
          new_data_point.update({
            col: date_icu_d[col].iloc[-1]
            for col in CUM_COLUMNS
          })
        else:
          for col in CUM_COLUMNS:
            for candidate in reversed(list(date_icu_d[col])):
              if candidate > prev_data_point[col]:
                increase = candidate - prev_data_point[col]
                if increase <= max_daily_increase[col]:
                  new_data_point[col] = increase
                  break
      clean_data_points.append(new_data_point)
      per_icu_prev_data_point[icu_name] = new_data_point
  return pd.DataFrame(clean_data_points)
