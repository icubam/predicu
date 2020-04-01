import itertools
import json
import pickle

import numpy as np
import pandas as pd

DEFAULT_ICUBAM_PATH = 'data/bedcount_2020-03-31.pickle'
DEFAULT_PRE_ICUBAM_PATH = 'data/pre_icubam_data.csv'
DEFAULT_ICU_NAME_TO_DEPARTMENT_PATH = 'data/icu_name_to_department.json'

CUM_COLUMNS = [
  "n_covid_free",
  "n_ncovid_free",
  "n_covid_occ",
  "n_covid_deaths",
  "n_covid_healed",
  "n_covid_transfered",
  "n_covid_refused",
]

ALL_COLUMNS = ["icu_name", "date", "department"] + CUM_COLUMNS

MAX_DAY_INCREASE = {
  "n_covid_free": 20,
  "n_ncovid_free": 20,
  "n_covid_occ": 20,
  "n_covid_deaths": 5,
  "n_covid_healed": 5,
  "n_covid_transfered": 20,
  "n_covid_refused": 200,
}


def load_all_data(
  icubam_path=DEFAULT_ICUBAM_PATH, pre_icubam_path=DEFAULT_PRE_ICUBAM_PATH
):
  pre_icubam = load_pre_icubam_data(pre_icubam_path)
  fix_same_icu = {
    "CHR-SSPI": "CHR-Thionville",
    "CHR-CCV": "CHR-Thionville",
    "Nancy-NC": "Nancy-RCP"
  }
  for old, new in fix_same_icu.items():
    pre_icubam.loc[pre_icubam.icu_name == old, "icu_name"] = new
  pre_icubam = pre_icubam.groupby(["date", "icu_name"]).sum().reset_index()
  pre_icubam = pre_icubam.sort_values(by=["icu_name", "date"])
  icubam = load_icubam_data(icubam_path)
  dates_in_both = set(icubam.date.unique()) & set(pre_icubam.date.unique())
  pre_icubam = pre_icubam.loc[~pre_icubam.date.isin(dates_in_both)]
  first_icubam_date = icubam.date.min()
  last_pre_icubam_date = pre_icubam.date.max()
  for icu_name in icubam.icu_name.unique():
    first_mask = (icubam.date == first_icubam_date) & (icu_name == icu_name)
    last_mask = \
      (pre_icubam.date == last_pre_icubam_date) & \
      (pre_icubam.icu_name == icu_name)
    for col in CUM_COLUMNS:
      icubam.loc[first_mask, col] -= pre_icubam.loc[last_mask, col]
  return pd.concat([pre_icubam, icubam])


def load_pre_icubam_data(pre_icubam_path, clean=True):
  d = load_data_file(pre_icubam_path)
  d = d.rename(
    columns={
      "Hopital": "icu_name",
      "NbSortieVivant": "n_covid_healed",
      "NbCOVID": "n_covid_occ",
      "NbLitDispo": "n_covid_free",
      "NbDeces": "n_covid_deaths",
      "Date": "date",
    }
  )
  fix_icu_names = {
    "C-Scweitzer": "C-Schweitzer",
    "Bezannes": "C-Bezannes",
    "NHC-Chir": "NHC-ChirC",
  }
  for wrong_name, fixed_name in fix_icu_names.items():
    d.loc[d.icu_name == wrong_name, "icu_name"] = fixed_name
  missing_columns = [
    "n_ncovid_free", "n_covid_transfered", "n_covid_refused", "n_ncodiv_free"
  ]
  for col in missing_columns:
    d[col] = 0
  d = format_data(d)
  return get_clean_daily_values(d) if clean else d


def load_icubam_data(icubam_bedcount_path, clean=True):
  d = load_data_file(icubam_bedcount_path)
  d = format_data(d)
  return get_clean_daily_values(d) if clean else d


def format_data(d):
  d = d.assign(datetime=pd.to_datetime(d.date))
  d = d.assign(date=d.datetime.dt.date)
  icu_name_to_department = load_icu_name_to_department()
  d['department'] = d.icu_name.apply(icu_name_to_department.get)
  d = d[ALL_COLUMNS + ['datetime']]
  return d


def get_clean_daily_values(d):
  dates = sorted(list(d.date.unique()))
  icu_names = sorted(list(d.icu_name.unique()))
  clean_data_points = list()
  prev_valid_values = {i: {c: None for c in CUM_COLUMNS} for i in icu_names}
  per_icu_prev_data_point = dict()
  for date, icu_name in itertools.product(dates, icu_names):
    new_data_point = {"date": date, "icu_name": icu_name}
    new_data_point.update({col: 0 for col in CUM_COLUMNS})
    sd = d.loc[(d.date == date) & (d.icu_name == icu_name)]
    if len(sd) > 0:
      sd = sd.sort_values(by="datetime")
      for col in CUM_COLUMNS:
        if prev_valid_values[icu_name][col] is None:
          new_data_point[col] = sd[col].iloc[-1]
          prev_valid_values[icu_name][col] = {
            'value': sd[col].iloc[-1],
            'date': date,
          }
        else:
          prev_valid_value = prev_valid_values[icu_name][col]['value']
          prev_valid_date = prev_valid_values[icu_name][col]['date']
          n_days_since_prev_valid = (date - prev_valid_date).days
          max_increase = n_days_since_prev_valid * MAX_DAY_INCREASE[col]
          for candidate in reversed(list(sd[col])):
            if candidate >= prev_valid_value:
              increase = candidate - prev_valid_value
              if increase <= max_increase:
                new_data_point[col] = increase
                prev_valid_values[icu_name][col] = {
                  'value': candidate,
                  'date': date,
                }
                break
    clean_data_points.append(new_data_point)
    per_icu_prev_data_point[icu_name] = new_data_point
  return pd.DataFrame(clean_data_points)


def load_data_file(data_path):
  ext = data_path.rsplit(".", 1)[-1]
  if ext == "pickle":
    with open(data_path, "rb") as f:
      d = pickle.load(f)
  elif ext == "h5":
    d = pd.read_hdf(data_path)
  elif ext == "csv":
    d = pd.read_csv(data_path)
  else:
    raise ValueError(f"unknown extension {ext}")
  return d


def load_icu_name_to_department(
  icu_name_to_department_path=DEFAULT_ICU_NAME_TO_DEPARTMENT_PATH
):
  with open(icu_name_to_department_path) as f:
    icu_name_to_department = json.load(f)
  return icu_name_to_department
