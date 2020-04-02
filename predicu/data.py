import itertools
import json
import pickle

import numpy as np
import pandas as pd

DEFAULT_ICUBAM_PATH = 'data/all_bedcounts_2020-04-02_11h05.csv'
DEFAULT_PRE_ICUBAM_PATH = 'data/pre_icubam_data.csv'
DEFAULT_ICU_NAME_TO_DEPARTMENT_PATH = 'data/icu_name_to_department.json'

CUM_COLUMNS = [
  "n_covid_deaths",
  "n_covid_healed",
  "n_covid_transfered",
  "n_covid_refused",
]

NCUM_COLUMNS = [
  "n_covid_free",
  "n_ncovid_free",
  "n_covid_occ",
  "n_ncovid_occ",
]

ALL_COLUMNS = ["icu_name", "date", "department"] + CUM_COLUMNS + NCUM_COLUMNS

MAX_DAY_INCREASE = {
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
  pre_icubam = format_data(pre_icubam)
  icubam = load_icubam_data(icubam_path)
  icubam = icubam.rename(columns={'create_date': 'date'})
  icubam = format_data(icubam)
  dates_in_both = set(icubam.date.unique()) & set(pre_icubam.date.unique())
  pre_icubam = pre_icubam.loc[~pre_icubam.date.isin(dates_in_both)]
  d = pd.concat([pre_icubam, icubam])
  d = clean_data(d)
  d = d.sort_values(by=['date', 'icu_name'])
  return d


def load_pre_icubam_data(pre_icubam_path):
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
    "n_covid_transfered", "n_covid_refused", "n_ncovid_free", "n_ncovid_occ"
  ]
  for col in missing_columns:
    d[col] = 0
  return d


def load_icubam_data(icubam_bedcount_path):
  d = load_data_file(icubam_bedcount_path)
  return d


def format_data(d):
  d['datetime'] = pd.to_datetime(d.date)
  d['date'] = d['datetime'].dt.date
  icu_name_to_department = load_icu_name_to_department()
  d['department'] = d.icu_name.apply(icu_name_to_department.get)
  d = d[ALL_COLUMNS + ['datetime']]
  return d


def clean_data(d):
  d = aggregate_multiple_inputs(d)
  d = fix_noncum_inputs(d)
  d = get_clean_daily_values(d)
  d = d[ALL_COLUMNS]
  return d


def aggregate_multiple_inputs(d):
  agg = {col: 'max' for col in CUM_COLUMNS}
  agg.update({col: 'last' for col in ALL_COLUMNS if col not in CUM_COLUMNS})
  res_dfs = []
  for (icu_name, date), dg in d.groupby(['icu_name', 'date']):
    if len(dg) < 3:
      res_dfs.append(dg)
    else:
      res_dfs.append(
        dg \
        .set_index('datetime') \
        .groupby(pd.Grouper(freq='15Min')) \
        .agg(agg) \
        .dropna() \
        .reset_index()
      )
  return pd.concat(res_dfs)


def fix_noncum_inputs(d, n_noncum_error_threshold=5):
  res_dfs = []
  non_cum_icus = dict()
  for col in CUM_COLUMNS:
    non_cum_icus[col] = {
      icu_name for icu_name in d.icu_name.unique()
      if (
        d.loc[d.icu_name == icu_name] \
        .set_index('datetime') \
        .sort_index()[col] \
        .diff(1) < 0 \
      ).sum() > n_noncum_error_threshold
    }
  for icu_name, dg in d.groupby('icu_name'):
    dg = dg.reset_index().sort_values(by='datetime')
    for col in non_cum_icus:
      if icu_name in non_cum_icus[col]:
        diffs = dg[col].diff(1) / dg.datetime.diff(1).days
        mask = diffs > MAX_DAY_INCREASE[col]
        dg.loc[~mask, col] = dg.loc[~mask, col].cumsum()
    res_dfs.append(dg)
  return pd.concat(res_dfs)


def get_clean_daily_values(d):
  icu_name_to_department = load_icu_name_to_department()
  dates = sorted(list(d.date.unique()))
  icu_names = sorted(list(d.icu_name.unique()))
  clean_data_points = list()
  prev_ncum_vals = dict()
  prev_cum_vals = {i: {c: None for c in CUM_COLUMNS} for i in icu_names}
  per_icu_prev_data_point = dict()
  for date, icu_name in itertools.product(dates, icu_names):
    sd = d.loc[(d.date == date) & (d.icu_name == icu_name)]
    new_data_point = {
      "date": date,
      "icu_name": icu_name,
      'department': icu_name_to_department[icu_name]
    }
    new_data_point.update({col: 0 for col in CUM_COLUMNS})
    new_data_point.update({col: 0 for col in NCUM_COLUMNS})
    if icu_name in prev_ncum_vals:
      new_data_point.update(prev_ncum_vals[icu_name])
    if len(sd) > 0:
      new_ncum_vals = {col: sd[col].iloc[-1] for col in NCUM_COLUMNS}
      new_data_point.update(new_ncum_vals)
      prev_ncum_vals[icu_name] = new_ncum_vals
      sd = sd.sort_values(by="datetime")
      for col in CUM_COLUMNS:
        if prev_cum_vals[icu_name][col] is None:
          new_data_point[col] = sd[col].iloc[-1]
          prev_cum_vals[icu_name][col] = {
            'value': sd[col].iloc[-1],
            'date': date,
          }
        else:
          prev_valid_value = prev_cum_vals[icu_name][col]['value']
          prev_valid_date = prev_cum_vals[icu_name][col]['date']
          n_days_since_prev_valid = (date - prev_valid_date).days
          max_increase = n_days_since_prev_valid * MAX_DAY_INCREASE[col]
          for candidate in reversed(list(sd[col])):
            if candidate >= prev_valid_value:
              increase = candidate - prev_valid_value
              if increase <= max_increase:
                new_data_point[col] = increase
                prev_cum_vals[icu_name][col] = {
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
