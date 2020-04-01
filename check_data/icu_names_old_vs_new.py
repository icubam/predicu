from predicu.data import (
  load_all_data, load_icubam_bedcount_data, load_pre_icubam_data
)

pre_icubam_path = 'data/pre_icubam_data.csv'
pre_icubam = load_pre_icubam_data(pre_icubam_path)
icubam_bedcount_path = 'data/bedcount_2020-03-31.pickle'
icubam = load_icubam_bedcount_data(icubam_bedcount_path)
combined = load_all_data(icubam_bedcount_path, pre_icubam_path)

pre_icubam_icu_names = set(pre_icubam.icu_name.unique())
icubam_icu_names = set(icubam.icu_name.unique())
combined_icu_names = set(combined.icu_name.unique())

print('icu_name in pre-icubam but not in icubam')
print('-' * 30)
for icu_name in (pre_icubam_icu_names - icubam_icu_names):
  print(icu_name)
print('-' * 30)
print('icu_name in icubam but not in pre-icubam')
print('-' * 30)
for icu_name in (icubam_icu_names - pre_icubam_icu_names):
  print(icu_name)
print('-' * 30)
print('icu_name in pre-icubam but not in combined')
print('-' * 30)
for icu_name in (pre_icubam_icu_names - combined_icu_names):
  print(icu_name)
print('-' * 30)
print('icu_name in icubam but not in combined')
print('-' * 30)
for icu_name in (icubam_icu_names - combined_icu_names):
  print(icu_name)
