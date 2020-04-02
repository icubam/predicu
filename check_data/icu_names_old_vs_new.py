from predicu.data import (
  DEFAULT_ICUBAM_PATH, DEFAULT_PRE_ICUBAM_PATH, load_all_data,
  load_icubam_data, load_pre_icubam_data
)

pre_icubam_path = DEFAULT_PRE_ICUBAM_PATH
pre_icubam = load_pre_icubam_data(pre_icubam_path)
icubam_bedcount_path = DEFAULT_ICUBAM_PATH
icubam = load_icubam_data(icubam_bedcount_path)
combined = load_all_data(icubam_bedcount_path, pre_icubam_path)

pre_icubam_icu_names = set(pre_icubam.icu_name.unique())
icubam_icu_names = set(icubam.icu_name.unique())
combined_icu_names = set(combined.icu_name.unique())

print('nb of ICUs in pre-ICUBAM data:', len(pre_icubam_icu_names))
print('nb of ICUs in ICUBAM data:', len(icubam_icu_names))
print('nb of ICUs in combined data:', len(combined_icu_names))

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
