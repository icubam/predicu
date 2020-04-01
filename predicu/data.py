import itertools
import pickle

import numpy as np
import pandas as pd

CUM_COLUMNS = [
  "n_covid_free",
  "n_ncovid_free",
  "n_covid_occ",
  "n_covid_deaths",
  "n_covid_healed",
  "n_covid_transfered",
  "n_covid_refused",
]

ALL_COLUMNS = ["icu_name", "date"] + CUM_COLUMNS


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


def load_all_data(icubam_bedcount_path, pre_icubam_path):
  pre_icubam = load_pre_icubam_data(pre_icubam_path)
  fix_same_icu = {
    "CHR-SSPI": "CHR-Thionville",
    "CHR-CCV": "CHR-Thionville",
    "Nancy-NC": "Nancy-RCP"
  }
  for old_icu_name, new_icu_name in fix_same_icu.items():
    pre_icubam.loc[pre_icubam.icu_name == old_icu_name,
                   "icu_name"] = new_icu_name
  pre_icubam = pre_icubam.groupby(["date", "icu_name"]).sum().reset_index()
  pre_icubam = pre_icubam.sort_values(by=["icu_name", "date"])
  icubam = load_icubam_data(icubam_bedcount_path)
  dates_in_both = set(icubam.date.unique()) & set(pre_icubam.date.unique())
  pre_icubam = pre_icubam.loc[~pre_icubam.date.isin(dates_in_both)]
  return pd.concat([pre_icubam, load_icubam_data(icubam_bedcount_path)])


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
  d = d.assign(datetime=pd.to_datetime(d.date))
  d = d.assign(date=d.datetime.dt.date)
  missing_columns = [
    "n_ncovid_free", "n_covid_transfered", "n_covid_refused", "n_ncodiv_free"
  ]
  for col in missing_columns:
    d[col] = 0
  return get_clean_daily_values(d[ALL_COLUMNS + ["datetime"]])


def load_icubam_data(icubam_bedcount_path):
  d = load_data_file(icubam_bedcount_path)
  d = d.assign(datetime=pd.to_datetime(d.date))
  d = d.assign(date=d.datetime.dt.date)
  return get_clean_daily_values(d[ALL_COLUMNS + ["datetime"]])


def get_clean_daily_values(d):
  max_day_increase = {
    "n_covid_free": 20,
    "n_ncovid_free": 20,
    "n_covid_occ": 20,
    "n_covid_deaths": 5,
    "n_covid_healed": 5,
    "n_covid_transfered": 20,
    "n_covid_refused": 200,
  }
  clean_data_points = list()
  per_icu_prev_data_point = dict()
  dates = sorted(list(d.date.unique()))
  icu_names = sorted(list(d.icu_name.unique()))
  for date, icu_name in itertools.product(dates, icu_names):
    new_data_point = {"date": date, "icu_name": icu_name}
    new_data_point.update({col: 0 for col in CUM_COLUMNS})
    sd = d.loc[(d.date == date) & (d.icu_name == icu_name)]
    if len(sd) > 0:
      sd = sd.sort_values(by="datetime")
      prev_data_point = per_icu_prev_data_point.get(icu_name, None)
      if prev_data_point is None:
        new_data_point.update({col: sd[col].iloc[-1] for col in CUM_COLUMNS})
      else:
        for col in CUM_COLUMNS:
          for candidate in reversed(list(sd[col])):
            if candidate >= prev_data_point[col]:
              increase = candidate - prev_data_point[col]
              if increase <= max_day_increase[col]:
                new_data_point[col] = increase
                break
    clean_data_points.append(new_data_point)
    per_icu_prev_data_point[icu_name] = new_data_point
  return pd.DataFrame(clean_data_points)
