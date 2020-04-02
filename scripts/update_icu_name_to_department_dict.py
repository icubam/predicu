import shutil
import json

from predicu.data import DEFAULT_ICUBAM_PATH, load_data_file, load_all_data

d = load_data_file(DEFAULT_ICUBAM_PATH)

icu_name_to_department = dict(
  d[['icu_name', 'icu_dept']].itertuples(name=None, index=False)
)

shutil.copy('data/icu_name_to_department.json',
            'data/icu_name_to_department.json.bkp')

with open('data/icu_name_to_department.json', 'w') as f:
  json.dump(icu_name_to_department, f)

d = load_all_data()
